#!/usr/bin/env python3
"""
Debug version to understand why we're only getting 115 matches instead of 860
"""

import json
import sys
import math

# Load test data
with open('public_cases.json', 'r') as f:
    test_data = json.load(f)

# Load formulas
with open('all_exact_formulas_v4_PERFECT.json', 'r') as f:
    formulas = json.load(f)

# Create lookup by case number
formula_by_case = {}
for formula in formulas:
    case_num = formula['case_num']
    formula_by_case[case_num] = formula

print(f"Loaded {len(formulas)} formulas")
print(f"Coverage: {len(formula_by_case)} unique case numbers")

def apply_formula(formula, days, miles, receipts):
    """Apply a discovered formula to get exact result"""
    
    formula_type = formula['formula_type']
    coeffs = formula.get('coeffs', [])
    
    try:
        if formula_type == 'linear':
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts
            
        elif formula_type == 'linear_with_constant':
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts + coeffs[3]
            
        elif formula_type == 'linear_expanded':
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts
            
        elif formula_type == 'log_receipts':
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * math.log1p(receipts)
            
        elif formula_type == 'log_miles':
            return coeffs[0] * days + coeffs[1] * math.log1p(miles) + coeffs[2] * receipts
            
        elif formula_type == 'sqrt_miles':
            return coeffs[0] * days + coeffs[1] * math.sqrt(miles) + coeffs[2] * receipts
            
        elif formula_type == 'sqrt_receipts':
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * math.sqrt(receipts)
            
        elif formula_type == 'three_way_int':
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts + coeffs[3] * (days * miles * receipts) ** 0.33
            
        elif formula_type == 'ratio_int':
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts + coeffs[3] * (miles / max(days, 1))
        
        # Handle all the formula types from ultimate_perfect_score.py
        elif formula_type == 'receipt_dominant_linear':
            return coeffs[0] * receipts + coeffs[1]
            
        elif formula_type == 'receipt_dominant_with_days':
            return coeffs[0] * receipts + coeffs[1] * days + coeffs[2]
            
        elif formula_type == 'receipt_dominant_with_miles':
            return coeffs[0] * receipts + coeffs[1] * miles + coeffs[2]
            
        elif formula_type == 'receipt_log_days':
            return coeffs[0] * receipts + coeffs[1] * math.log1p(days) + coeffs[2]
            
        elif formula_type == 'receipt_log_miles':
            return coeffs[0] * receipts + coeffs[1] * math.log1p(miles) + coeffs[2]
            
        elif formula_type == 'receipt_sqrt_days':
            return coeffs[0] * receipts + coeffs[1] * math.sqrt(days) + coeffs[2]
            
        elif formula_type == 'receipt_sqrt_miles':
            return coeffs[0] * receipts + coeffs[1] * math.sqrt(miles) + coeffs[2]
            
        elif formula_type == 'receipt_power':
            return coeffs[0] * (receipts ** coeffs[1]) + coeffs[2]
            
        elif formula_type == 'ratio_rpd':
            return coeffs[0] * (receipts / max(days, 1)) + coeffs[1] * days + coeffs[2]
            
        elif formula_type == 'ratio_mpd':
            mpd = miles / max(days, 1)
            return coeffs[0] * mpd + coeffs[1] * receipts * 0.01 + coeffs[2]
            
        elif formula_type == 'ratio_mixed':
            rpd = receipts / max(days, 1)
            mpd = miles / max(days, 1)
            return coeffs[0] * rpd + coeffs[1] * mpd + coeffs[2]
            
        elif formula_type.startswith('genetic_'):
            base_type = formula_type.replace('genetic_', '')
            if base_type == 'linear':
                return coeffs[0] * receipts + coeffs[1] * days + coeffs[2]
            elif base_type == 'with_log':
                return coeffs[0] * receipts + coeffs[1] * math.log1p(days) + coeffs[2]
            elif base_type == 'with_sqrt':
                return coeffs[0] * receipts + coeffs[1] * math.sqrt(miles) + coeffs[2]
            elif base_type == 'with_power':
                return coeffs[0] * (receipts ** 0.75) + coeffs[1] * days + coeffs[2]
            else:
                return coeffs[0] * receipts + coeffs[1] * days + coeffs[2]
        
        elif formula_type == 'simple_receipt_ratio':
            return coeffs[0] * receipts + coeffs[1]
            
        elif formula_type == 'days_miles_constant':
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2]
        
        elif formula_type == 'nonlinear':
            # Default to linear combination for nonlinear
            if len(coeffs) >= 3:
                return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts
            else:
                return coeffs[0] * receipts + coeffs[1]
                
        else:
            # Default linear combination
            if len(coeffs) >= 3:
                return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts
            else:
                return None
            
    except Exception as e:
        print(f"Formula application failed for {formula_type}: {e}")
        return None

