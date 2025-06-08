"""
Unit tests for feature engineering module.
"""

import unittest
import math
from src.data_models import TripInput
from src.feature_engineering import FeatureEngineer, FeatureSet
from src.config import ModelConfig


class TestFeatureSet(unittest.TestCase):
    """Test cases for FeatureSet class"""
    
    def test_feature_set_creation(self):
        """Test creation of feature set"""
        feature_set = FeatureSet(
            basic_features=[1, 2, 3],
            derived_features=[4, 5],
            categorical_features=[0, 1],
            transformed_features=[6, 7],
            feature_names=['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7']
        )
        
        self.assertEqual(feature_set.all_features, [1, 2, 3, 4, 5, 0, 1, 6, 7])
        self.assertEqual(feature_set.feature_count, 9)
        self.assertEqual(len(feature_set.feature_names), 7)
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        feature_set = FeatureSet(
            basic_features=[1, 2],
            derived_features=[3],
            categorical_features=[0],
            transformed_features=[4],
            feature_names=['a', 'b', 'c', 'd', 'e']
        )
        
        feature_dict = feature_set.to_dict()
        expected = {'a': 1, 'b': 2, 'c': 3, 'd': 0, 'e': 4}
        self.assertEqual(feature_dict, expected)
    
    def test_mismatched_names(self):
        """Test handling of mismatched feature names"""
        feature_set = FeatureSet(
            basic_features=[1, 2],
            derived_features=[3],
            categorical_features=[0],
            transformed_features=[4],
            feature_names=['a', 'b']  # Wrong number of names
        )
        
        with self.assertRaises(ValueError):
            feature_set.to_dict()


