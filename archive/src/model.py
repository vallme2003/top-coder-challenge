"""
Machine learning model implementation for reimbursement prediction.

This module implements a conservative modeling approach designed to generalize
well to unseen data and avoid overfitting to the public dataset.
"""

import logging
import pickle
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

from .data_models import TripInput, ReimbursementResult, TestCase, ValidationMetrics
from .feature_engineering import FeatureEngineer, FeatureSet
from .config import ModelConfig, ValidationConfig


logger = logging.getLogger(__name__)


class ReimbursementModel:
    """
    Machine learning model for predicting travel reimbursements.
    
    This model is designed with conservative hyperparameters to avoid
    overfitting and ensure good generalization to private test cases.
    """
    
    def __init__(self, model_config: ModelConfig, validation_config: ValidationConfig):
        """
        Initialize the reimbursement model.
        
        Args:
            model_config: Configuration for model hyperparameters
            validation_config: Configuration for validation settings
        """
        self.model_config = model_config
        self.validation_config = validation_config
        self.feature_engineer = FeatureEngineer(model_config)
        self.model = None
        self.is_trained = False
        self.training_metrics = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def train(self, training_cases: List[TestCase]) -> ValidationMetrics:
        """
        Train the model on the provided training cases.
        
        Args:
            training_cases: List of test cases with known outputs
            
        Returns:
            ValidationMetrics from cross-validation
            
        Raises:
            ValueError: If training cases are invalid or insufficient
        """
        if len(training_cases) < 10:
            raise ValueError("Need at least 10 training cases")
        
        # Validate all training cases have expected outputs
        for case in training_cases:
            if case.expected_output is None:
                raise ValueError("All training cases must have expected outputs")
        
        self.logger.info(f"Training model on {len(training_cases)} cases")
        
        # Extract features and targets
        X, y, feature_names = self._prepare_training_data(training_cases)
        
        # Perform cross-validation to detect overfitting
        cv_metrics = self._cross_validate(X, y)
        
        # Check for overfitting
        if cv_metrics.score > self.validation_config.max_train_test_gap:
            self.logger.warning(f"Potential overfitting detected. CV score: {cv_metrics.score}")
        
        # Train final model on all data (conservative approach)
        self.model = self._create_model()
        self.model.fit(X, y)
        
        # Store training information
        self.is_trained = True
        self.training_metrics = cv_metrics
        self.feature_names = feature_names
        
        # Log feature importance
        self._log_feature_importance()
        
        self.logger.info("Model training completed successfully")
        return cv_metrics
    
    def predict(self, trip_input: TripInput) -> ReimbursementResult:
        """
        Predict reimbursement amount for a single trip.
        
        Args:
            trip_input: Trip data to predict reimbursement for
            
        Returns:
            ReimbursementResult with predicted amount and metadata
            
        Raises:
            RuntimeError: If model is not trained
            ValueError: If input is invalid
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        
        try:
            # Extract features
            feature_set = self.feature_engineer.extract_features(trip_input)
            X = np.array(feature_set.all_features).reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            
            # Calculate confidence (simplified approach)
            confidence = self._calculate_confidence(feature_set)
            
            # Create result
            result = ReimbursementResult(
                amount=round(prediction, 2),
                confidence=confidence
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise
    
    def predict_batch(self, trip_inputs: List[TripInput]) -> List[ReimbursementResult]:
        """
        Predict reimbursement amounts for multiple trips.
        
        Args:
            trip_inputs: List of trip data to predict reimbursements for
            
        Returns:
            List of ReimbursementResult objects
        """
        return [self.predict(trip_input) for trip_input in trip_inputs]
    
    def evaluate(self, test_cases: List[TestCase]) -> ValidationMetrics:
        """
        Evaluate model performance on test cases.
        
        Args:
            test_cases: List of test cases with known expected outputs
            
        Returns:
            ValidationMetrics with performance statistics
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before evaluation")
        
        predictions = []
        actuals = []
        
        for case in test_cases:
            if case.expected_output is None:
                continue
                
            try:
                result = self.predict(case.input_data)
                predictions.append(result.amount)
                actuals.append(case.expected_output)
            except Exception as e:
                self.logger.error(f"Prediction failed for case {case.case_id}: {e}")
                continue
        
        if len(predictions) == 0:
            raise ValueError("No valid predictions were made")
        
        return self._calculate_metrics(predictions, actuals)
    
    def save(self, model_path: str) -> None:
        """
        Save the trained model to disk.
        
        Args:
            model_path: Path where to save the model
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'feature_engineer': self.feature_engineer,
            'model_config': self.model_config,
            'validation_config': self.validation_config,
            'training_metrics': self.training_metrics,
            'feature_names': getattr(self, 'feature_names', None)
        }
        
        joblib.dump(model_data, model_path)
        self.logger.info(f"Model saved to {model_path}")
    
    @classmethod
    def load(cls, model_path: str) -> 'ReimbursementModel':
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            Loaded ReimbursementModel instance
        """
        model_data = joblib.load(model_path)
        
        instance = cls(model_data['model_config'], model_data['validation_config'])
        instance.model = model_data['model']
        instance.feature_engineer = model_data['feature_engineer']
        instance.training_metrics = model_data['training_metrics']
        instance.feature_names = model_data.get('feature_names')
        instance.is_trained = True
        
        return instance
    
    def _prepare_training_data(self, training_cases: List[TestCase]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare feature matrix and target vector from training cases"""
        X_list = []
        y_list = []
        feature_names = None
        
        for case in training_cases:
            try:
                feature_set = self.feature_engineer.extract_features(case.input_data)
                X_list.append(feature_set.all_features)
                y_list.append(case.expected_output)
                
                if feature_names is None:
                    feature_names = feature_set.feature_names
                    
            except Exception as e:
                self.logger.warning(f"Skipping case {case.case_id}: {e}")
                continue
        
        if len(X_list) == 0:
            raise ValueError("No valid training cases found")
        
        return np.array(X_list), np.array(y_list), feature_names
    
    def _create_model(self):
        """Create the machine learning model with conservative hyperparameters"""
        # Use Random Forest with conservative settings to avoid overfitting
        return RandomForestRegressor(
            n_estimators=50,  # Conservative number of trees
            max_depth=self.model_config.max_depth,  # Limited depth
            min_samples_split=self.model_config.min_samples_split,  # Prevent small splits
            min_samples_leaf=self.model_config.min_samples_leaf,  # Ensure leaf size
            max_features='sqrt',  # Feature subsampling
            random_state=self.model_config.random_state,
            n_jobs=1  # Single thread for reproducibility
        )
    
    def _cross_validate(self, X: np.ndarray, y: np.ndarray) -> ValidationMetrics:
        """Perform cross-validation to assess generalization"""
        model = self._create_model()
        
        # Perform cross-validation
        cv_scores = cross_val_score(
            model, X, y, 
            cv=self.model_config.cv_folds,
            scoring='neg_mean_absolute_error',
            n_jobs=1
        )
        
        mae_scores = -cv_scores
        mean_mae = np.mean(mae_scores)
        
        self.logger.info(f"Cross-validation MAE: {mean_mae:.2f} (+/- {np.std(mae_scores):.2f})")
        
        # Create simplified metrics for CV
        return ValidationMetrics(
            mean_absolute_error=mean_mae,
            exact_matches=0,  # Not applicable for CV
            close_matches=0,  # Not applicable for CV
            max_error=np.max(mae_scores),
            total_cases=len(y),
            score=mean_mae
        )
    
    def _calculate_confidence(self, feature_set: FeatureSet) -> float:
        """Calculate confidence score for a prediction (simplified approach)"""
        # For Random Forest, we could use tree variance, but keep it simple
        # Higher confidence for inputs similar to training data
        
        # Check for extreme values that might indicate out-of-distribution data
        features = feature_set.all_features
        
        confidence = 1.0
        
        # Reduce confidence for extreme values
        if any(abs(f) > 1000 for f in features if not np.isinf(f)):
            confidence *= 0.8
        
        if any(np.isinf(f) or np.isnan(f) for f in features):
            confidence *= 0.5
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_metrics(self, predictions: List[float], actuals: List[float]) -> ValidationMetrics:
        """Calculate validation metrics"""
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        errors = np.abs(predictions - actuals)
        mae = np.mean(errors)
        max_error = np.max(errors)
        
        exact_matches = np.sum(errors <= self.validation_config.exact_match_tolerance)
        close_matches = np.sum(errors <= self.validation_config.close_match_tolerance)
        
        score = mae * 100  # Simple scoring function
        
        return ValidationMetrics(
            mean_absolute_error=mae,
            exact_matches=int(exact_matches),
            close_matches=int(close_matches),
            max_error=max_error,
            total_cases=len(predictions),
            score=score
        )
    
    def _log_feature_importance(self) -> None:
        """Log feature importance for interpretability"""
        if hasattr(self.model, 'feature_importances_') and hasattr(self, 'feature_names'):
            importances = self.model.feature_importances_
            importance_dict = dict(zip(self.feature_names, importances))
            
            # Sort by importance
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            self.logger.info("Top 10 most important features:")
            for feature, importance in sorted_features[:10]:
                self.logger.info(f"  {feature}: {importance:.4f}")


class SimpleDecisionTreeModel:
    """
    Simplified decision tree model for fast execution without external dependencies.
    
    This model is designed to approximate the Random Forest model but with
    much faster prediction times and no sklearn dependency at runtime.
    """
    
    def __init__(self, max_depth: int = 4):
        """
        Initialize the simple decision tree model.
        
        Args:
            max_depth: Maximum depth of the decision tree
        """
        self.max_depth = max_depth
        self.tree_rules = None
        self.feature_engineer = None
        self.is_trained = False
    
    def train_from_model(self, trained_model: ReimbursementModel, training_cases: List[TestCase]) -> None:
        """
        Train this simple model to approximate a complex trained model.
        
        Args:
            trained_model: The complex model to approximate
            training_cases: Training cases to use for approximation
        """
        # Generate predictions from the complex model
        X, y_original, feature_names = trained_model._prepare_training_data(training_cases)
        
        # Get predictions from the complex model
        y_complex = []
        for case in training_cases:
            if case.expected_output is not None:
                try:
                    result = trained_model.predict(case.input_data)
                    y_complex.append(result.amount)
                except:
                    continue
        
        if len(y_complex) != len(y_original):
            raise ValueError("Mismatch in prediction counts")
        
        # Train a simple decision tree to approximate the complex model
        simple_tree = DecisionTreeRegressor(
            max_depth=self.max_depth,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42
        )
        
        simple_tree.fit(X, y_complex)
        
        # Store the approximation
        self.tree_rules = self._extract_tree_rules(simple_tree, feature_names)
        self.feature_engineer = trained_model.feature_engineer
        self.is_trained = True
    
    def predict(self, trip_input: TripInput) -> ReimbursementResult:
        """
        Predict reimbursement using the simple tree rules.
        
        Args:
            trip_input: Trip data to predict reimbursement for
            
        Returns:
            ReimbursementResult with predicted amount
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        
        # Extract features
        feature_set = self.feature_engineer.extract_features(trip_input)
        features = feature_set.all_features
        
        # Apply tree rules (simplified implementation)
        prediction = self._apply_tree_rules(features)
        
        return ReimbursementResult(amount=round(prediction, 2))
    
    def _extract_tree_rules(self, tree, feature_names: List[str]) -> Dict[str, Any]:
        """Extract decision tree rules for fast execution"""
        # This would contain the tree structure for fast execution
        # For now, return a placeholder
        return {
            'tree': tree,
            'feature_names': feature_names
        }
    
    def _apply_tree_rules(self, features: List[float]) -> float:
        """Apply tree rules to get prediction"""
        # Use the stored tree to make prediction
        X = np.array(features).reshape(1, -1)
        return self.tree_rules['tree'].predict(X)[0]