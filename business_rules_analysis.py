#!/usr/bin/env python3
"""
BUSINESS RULES ANALYSIS
=======================

Since there's an analytical function with score 0, and our coefficient analysis 
shows patterns like "10*days" for 303 cases, the system likely uses business 
rules with conditional logic.

Hypothesis: Different rate structures based on:
- Trip length (1-3 days vs 4-7 days vs 8+ days)
- Distance ranges (local vs medium vs long distance)
- Receipt amounts (low vs medium vs high spending)
"""

import json
import numpy as np
import pandas as pd
from collections import defaultdict

def load_data():
    """Load public cases and discovered formulas"""
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    with open('all_exact_formulas_v4_PERFECT.json', 'r') as f:
        formulas = json.load(f)
    
    return public_cases, formulas

def analyze_business_rule_patterns(public_cases, formulas):
    """Analyze if formulas cluster by business rule categories"""
    
    print("=== BUSINESS RULE PATTERN ANALYSIS ===")
    
    # Create lookup for formulas by case number
    formula_by_case = {}
    for formula in formulas:
        formula_by_case[formula['case_num']] = formula
    
    # Analyze patterns by trip characteristics
    analysis_data = []
    
    for i, case in enumerate(public_cases):
        case_num = i + 1
        input_data = case['input']
        
        days = input_data['trip_duration_days']
        miles = input_data['miles_traveled']
        receipts = input_data['total_receipts_amount']
        expected = case['expected_output']
        
        # Categorize the trip
        trip_length_cat = 'short' if days <= 3 else 'medium' if days <= 7 else 'long'
        distance_cat = 'local' if miles <= 200 else 'medium' if miles <= 600 else 'long'
        spending_cat = 'low' if receipts <= 500 else 'medium' if receipts <= 1500 else 'high'
        
        # Get formula info if available
        formula_info = formula_by_case.get(case_num, {})
        formula_type = formula_info.get('formula_type', 'fallback')
        coeffs = formula_info.get('coeffs', [])
        
        analysis_data.append({
            'case_num': case_num,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'trip_length_cat': trip_length_cat,
            'distance_cat': distance_cat,
            'spending_cat': spending_cat,
            'formula_type': formula_type,
            'day_coeff': coeffs[0] if len(coeffs) > 0 else None,
            'mile_coeff': coeffs[1] if len(coeffs) > 1 else None,
            'receipt_coeff': coeffs[2] if len(coeffs) > 2 else None,
            'constant': coeffs[3] if len(coeffs) > 3 else None
        })
    
    df = pd.DataFrame(analysis_data)
    
    # Analyze coefficient patterns by categories
    print(f"\n=== COEFFICIENT PATTERNS BY TRIP LENGTH ===")
    for trip_cat in ['short', 'medium', 'long']:
        subset = df[df['trip_length_cat'] == trip_cat]
        linear_subset = subset[subset['formula_type'].isin(['linear', 'linear_with_constant'])]
        
        if len(linear_subset) > 10:
            print(f"\n{trip_cat.upper()} trips ({subset['days'].min()}-{subset['days'].max()} days):")
            print(f"  Cases: {len(subset)} total, {len(linear_subset)} linear")
            print(f"  Day coeff: mean={linear_subset['day_coeff'].mean():.1f}, mode={linear_subset['day_coeff'].mode().iloc[0] if len(linear_subset['day_coeff'].mode()) > 0 else 'N/A'}")
            print(f"  Mile coeff: mean={linear_subset['mile_coeff'].mean():.2f}")
            print(f"  Receipt coeff: mean={linear_subset['receipt_coeff'].mean():.2f}")
    
    print(f"\n=== COEFFICIENT PATTERNS BY DISTANCE ===")
    for dist_cat in ['local', 'medium', 'long']:
        subset = df[df['distance_cat'] == dist_cat]
        linear_subset = subset[subset['formula_type'].isin(['linear', 'linear_with_constant'])]
        
        if len(linear_subset) > 10:
            print(f"\n{dist_cat.upper()} distance ({subset['miles'].min():.0f}-{subset['miles'].max():.0f} miles):")
            print(f"  Cases: {len(subset)} total, {len(linear_subset)} linear")
            print(f"  Day coeff: mean={linear_subset['day_coeff'].mean():.1f}")
            print(f"  Mile coeff: mean={linear_subset['mile_coeff'].mean():.2f}, mode={linear_subset['mile_coeff'].mode().iloc[0] if len(linear_subset['mile_coeff'].mode()) > 0 else 'N/A'}")
            print(f"  Receipt coeff: mean={linear_subset['receipt_coeff'].mean():.2f}")
    
    print(f"\n=== COEFFICIENT PATTERNS BY SPENDING ===")
    for spend_cat in ['low', 'medium', 'high']:
        subset = df[df['spending_cat'] == spend_cat]
        linear_subset = subset[subset['formula_type'].isin(['linear', 'linear_with_constant'])]
        
        if len(linear_subset) > 10:
            print(f"\n{spend_cat.upper()} spending (${subset['receipts'].min():.0f}-${subset['receipts'].max():.0f}):")
            print(f"  Cases: {len(subset)} total, {len(linear_subset)} linear")
            print(f"  Day coeff: mean={linear_subset['day_coeff'].mean():.1f}")
            print(f"  Mile coeff: mean={linear_subset['mile_coeff'].mean():.2f}")
            print(f"  Receipt coeff: mean={linear_subset['receipt_coeff'].mean():.2f}, mode={linear_subset['receipt_coeff'].mode().iloc[0] if len(linear_subset['receipt_coeff'].mode()) > 0 else 'N/A'}")
    
    return df

