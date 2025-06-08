"""
Unit tests for configuration management.
"""

import unittest
import tempfile
import os
import json
from src.config import ModelConfig, ValidationConfig, SystemConfig, load_config, save_config


class TestModelConfig(unittest.TestCase):
    """Test cases for ModelConfig class"""
    
    def test_default_config(self):
        """Test default model configuration"""
        config = ModelConfig()
        
        # Check that conservative defaults are set
        self.assertEqual(config.cv_folds, 5)
        self.assertEqual(config.test_size, 0.2)
        self.assertEqual(config.random_state, 42)
        self.assertLessEqual(config.max_depth, 6)  # Should be conservative
        self.assertGreaterEqual(config.min_samples_split, 10)  # Should prevent overfitting
        self.assertGreaterEqual(config.min_samples_leaf, 5)  # Should prevent overfitting
        self.assertFalse(config.use_polynomial_features)  # Should be disabled by default
        self.assertTrue(config.apply_regularization)
    
    def test_custom_config(self):
        """Test custom model configuration"""
        config = ModelConfig(
            cv_folds=10,
            max_depth=3,
            min_samples_split=30,
            use_polynomial_features=True
        )
        
        self.assertEqual(config.cv_folds, 10)
        self.assertEqual(config.max_depth, 3)
        self.assertEqual(config.min_samples_split, 30)
        self.assertTrue(config.use_polynomial_features)


class TestValidationConfig(unittest.TestCase):
    """Test cases for ValidationConfig class"""
    
    def test_default_config(self):
        """Test default validation configuration"""
        config = ValidationConfig()
        
        self.assertEqual(config.max_acceptable_mae, 100.0)
        self.assertEqual(config.exact_match_tolerance, 0.01)
        self.assertEqual(config.close_match_tolerance, 1.00)
        self.assertGreater(config.max_train_test_gap, 0)
        self.assertGreater(config.min_cv_score, 0)
    
    def test_custom_config(self):
        """Test custom validation configuration"""
        config = ValidationConfig(
            max_acceptable_mae=50.0,
            exact_match_tolerance=0.005,
            max_train_test_gap=25.0
        )
        
        self.assertEqual(config.max_acceptable_mae, 50.0)
        self.assertEqual(config.exact_match_tolerance, 0.005)
        self.assertEqual(config.max_train_test_gap, 25.0)


class TestSystemConfig(unittest.TestCase):
    """Test cases for SystemConfig class"""
    
    def test_default_config(self):
        """Test default system configuration"""
        config = SystemConfig(
            model=ModelConfig(),
            validation=ValidationConfig()
        )
        
        self.assertIsInstance(config.model, ModelConfig)
        self.assertIsInstance(config.validation, ValidationConfig)
        self.assertEqual(config.public_cases_path, "public_cases.json")
        self.assertEqual(config.private_cases_path, "private_cases.json")
        self.assertEqual(config.log_level, "INFO")
        self.assertGreater(config.max_execution_time, 0)
        self.assertTrue(config.enable_caching)


class TestConfigLoadSave(unittest.TestCase):
    """Test cases for configuration loading and saving"""
    
    def test_load_default_config(self):
        """Test loading default configuration when no file exists"""
        config = load_config("nonexistent_file.json")
        
        self.assertIsInstance(config, SystemConfig)
        self.assertIsInstance(config.model, ModelConfig)
        self.assertIsInstance(config.validation, ValidationConfig)
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        # Create a custom config
        original_config = SystemConfig(
            model=ModelConfig(max_depth=3, cv_folds=10),
            validation=ValidationConfig(max_acceptable_mae=75.0),
            log_level="DEBUG",
            max_execution_time=10.0
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            save_config(original_config, temp_path)
            
            # Verify file was created and contains JSON
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                config_data = json.load(f)
            
            self.assertIn('model', config_data)
            self.assertIn('validation', config_data)
            self.assertEqual(config_data['log_level'], 'DEBUG')
            self.assertEqual(config_data['max_execution_time'], 10.0)
            
            # Load the config back
            loaded_config = load_config(temp_path)
            
            # Verify values were preserved
            self.assertEqual(loaded_config.model.max_depth, 3)
            self.assertEqual(loaded_config.model.cv_folds, 10)
            self.assertEqual(loaded_config.validation.max_acceptable_mae, 75.0)
            self.assertEqual(loaded_config.log_level, "DEBUG")
            self.assertEqual(loaded_config.max_execution_time, 10.0)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_partial_config(self):
        """Test loading configuration with only some fields specified"""
        # Create a partial config file
        partial_config = {
            'model': {
                'max_depth': 2
            },
            'log_level': 'WARNING'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(partial_config, f)
            temp_path = f.name
        
        try:
            loaded_config = load_config(temp_path)
            
            # Specified values should be loaded
            self.assertEqual(loaded_config.model.max_depth, 2)
            self.assertEqual(loaded_config.log_level, 'WARNING')
            
            # Unspecified values should use defaults
            self.assertEqual(loaded_config.model.cv_folds, 5)  # Default value
            self.assertEqual(loaded_config.validation.max_acceptable_mae, 100.0)  # Default value
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_invalid_json(self):
        """Test handling of invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            temp_path = f.name
        
        try:
            # Should raise an exception for invalid JSON
            with self.assertRaises(json.JSONDecodeError):
                load_config(temp_path)
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_conservative_defaults(self):
        """Test that default configuration is conservative to avoid overfitting"""
        config = load_config()
        
        # Model should have conservative settings
        self.assertLessEqual(config.model.max_depth, 6)
        self.assertGreaterEqual(config.model.min_samples_split, 10)
        self.assertGreaterEqual(config.model.min_samples_leaf, 5)
        self.assertFalse(config.model.use_polynomial_features)
        self.assertTrue(config.model.apply_regularization)
        
        # Validation should have reasonable thresholds
        self.assertGreater(config.validation.max_train_test_gap, 0)
        self.assertGreater(config.validation.min_cv_score, 0)


if __name__ == '__main__':
    unittest.main()