"""
Unit tests for data models and validation.
"""

import unittest
from src.data_models import TripInput, ReimbursementResult, TestCase, ValidationMetrics


class TestTripInput(unittest.TestCase):
    """Test cases for TripInput class"""
    
    def test_valid_trip_input(self):
        """Test creation of valid trip input"""
        trip = TripInput(
            trip_duration_days=5,
            miles_traveled=250.5,
            total_receipts_amount=150.75
        )
        self.assertEqual(trip.trip_duration_days, 5)
        self.assertEqual(trip.miles_traveled, 250.5)
        self.assertEqual(trip.total_receipts_amount, 150.75)
    
    def test_calculated_properties(self):
        """Test calculated properties"""
        trip = TripInput(
            trip_duration_days=4,
            miles_traveled=200.0,
            total_receipts_amount=100.0
        )
        self.assertEqual(trip.miles_per_day, 50.0)
        self.assertEqual(trip.receipts_per_day, 25.0)
    
    def test_invalid_days(self):
        """Test validation of invalid trip duration"""
        with self.assertRaises(ValueError):
            TripInput(trip_duration_days=0, miles_traveled=100, total_receipts_amount=50)
        
        with self.assertRaises(ValueError):
            TripInput(trip_duration_days=-1, miles_traveled=100, total_receipts_amount=50)
        
        with self.assertRaises(ValueError):
            TripInput(trip_duration_days=1.5, miles_traveled=100, total_receipts_amount=50)
    
    def test_invalid_miles(self):
        """Test validation of invalid miles"""
        with self.assertRaises(ValueError):
            TripInput(trip_duration_days=3, miles_traveled=-10, total_receipts_amount=50)
    
    def test_invalid_receipts(self):
        """Test validation of invalid receipts"""
        with self.assertRaises(ValueError):
            TripInput(trip_duration_days=3, miles_traveled=100, total_receipts_amount=-25)
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Zero miles should be valid
        trip = TripInput(trip_duration_days=1, miles_traveled=0, total_receipts_amount=0)
        self.assertEqual(trip.miles_per_day, 0.0)
        self.assertEqual(trip.receipts_per_day, 0.0)
        
        # Very large values should work but may generate warnings
        trip = TripInput(trip_duration_days=365, miles_traveled=10000, total_receipts_amount=50000)
        self.assertEqual(trip.trip_duration_days, 365)


class TestReimbursementResult(unittest.TestCase):
    """Test cases for ReimbursementResult class"""
    
    def test_valid_result(self):
        """Test creation of valid reimbursement result"""
        result = ReimbursementResult(
            amount=487.25,
            confidence=0.95,
            breakdown={'per_diem': 200, 'mileage': 150, 'receipts': 137.25},
            warnings=['High mileage detected']
        )
        self.assertEqual(result.amount, 487.25)
        self.assertEqual(result.confidence, 0.95)
        self.assertIsNotNone(result.breakdown)
        self.assertIsNotNone(result.warnings)
    
    def test_minimal_result(self):
        """Test creation with minimal parameters"""
        result = ReimbursementResult(amount=100.0)
        self.assertEqual(result.amount, 100.0)
        self.assertIsNone(result.confidence)
        self.assertIsNone(result.breakdown)
        self.assertIsNone(result.warnings)
    
    def test_invalid_amount(self):
        """Test validation of invalid amounts"""
        with self.assertRaises(ValueError):
            ReimbursementResult(amount=-50.0)
    
    def test_invalid_confidence(self):
        """Test validation of invalid confidence"""
        with self.assertRaises(ValueError):
            ReimbursementResult(amount=100.0, confidence=1.5)
        
        with self.assertRaises(ValueError):
            ReimbursementResult(amount=100.0, confidence=-0.1)


class TestTestCase(unittest.TestCase):
    """Test cases for TestCase class"""
    
    def test_valid_test_case(self):
        """Test creation of valid test case"""
        trip_input = TripInput(5, 250, 150)
        test_case = TestCase(
            input_data=trip_input,
            expected_output=487.25,
            case_id="test_001"
        )
        self.assertEqual(test_case.input_data, trip_input)
        self.assertEqual(test_case.expected_output, 487.25)
        self.assertEqual(test_case.case_id, "test_001")
    
    def test_private_case(self):
        """Test creation of private test case (no expected output)"""
        trip_input = TripInput(3, 150, 75)
        test_case = TestCase(input_data=trip_input)
        self.assertEqual(test_case.input_data, trip_input)
        self.assertIsNone(test_case.expected_output)
        self.assertIsNone(test_case.case_id)
    
    def test_invalid_expected_output(self):
        """Test validation of invalid expected output"""
        trip_input = TripInput(5, 250, 150)
        with self.assertRaises(ValueError):
            TestCase(input_data=trip_input, expected_output=-100.0)


class TestValidationMetrics(unittest.TestCase):
    """Test cases for ValidationMetrics class"""
    
    def test_metrics_creation(self):
        """Test creation of validation metrics"""
        metrics = ValidationMetrics(
            mean_absolute_error=25.5,
            exact_matches=10,
            close_matches=25,
            max_error=150.0,
            total_cases=100,
            score=2550.0
        )
        self.assertEqual(metrics.mean_absolute_error, 25.5)
        self.assertEqual(metrics.exact_matches, 10)
        self.assertEqual(metrics.close_matches, 25)
        self.assertEqual(metrics.max_error, 150.0)
        self.assertEqual(metrics.total_cases, 100)
        self.assertEqual(metrics.score, 2550.0)
    
    def test_calculated_properties(self):
        """Test calculated properties"""
        metrics = ValidationMetrics(
            mean_absolute_error=25.5,
            exact_matches=10,
            close_matches=25,
            max_error=150.0,
            total_cases=100,
            score=2550.0
        )
        self.assertEqual(metrics.exact_match_rate, 10.0)
        self.assertEqual(metrics.close_match_rate, 25.0)
    
    def test_zero_total_cases(self):
        """Test handling of zero total cases"""
        metrics = ValidationMetrics(
            mean_absolute_error=0.0,
            exact_matches=0,
            close_matches=0,
            max_error=0.0,
            total_cases=0,
            score=0.0
        )
        self.assertEqual(metrics.exact_match_rate, 0.0)
        self.assertEqual(metrics.close_match_rate, 0.0)
    
    def test_string_representation(self):
        """Test string representation"""
        metrics = ValidationMetrics(
            mean_absolute_error=25.5,
            exact_matches=10,
            close_matches=25,
            max_error=150.0,
            total_cases=100,
            score=2550.0
        )
        str_repr = str(metrics)
        self.assertIn("25.50", str_repr)
        self.assertIn("10/100", str_repr)
        self.assertIn("25/100", str_repr)


if __name__ == '__main__':
    unittest.main()