def test_conditional_business_rules(public_cases, df):
    """Test conditional business rule hypotheses"""
    
    print(f"\n=== TESTING CONDITIONAL BUSINESS RULES ===")
    
    # Test the most promising pattern from coefficient analysis:
    # Days coefficient of 10 appears in 303 cases - let's see if there's a pattern
    
    # Hypothesis 1: Base rate of $10/day for most trips
    print(f"\n--- Hypothesis 1: $10/day base rate ---")
    day_10_cases = df[df['day_coeff'] == 10]
    print(f"Cases with $10/day coefficient: {len(day_10_cases)}")
    
    if len(day_10_cases) > 0:
        print(f"Trip length distribution:")
        for days in sorted(day_10_cases['days'].unique()):
            count = len(day_10_cases[day_10_cases['days'] == days])
            print(f"  {days} days: {count} cases")
        
        print(f"Most common mile coefficients:")
        mile_coeffs = day_10_cases['mile_coeff'].value_counts().head(5)
        for coeff, count in mile_coeffs.items():
            print(f"  {coeff}: {count} cases")
        
        print(f"Most common receipt coefficients:")
        receipt_coeffs = day_10_cases['receipt_coeff'].value_counts().head(5)
        for coeff, count in receipt_coeffs.items():
            print(f"  {coeff}: {count} cases")
    
    # Hypothesis 2: Different rates for different trip lengths
    print(f"\n--- Hypothesis 2: Trip length-based rates ---")
    
    def test_trip_length_rates():
        """Test if different trip lengths use different day rates"""
        
        candidates = [
            # 1-3 days: $10/day, 4-7 days: $12/day, 8+ days: $14/day
            {
                'name': 'Progressive Daily Rates',
                'rules': {
                    (1, 3): 10,
                    (4, 7): 12,
                    (8, float('inf')): 14
                },
                'mile_rate': 0.56,
                'receipt_rate': 0.75
            },
            
            # 1-2 days: $8/day, 3-5 days: $10/day, 6+ days: $12/day  
            {
                'name': 'Business Travel Rates',
                'rules': {
                    (1, 2): 8,
                    (3, 5): 10,
                    (6, float('inf')): 12
                },
                'mile_rate': 0.5,
                'receipt_rate': 0.8
            }
        ]
        
        for candidate in candidates:
            print(f"\nTesting: {candidate['name']}")
            
            exact_matches = 0
            errors = []
            
            for _, row in df.iterrows():
                days = row['days']
                miles = row['miles'] 
                receipts = row['receipts']
                expected = row['expected']
                
                # Find the day rate for this trip length
                day_rate = None
                for (min_days, max_days), rate in candidate['rules'].items():
                    if min_days <= days <= max_days:
                        day_rate = rate
                        break
                
                if day_rate is not None:
                    predicted = (day_rate * days + 
                               candidate['mile_rate'] * miles + 
                               candidate['receipt_rate'] * receipts)
                    
                    error = abs(predicted - expected)
                    errors.append(error)
                    
                    if error < 0.01:
                        exact_matches += 1
            
            avg_error = np.mean(errors)
            score = avg_error * 100 + (1000 - exact_matches) * 0.1
            
            print(f"  Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
            print(f"  Average error: ${avg_error:.2f}")
            print(f"  Score: {score:.2f}")
    
    test_trip_length_rates()
    
    # Hypothesis 3: Receipt thresholds with different rates
    print(f"\n--- Hypothesis 3: Receipt threshold rates ---")
    
    def test_receipt_thresholds():
        """Test if different receipt amounts use different rates"""
        
        candidates = [
            {
                'name': 'Receipt Tier System',
                'day_rate': 10,
                'mile_rate': 0.56,
                'receipt_rules': {
                    (0, 500): 0.8,      # Low spending: 80%
                    (500, 1500): 0.7,   # Medium spending: 70%
                    (1500, float('inf')): 0.6  # High spending: 60%
                }
            }
        ]
        
        for candidate in candidates:
            print(f"\nTesting: {candidate['name']}")
            
            exact_matches = 0
            errors = []
            
            for _, row in df.iterrows():
                days = row['days']
                miles = row['miles']
                receipts = row['receipts']
                expected = row['expected']
                
                # Find receipt rate for this spending level
                receipt_rate = None
                for (min_receipts, max_receipts), rate in candidate['receipt_rules'].items():
                    if min_receipts <= receipts < max_receipts:
                        receipt_rate = rate
                        break
                
                if receipt_rate is not None:
                    predicted = (candidate['day_rate'] * days +
                               candidate['mile_rate'] * miles +
                               receipt_rate * receipts)
                    
                    error = abs(predicted - expected)
                    errors.append(error)
                    
                    if error < 0.01:
                        exact_matches += 1
            
            avg_error = np.mean(errors)
            score = avg_error * 100 + (1000 - exact_matches) * 0.1
            
            print(f"  Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
            print(f"  Average error: ${avg_error:.2f}")
            print(f"  Score: {score:.2f}")
    
    test_receipt_thresholds()

def main():
    """Main business rules analysis"""
    print("BUSINESS RULES ANALYSIS")
    print("=" * 50)
    
    # Load data
    public_cases, formulas = load_data()
    print(f"Loaded {len(public_cases)} public cases and {len(formulas)} discovered formulas")
    
    # Analyze patterns by business categories
    df = analyze_business_rule_patterns(public_cases, formulas)
    
    # Test conditional business rule hypotheses
    test_conditional_business_rules(public_cases, df)
    
    print(f"\n=== NEXT STEPS ===")
    print(f"1. The $10/day coefficient appears in 303 cases - investigate this pattern further")
    print(f"2. Test more complex conditional logic based on trip characteristics") 
    print(f"3. Consider legacy 1960s business travel policies")

if __name__ == "__main__":
    main()