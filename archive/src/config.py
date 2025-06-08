"""
Configuration management for the reimbursement system.

This module handles all configuration parameters to ensure consistent behavior
across different components and easy tuning without code changes.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for model parameters"""
    # Cross-validation settings
    cv_folds: int = 5
    test_size: float = 0.2
    random_state: int = 42
    
    # Model hyperparameters (conservative to avoid overfitting)
    max_depth: int = 4  # Reduced from 6 to prevent overfitting
    min_samples_split: int = 20  # Increased to prevent overfitting
    min_samples_leaf: int = 10  # Increased to prevent overfitting
    
    # Feature engineering
    use_polynomial_features: bool = False  # Disabled to reduce complexity
    max_polynomial_degree: int = 2
    
    # Regularization
    apply_regularization: bool = True
    regularization_strength: float = 0.1


@dataclass
class ValidationConfig:
    """Configuration for validation and testing"""
    # Error thresholds
    max_acceptable_mae: float = 100.0
    exact_match_tolerance: float = 0.01
    close_match_tolerance: float = 1.00
    
    # Overfitting detection
    max_train_test_gap: float = 50.0  # Max acceptable gap between train/test MAE
    
    # Cross-validation requirements
    min_cv_score: float = 0.8  # Minimum acceptable CV R-squared


@dataclass
class SystemConfig:
    """Main system configuration"""
    model: ModelConfig
    validation: ValidationConfig
    
    # File paths
    public_cases_path: str = "public_cases.json"
    private_cases_path: str = "private_cases.json"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance
    max_execution_time: float = 5.0  # seconds per test case
    enable_caching: bool = True


def load_config(config_path: Optional[str] = None) -> SystemConfig:
    """
    Load system configuration from file or use defaults.
    
    Args:
        config_path: Optional path to JSON configuration file
        
    Returns:
        SystemConfig object with loaded or default configuration
    """
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        
        model_config = ModelConfig(**config_dict.get('model', {}))
        validation_config = ValidationConfig(**config_dict.get('validation', {}))
        
        system_config = SystemConfig(
            model=model_config,
            validation=validation_config,
            **{k: v for k, v in config_dict.items() if k not in ['model', 'validation']}
        )
    else:
        # Use conservative defaults to avoid overfitting
        system_config = SystemConfig(
            model=ModelConfig(),
            validation=ValidationConfig()
        )
    
    return system_config


def save_config(config: SystemConfig, config_path: str) -> None:
    """
    Save configuration to JSON file.
    
    Args:
        config: SystemConfig object to save
        config_path: Path where to save the configuration
    """
    config_dict = {
        'model': config.model.__dict__,
        'validation': config.validation.__dict__,
        'public_cases_path': config.public_cases_path,
        'private_cases_path': config.private_cases_path,
        'log_level': config.log_level,
        'log_format': config.log_format,
        'max_execution_time': config.max_execution_time,
        'enable_caching': config.enable_caching
    }
    
    with open(config_path, 'w') as f:
        json.dump(config_dict, f, indent=2)