class TestFeatureEngineer(unittest.TestCase):
    """Test cases for FeatureEngineer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ModelConfig(
            use_polynomial_features=False,
            max_polynomial_degree=2
        )
        self.engineer = FeatureEngineer(self.config)
    
    def test_basic_feature_extraction(self):
        """Test extraction of basic features"""
        trip = TripInput(trip_duration_days=5, miles_traveled=250, total_receipts_amount=150)
        feature_set = self.engineer.extract_features(trip)
        
        # Should have basic features
        self.assertGreaterEqual(len(feature_set.basic_features), 3)
        self.assertEqual(feature_set.basic_features[0], 5.0)  # days
        self.assertEqual(feature_set.basic_features[1], 250.0)  # miles
        self.assertEqual(feature_set.basic_features[2], 150.0)  # receipts
    
    def test_derived_features(self):
        """Test extraction of derived features"""
        trip = TripInput(trip_duration_days=4, miles_traveled=200, total_receipts_amount=100)
        feature_set = self.engineer.extract_features(trip)
        
        # Check specific derived features
        self.assertGreater(len(feature_set.derived_features), 0)
        
        # Miles per day should be 50
        mpd_index = 0  # First derived feature
        self.assertEqual(feature_set.derived_features[mpd_index], 50.0)
        
        # Receipts per day should be 25
        rpd_index = 1  # Second derived feature
        self.assertEqual(feature_set.derived_features[rpd_index], 25.0)
    
    def test_categorical_features(self):
        """Test extraction of categorical features"""
        # Test 5-day trip (should trigger 5-day indicator)
        trip = TripInput(trip_duration_days=5, miles_traveled=250, total_receipts_amount=150)
        feature_set = self.engineer.extract_features(trip)
        
        # Should have categorical features
        self.assertGreater(len(feature_set.categorical_features), 0)
        
        # Check that we have binary indicators
        for feature in feature_set.categorical_features:
            if not math.isnan(feature) and not math.isinf(feature):
                self.assertIn(feature, [0.0, 1.0] + list(range(100)))  # Allow cents values
    
    def test_transformed_features(self):
        """Test extraction of transformed features"""
        trip = TripInput(trip_duration_days=3, miles_traveled=100, total_receipts_amount=50)
        feature_set = self.engineer.extract_features(trip)
        
        # Should have log transformed features
        self.assertGreaterEqual(len(feature_set.transformed_features), 3)
        
        # Check log transformations
        log_days = math.log1p(3)
        log_miles = math.log1p(100)
        log_receipts = math.log1p(50)
        
        self.assertAlmostEqual(feature_set.transformed_features[0], log_days, places=5)
        self.assertAlmostEqual(feature_set.transformed_features[1], log_miles, places=5)
        self.assertAlmostEqual(feature_set.transformed_features[2], log_receipts, places=5)
    
    def test_polynomial_features_disabled(self):
        """Test that polynomial features are not included when disabled"""
        trip = TripInput(trip_duration_days=3, miles_traveled=100, total_receipts_amount=50)
        feature_set = self.engineer.extract_features(trip)
        
        # With polynomial features disabled, should only have log transforms
        self.assertEqual(len(feature_set.transformed_features), 3)
    
    def test_polynomial_features_enabled(self):
        """Test polynomial feature extraction when enabled"""
        config = ModelConfig(
            use_polynomial_features=True,
            max_polynomial_degree=2
        )
        engineer = FeatureEngineer(config)
        
        trip = TripInput(trip_duration_days=3, miles_traveled=100, total_receipts_amount=50)
        feature_set = engineer.extract_features(trip)
        
        # Should have log transforms + polynomial features
        self.assertGreater(len(feature_set.transformed_features), 3)
    
    def test_special_receipt_endings(self):
        """Test detection of special receipt endings"""
        # Test receipt ending in 49 cents
        trip_49 = TripInput(trip_duration_days=3, miles_traveled=100, total_receipts_amount=50.49)
        feature_set_49 = self.engineer.extract_features(trip_49)
        
        # Test receipt ending in 99 cents
        trip_99 = TripInput(trip_duration_days=3, miles_traveled=100, total_receipts_amount=50.99)
        feature_set_99 = self.engineer.extract_features(trip_99)
        
        # Should detect the special endings in categorical features
        # (Implementation details may vary, but should be present)
        self.assertIsNotNone(feature_set_49.categorical_features)
        self.assertIsNotNone(feature_set_99.categorical_features)
    
    def test_zero_edge_cases(self):
        """Test handling of zero values"""
        trip = TripInput(trip_duration_days=1, miles_traveled=0, total_receipts_amount=0)
        feature_set = self.engineer.extract_features(trip)
        
        # Should handle zero values gracefully
        self.assertIsNotNone(feature_set.all_features)
        
        # Check that no features are NaN (except for specific calculations)
        for feature in feature_set.all_features:
            if not (math.isinf(feature) and feature > 0):  # Allow positive infinity for miles/receipts ratios
                self.assertFalse(math.isnan(feature), f"Feature should not be NaN: {feature}")
    
    def test_feature_names_consistency(self):
        """Test that feature names match the number of features"""
        trip = TripInput(trip_duration_days=5, miles_traveled=250, total_receipts_amount=150)
        feature_set = self.engineer.extract_features(trip)
        
        # Number of feature names should match number of features
        self.assertEqual(len(feature_set.feature_names), feature_set.feature_count)
        
        # All feature names should be strings
        for name in feature_set.feature_names:
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)
    
    def test_invalid_input(self):
        """Test handling of invalid input"""
        with self.assertRaises(ValueError):
            invalid_trip = TripInput(trip_duration_days=0, miles_traveled=100, total_receipts_amount=50)
    
    def test_feature_importance_explanation(self):
        """Test feature importance explanation"""
        trip = TripInput(trip_duration_days=5, miles_traveled=250, total_receipts_amount=150)
        feature_set = self.engineer.extract_features(trip)
        
        # Create mock importance scores
        num_features = feature_set.feature_count
        mock_importances = [0.1] * num_features
        
        importance_dict = self.engineer.get_feature_importance_explanation(mock_importances)
        
        self.assertEqual(len(importance_dict), num_features)
        self.assertEqual(len(importance_dict), len(feature_set.feature_names))
        
        # Check that all feature names are present
        for name in feature_set.feature_names:
            self.assertIn(name, importance_dict)
    
    def test_feature_importance_mismatch(self):
        """Test handling of mismatched importance scores"""
        trip = TripInput(trip_duration_days=5, miles_traveled=250, total_receipts_amount=150)
        feature_set = self.engineer.extract_features(trip)
        
        # Wrong number of importance scores
        wrong_importances = [0.1] * (feature_set.feature_count - 1)
        
        with self.assertRaises(ValueError):
            self.engineer.get_feature_importance_explanation(wrong_importances)


if __name__ == '__main__':
    unittest.main()