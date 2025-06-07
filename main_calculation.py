#!/usr/bin/env python3
"""
Main calculation script that integrates the modular system
for the 8090 Top Coder Challenge.

This script provides a clean interface to the modular reimbursement system
while maintaining backward compatibility with the original run.sh interface.
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from data_models import TripInput, ReimbursementResult
    from feature_engineering import FeatureEngineer
    from config import ModelConfig
    import math
except ImportError as e:
    # Fallback to simple calculation if modular system is not available
    print(f"Warning: Could not import modular system ({e}), falling back to simple calculation", file=sys.stderr)
    import math
    
    def simple_fallback_calculation(days, miles, receipts):
        """Simple fallback calculation based on earlier analysis"""
        days = int(days)
        miles = float(miles)
        receipts = float(receipts)
        
        # Key derived features
        days_miles = days * miles
        three_way = days * miles * receipts / 1000
        log_receipts = math.log1p(receipts)
        
        # Decision tree approximation (simplified)
        if log_receipts <= 6.720334:
            if days_miles <= 2070.000000:
                if days * receipts <= 562.984985:
                    if days_miles <= 566.000000:
                        result = 287.10
                    else:
                        result = 581.58
                else:
                    if days * receipts <= 3089.010010:
                        if days_miles <= 1310.500000:
                            if receipts <= 461.820007:
                                result = 557.93
                            else:
                                result = 643.31
                        else:
                            result = 750.45
                    else:
                        result = 876.59
            else:
                if three_way <= 2172.216919:
                    if days_miles <= 4940.000000:
                        if three_way <= 1258.291565:
                            if days <= 5.5:
                                result = 770.85
                            else:
                                result = 864.46
                        else:
                            if receipts <= 506.684998:
                                result = 941.68
                            else:
                                result = 1012.53
                    else:
                        result = 1145.20
                else:
                    if three_way <= 3762.473267:
                        if miles <= 771.000000:
                            result = 1163.81
                        else:
                            result = 1240.19
                    else:
                        result = 1442.54
        else:
            # High receipt cases
            if three_way <= 6405.638672:
                if three_way <= 1253.387817:
                    if days * receipts <= 9442.660156:
                        if 1/(1+receipts) <= 0.000923:
                            if days_miles <= 449.000000:
                                result = 1196.52
                            else:
                                result = 1296.70
                        else:
                            result = 1067.12
                    else:
                        result = 1505.52
                else:
                    result = 1400.0  # Simplified for remaining cases
            else:
                result = 1700.0  # Simplified for high complexity cases
        
        # Apply small adjustments
        cents = int(round(receipts * 100)) % 100
        if cents == 49 or cents == 99:
            result += 3
        if days == 5:
            result += 10
        
        return round(result, 2)
    
    def calculate_reimbursement(days, miles, receipts):
        return simple_fallback_calculation(days, miles, receipts)


def calculate_reimbursement_modular(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate reimbursement using the modular system.
    
    This function demonstrates the full modular approach with proper
    data validation, feature engineering, and error handling.
    
    Args:
        trip_duration_days: Number of days (int)
        miles_traveled: Miles traveled (float)
        total_receipts_amount: Receipt amount (float)
        
    Returns:
        float: Calculated reimbursement amount
    """
    try:
        # Create validated trip input
        trip_input = TripInput(
            trip_duration_days=int(trip_duration_days),
            miles_traveled=float(miles_traveled),
            total_receipts_amount=float(total_receipts_amount)
        )
        
        # Use conservative configuration
        config = ModelConfig(
            max_depth=4,
            min_samples_split=20,
            min_samples_leaf=10,
            use_polynomial_features=False,
            apply_regularization=True
        )
        
        # Extract features using the feature engineering pipeline
        feature_engineer = FeatureEngineer(config)
        feature_set = feature_engineer.extract_features(trip_input)
        
        # Apply the decision tree logic using extracted features
        features = feature_set.all_features
        feature_dict = feature_set.to_dict()
        
        # Use key features for decision tree
        log_receipts = feature_dict['log_receipts']
        days_miles = feature_dict['days_miles']
        three_way = feature_dict['three_way_interaction']
        days_receipts = feature_dict['days_receipts']
        inv_receipts = feature_dict['inv_receipts']
        
        # Apply the trained decision tree logic
        if log_receipts <= 6.720334:
            if days_miles <= 2070.000000:
                if days_receipts <= 562.984985:
                    if days_miles <= 566.000000:
                        result = 287.10
                    else:
                        result = 581.58
                else:
                    if days_receipts <= 3089.010010:
                        if days_miles <= 1310.500000:
                            if trip_input.total_receipts_amount <= 461.820007:
                                result = 557.93
                            else:
                                result = 643.31
                        else:
                            result = 750.45
                    else:
                        result = 876.59
            else:
                if three_way <= 2172.216919:
                    if days_miles <= 4940.000000:
                        if three_way <= 1258.291565:
                            if trip_input.trip_duration_days <= 5.5:
                                result = 770.85
                            else:
                                result = 864.46
                        else:
                            if trip_input.total_receipts_amount <= 506.684998:
                                result = 941.68
                            else:
                                result = 1012.53
                    else:
                        result = 1145.20
                else:
                    if three_way <= 3762.473267:
                        if trip_input.miles_traveled <= 771.000000:
                            result = 1163.81
                        else:
                            result = 1240.19
                    else:
                        result = 1442.54
        else:
            # High log_receipts cases
            if three_way <= 6405.638672:
                if three_way <= 1253.387817:
                    if days_receipts <= 9442.660156:
                        if inv_receipts <= 0.000923:
                            if days_miles <= 449.000000:
                                result = 1196.52
                            else:
                                result = 1296.70
                        else:
                            result = 1067.12
                    else:
                        result = 1505.52
                else:
                    # Additional logic for mid-range three_way values
                    if days_receipts <= 5494.430176:
                        miles_receipts_scaled = feature_dict['miles_receipts_scaled']
                        if three_way <= 2917.123047:
                            if miles_receipts_scaled <= 834.080933:
                                result = 1297.57
                            else:
                                result = 1392.04
                        else:
                            result = 1488.02
                    else:
                        result = 1550.0  # Simplified
            else:
                # Very high three_way values
                result = 1700.0
        
        # Apply categorical adjustments
        if feature_dict.get('ends_49', 0) == 1:
            result += 3
        if feature_dict.get('ends_99', 0) == 1:
            result += 3
        if feature_dict.get('is_5_days', 0) == 1:
            result += 10
        
        return round(result, 2)
        
    except Exception as e:
        # Log error and fall back to simple calculation
        logging.warning(f"Modular calculation failed: {e}, falling back to simple calculation")
        return simple_fallback_calculation(trip_duration_days, miles_traveled, total_receipts_amount)


def main():
    """Main entry point for the calculation script"""
    if len(sys.argv) != 4:
        print("Usage: python main_calculation.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    try:
        days = sys.argv[1]
        miles = sys.argv[2]
        receipts = sys.argv[3]
        
        # Try modular calculation first, fall back to simple if needed
        try:
            result = calculate_reimbursement_modular(days, miles, receipts)
        except:
            result = calculate_reimbursement(days, miles, receipts)
        
        print(result)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()