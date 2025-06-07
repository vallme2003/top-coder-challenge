"""
Main training and evaluation script for the reimbursement system.

This script demonstrates the complete workflow from data loading through
model training and evaluation, with emphasis on avoiding overfitting.
"""

import json
import logging
import sys
import os
from typing import List, Tuple
from pathlib import Path

from .config import load_config, SystemConfig
from .data_models import TripInput, TestCase, ValidationMetrics
from .model import ReimbursementModel, SimpleDecisionTreeModel
from .feature_engineering import FeatureEngineer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_test_cases(file_path: str, include_outputs: bool = True) -> List[TestCase]:
    """
    Load test cases from JSON file.
    
    Args:
        file_path: Path to the JSON file containing test cases
        include_outputs: Whether to expect output values in the file
        
    Returns:
        List of TestCase objects
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test case file not found: {file_path}")
    
    logger.info(f"Loading test cases from {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    test_cases = []
    for i, case in enumerate(data):
        try:
            # Extract input data
            input_data = case['input']
            trip_input = TripInput(
                trip_duration_days=input_data['trip_duration_days'],
                miles_traveled=input_data['miles_traveled'],
                total_receipts_amount=input_data['total_receipts_amount']
            )
            
            # Extract expected output if available
            expected_output = case.get('expected_output') if include_outputs else None
            
            test_case = TestCase(
                input_data=trip_input,
                expected_output=expected_output,
                case_id=f"case_{i:04d}"
            )
            
            test_cases.append(test_case)
            
        except Exception as e:
            logger.warning(f"Skipping invalid test case {i}: {e}")
            continue
    
    logger.info(f"Loaded {len(test_cases)} valid test cases")
    return test_cases


def create_holdout_split(test_cases: List[TestCase], holdout_fraction: float = 0.2) -> Tuple[List[TestCase], List[TestCase]]:
    """
    Split test cases into training and holdout sets.
    
    Args:
        test_cases: List of all test cases
        holdout_fraction: Fraction to reserve for holdout validation
        
    Returns:
        Tuple of (training_cases, holdout_cases)
    """
    # Use a fixed seed for reproducible splits
    import random
    random.seed(42)
    
    # Shuffle the cases
    shuffled_cases = test_cases.copy()
    random.shuffle(shuffled_cases)
    
    # Split
    holdout_size = int(len(shuffled_cases) * holdout_fraction)
    holdout_cases = shuffled_cases[:holdout_size]
    training_cases = shuffled_cases[holdout_size:]
    
    logger.info(f"Created split: {len(training_cases)} training, {len(holdout_cases)} holdout")
    return training_cases, holdout_cases


def train_and_evaluate_model(config: SystemConfig, training_cases: List[TestCase], 
                           holdout_cases: List[TestCase]) -> Tuple[ReimbursementModel, ValidationMetrics, ValidationMetrics]:
    """
    Train and evaluate the reimbursement model.
    
    Args:
        config: System configuration
        training_cases: Cases to train on
        holdout_cases: Cases to evaluate on (unseen during training)
        
    Returns:
        Tuple of (trained_model, training_metrics, holdout_metrics)
    """
    logger.info("Training reimbursement model")
    
    # Create and train model
    model = ReimbursementModel(config.model, config.validation)
    training_metrics = model.train(training_cases)
    
    # Evaluate on training data (should be better than holdout)
    logger.info("Evaluating on training data")
    training_eval_metrics = model.evaluate(training_cases)
    
    # Evaluate on holdout data (true generalization test)
    logger.info("Evaluating on holdout data")
    holdout_metrics = model.evaluate(holdout_cases)
    
    # Check for overfitting
    train_mae = training_eval_metrics.mean_absolute_error
    holdout_mae = holdout_metrics.mean_absolute_error
    overfitting_gap = train_mae - holdout_mae
    
    logger.info(f"Training MAE: ${train_mae:.2f}")
    logger.info(f"Holdout MAE: ${holdout_mae:.2f}")
    logger.info(f"Overfitting gap: ${overfitting_gap:.2f}")
    
    if abs(overfitting_gap) > config.validation.max_train_test_gap:
        logger.warning(f"Significant overfitting detected! Gap: ${overfitting_gap:.2f}")
    else:
        logger.info("Overfitting check passed")
    
    return model, training_metrics, holdout_metrics


def create_production_model(trained_model: ReimbursementModel, 
                          training_cases: List[TestCase]) -> SimpleDecisionTreeModel:
    """
    Create a simplified production model for fast execution.
    
    Args:
        trained_model: The complex trained model to approximate
        training_cases: Training data for the approximation
        
    Returns:
        SimpleDecisionTreeModel ready for production use
    """
    logger.info("Creating simplified production model")
    
    simple_model = SimpleDecisionTreeModel(max_depth=4)
    simple_model.train_from_model(trained_model, training_cases)
    
    logger.info("Production model created successfully")
    return simple_model


def generate_predictions(model: ReimbursementModel, test_cases: List[TestCase], 
                        output_path: str) -> None:
    """
    Generate predictions for test cases and save to file.
    
    Args:
        model: Trained model to use for predictions
        test_cases: Test cases to predict
        output_path: Path to save predictions
    """
    logger.info(f"Generating predictions for {len(test_cases)} cases")
    
    predictions = []
    for case in test_cases:
        try:
            result = model.predict(case.input_data)
            predictions.append(str(result.amount))
        except Exception as e:
            logger.error(f"Prediction failed for case {case.case_id}: {e}")
            predictions.append("ERROR")
    
    # Save predictions
    with open(output_path, 'w') as f:
        for prediction in predictions:
            f.write(f"{prediction}\n")
    
    logger.info(f"Predictions saved to {output_path}")


def main():
    """Main execution function"""
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Load public cases (with expected outputs)
        public_cases = load_test_cases(config.public_cases_path, include_outputs=True)
        
        # Create train/holdout split to validate generalization
        training_cases, holdout_cases = create_holdout_split(public_cases, holdout_fraction=0.2)
        
        # Train and evaluate model
        model, training_metrics, holdout_metrics = train_and_evaluate_model(
            config, training_cases, holdout_cases
        )
        
        # Print results
        print("\n" + "="*50)
        print("TRAINING RESULTS")
        print("="*50)
        print(f"Cross-validation MAE: ${training_metrics.mean_absolute_error:.2f}")
        print(f"Holdout MAE: ${holdout_metrics.mean_absolute_error:.2f}")
        print(f"Holdout Score: {holdout_metrics.score:.2f}")
        print(f"Close matches on holdout: {holdout_metrics.close_match_rate:.1f}%")
        
        # Save trained model
        model.save("trained_model.pkl")
        logger.info("Model saved to trained_model.pkl")
        
        # Create production model
        simple_model = create_production_model(model, training_cases)
        
        # Load private cases (no expected outputs)
        try:
            private_cases = load_test_cases(config.private_cases_path, include_outputs=False)
            generate_predictions(model, private_cases, "private_results.txt")
        except FileNotFoundError:
            logger.warning("Private cases file not found, skipping prediction generation")
        
        print(f"\n✅ Training completed successfully!")
        print(f"Holdout validation MAE: ${holdout_metrics.mean_absolute_error:.2f}")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        print(f"❌ Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()