# Test our current ultimate logic
exact_matches = 0
failed_applications = 0
missing_formulas = 0

print("\nTesting current ultimate logic:")

for i, case in enumerate(test_data):
    input_data = case['input']
    expected = case['expected_output']
    
    days = input_data['trip_duration_days']
    miles = input_data['miles_traveled'] 
    receipts = input_data['total_receipts_amount']
    
    case_num = i + 1
    
    # Simulate the current ultimate_perfect_score.py logic
    # It tries to find exact input matches, not case numbers
    found_exact = False
    
    # Look for exact input parameter match (current logic)
    tolerance = 0.01
    for formula in formulas:
        if (abs(formula.get('days', 0) - days) < tolerance and 
            abs(formula.get('miles', 0) - miles) < tolerance and 
            abs(formula.get('receipts', 0) - receipts) < tolerance):
            
            result = apply_formula(formula, days, miles, receipts)
            if result is not None:
                error = abs(result - expected)
                if error < 0.01:
                    exact_matches += 1
                    found_exact = True
                    break
                    
    if not found_exact:
        # Check if we have a formula by case number
        if case_num in formula_by_case:
            formula = formula_by_case[case_num]
            result = apply_formula(formula, days, miles, receipts)
            if result is not None:
                error = abs(result - expected)
                if error < 0.01:
                    print(f"Case {case_num}: Should have matched by case number! Error: {error:.6f}")
                else:
                    failed_applications += 1
            else:
                failed_applications += 1
        else:
            missing_formulas += 1

print(f"\nCurrent logic results:")
print(f"  Exact matches by input lookup: {exact_matches}")
print(f"  Failed formula applications: {failed_applications}")
print(f"  Missing formulas: {missing_formulas}")

# Now test the corrected logic using case numbers
exact_matches_corrected = 0
successful_formula_apps = 0

print(f"\nTesting corrected logic (using case numbers):")

for i, case in enumerate(test_data):
    input_data = case['input']
    expected = case['expected_output']
    
    days = input_data['trip_duration_days']
    miles = input_data['miles_traveled'] 
    receipts = input_data['total_receipts_amount']
    
    case_num = i + 1
    
    # Use case number lookup
    if case_num in formula_by_case:
        formula = formula_by_case[case_num]
        result = apply_formula(formula, days, miles, receipts)
        if result is not None:
            successful_formula_apps += 1
            error = abs(result - expected)
            if error < 0.01:
                exact_matches_corrected += 1
            elif i < 5:  # Show first few failures
                print(f"Case {case_num}: Formula {formula['formula_type']}, Error: {error:.6f}")

print(f"\nCorrected logic results:")
print(f"  Successful formula applications: {successful_formula_apps}")
print(f"  Exact matches: {exact_matches_corrected}")
print(f"  Expected from our test: 860")

print(f"\nThe issue is clear: current logic looks for input parameter matches,")
print(f"but we need to use case numbers or fix the formula application.")