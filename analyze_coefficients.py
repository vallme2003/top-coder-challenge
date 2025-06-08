#!/usr/bin/env python3
"""
Coefficient Pattern Analysis for Score 0 Discovery
================================================

Analyzes the 1,000 exact formulas to find patterns that could lead
to the unified analytical function.
"""

import json
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt

def load_data():
    """Load the input-to-formula mapping and public cases"""
    with open('input_to_formula_mapping.json', 'r') as f:
        mapping = json.load(f)
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    return mapping, cases

def analyze_coefficient_patterns(mapping):
    """Analyze coefficient patterns across all formula types"""
    
    # Group by formula type
    by_type = defaultdict(list)
    
    for key, formula_info in mapping.items():
        formula_type = formula_info['formula_type']
        coeffs = formula_info.get('coeffs', [])
        
        # Parse the input values
        parts = key.split(',')
        days = float(parts[0])
        miles = float(parts[1])
        receipts = float(parts[2])
        expected = formula_info['expected']
        
        by_type[formula_type].append({
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'coeffs': coeffs,
            'key': key
        })
    
    print("=== Formula Type Distribution ===")
    for formula_type, cases in by_type.items():
        print(f"{formula_type}: {len(cases)} cases")
    
    return by_type

def analyze_linear_with_constant(cases):
    """Deep analysis of linear_with_constant cases (most common)"""
    print("\n=== Linear With Constant Analysis ===")
    print(f"Total cases: {len(cases)}")
    
    # Extract coefficients
    coeffs_data = []
    for case in cases:
        if len(case['coeffs']) >= 4:
            coeffs_data.append({
                'days': case['days'],
                'miles': case['miles'], 
                'receipts': case['receipts'],
                'expected': case['expected'],
                'a': case['coeffs'][0],  # days coefficient
                'b': case['coeffs'][1],  # miles coefficient
                'c': case['coeffs'][2],  # receipts coefficient
                'd': case['coeffs'][3]   # constant
            })
    
    df = pd.DataFrame(coeffs_data)
    
    print("\nCoefficient Statistics:")
    print(df[['a', 'b', 'c', 'd']].describe())
    
    # Look for patterns
    print("\nUnique coefficient values:")
    print(f"Days coeff (a): {sorted(df['a'].unique())}")
    print(f"Miles coeff (b): {sorted(df['b'].unique())}")
    print(f"Receipts coeff (c): {sorted(df['c'].unique())}")
    print(f"Constant (d): {sorted(df['d'].unique())}")
    
    return df

def search_universal_patterns(by_type):
    """Search for universal patterns across all formula types"""
    print("\n=== Universal Pattern Search ===")
    
    all_cases = []
    for formula_type, cases in by_type.items():
        for case in cases:
            all_cases.append({
                'days': case['days'],
                'miles': case['miles'],
                'receipts': case['receipts'],
                'expected': case['expected'],
                'formula_type': formula_type
            })
    
    df = pd.DataFrame(all_cases)
    
    # Check for simple rate patterns
    print("\nTesting basic rate patterns:")
    
    # Pattern 1: Base daily rate + mileage rate + receipt percentage
    for daily_rate in [80, 90, 100, 110, 120]:
        for mileage_rate in [0.3, 0.4, 0.5, 0.6, 0.7]:
            for receipt_rate in [0.1, 0.2, 0.3, 0.4, 0.5]:
                df['predicted'] = daily_rate * df['days'] + mileage_rate * df['miles'] + receipt_rate * df['receipts']
                exact_matches = (abs(df['predicted'] - df['expected']) < 0.01).sum()
                if exact_matches > 50:  # If we get many matches
                    print(f"Pattern: {daily_rate}*days + {mileage_rate}*miles + {receipt_rate}*receipts")
                    print(f"Exact matches: {exact_matches}/1000")
    
    return df

def test_business_logic_patterns(df):
    """Test business logic patterns typical of 1960s expense systems"""
    print("\n=== Business Logic Pattern Testing ===")
    
    # Pattern: Different rates based on trip characteristics
    def test_tiered_system(df):
        """Test tiered reimbursement system"""
        predictions = []
        
        for _, row in df.iterrows():
            days = row['days']
            miles = row['miles']
            receipts = row['receipts']
            
            # Hypothesis: Tiered system based on trip length and expenses
            if days <= 2:
                # Short trips: higher daily rate, lower mileage
                pred = 100 * days + 0.5 * miles + 0.3 * receipts
            elif days <= 5:
                # Medium trips: standard rates
                pred = 90 * days + 0.4 * miles + 0.25 * receipts
            else:
                # Long trips: bulk rate
                pred = 80 * days + 0.35 * miles + 0.2 * receipts
            
            predictions.append(pred)
        
        df['tiered_pred'] = predictions
        exact_matches = (abs(df['tiered_pred'] - df['expected']) < 0.01).sum()
        print(f"Tiered system matches: {exact_matches}/1000")
        
        return exact_matches
    
    # Test the tiered system
    tiered_matches = test_tiered_system(df)
    
    # Pattern: Weekend/weekday differences
    def test_weekend_system(df):
        """Test system with weekend bonuses"""
        # This is harder to test without knowing start dates
        # But we can test day-based variations
        predictions = []
        
        for _, row in df.iterrows():
            days = row['days']
            miles = row['miles']
            receipts = row['receipts']
            
            # Hypothesis: Weekend days get bonus
            weekend_bonus = 10 if days >= 2 else 0  # Rough proxy
            pred = 85 * days + 0.4 * miles + 0.25 * receipts + weekend_bonus
            
            predictions.append(pred)
        
        df['weekend_pred'] = predictions
        exact_matches = (abs(df['weekend_pred'] - df['expected']) < 0.01).sum()
        print(f"Weekend system matches: {exact_matches}/1000")
        
        return exact_matches
    
    weekend_matches = test_weekend_system(df)
    
    return max(tiered_matches, weekend_matches)

def main():
    """Main analysis function"""
    print("Loading data...")
    mapping, cases = load_data()
    
    print(f"Loaded {len(mapping)} exact formulas and {len(cases)} test cases")
    
    # Analyze coefficient patterns
    by_type = analyze_coefficient_patterns(mapping)
    
    # Deep dive into most common type
    if 'linear_with_constant' in by_type:
        linear_df = analyze_linear_with_constant(by_type['linear_with_constant'])
    
    # Search for universal patterns
    all_df = search_universal_patterns(by_type)
    
    # Test business logic patterns
    best_matches = test_business_logic_patterns(all_df)
    
    print(f"\nBest pattern found: {best_matches} exact matches")
    
    if best_matches < 900:
        print("\nNext steps:")
        print("1. Analyze coefficient relationships vs input parameters")
        print("2. Test more complex business rules")
        print("3. Look for conditional logic based on input ranges")

if __name__ == "__main__":
    main()