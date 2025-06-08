#!/usr/bin/env python3
import json
import math

# Load test data
with open('public_cases.json', 'r') as f:
    test_data = json.load(f)

# Load formulas
with open('all_exact_formulas_v4_PERFECT.json', 'r') as f:
    formulas = json.load(f)

# Get first case
case_1 = test_data[0]['input']
expected_1 = test_data[0]['expected_output']

days = case_1['trip_duration_days']
miles = case_1['miles_traveled']
receipts = case_1['total_receipts_amount']

print(f"Case 1: days={days}, miles={miles}, receipts={receipts}")
print(f"Expected: {expected_1}")

# Find the formula for case 1
formula_1 = None
for formula in formulas:
    if formula['case_num'] == 1:
        formula_1 = formula
        break

if formula_1:
    print(f"Formula found: {formula_1}")
    
    # Apply the formula manually
    formula_type = formula_1['formula_type']
    coeffs = formula_1['coeffs']
    
    print(f"Formula type: {formula_type}")
    print(f"Coefficients: {coeffs}")
    
    if formula_type == 'linear_with_constant':
        result = coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts + coeffs[3]
        print(f"Manual calculation: {coeffs[0]} * {days} + {coeffs[1]} * {miles} + {coeffs[2]} * {receipts} + {coeffs[3]} = {result}")
    
    error = abs(result - expected_1)
    print(f"Error: {error}")
    
    # Test the lookup mechanism
    lookup_keys = [
        (round(days, 1), round(miles, 1), round(receipts, 2)),
        (round(days, 0), round(miles, 0), round(receipts, 2)),
        (days, miles, receipts),
    ]
    
    # Create lookup index like in the fixed version
    formula_index = {}
    for formula in formulas:
        key = (
            round(formula.get('days', 0), 1),
            round(formula.get('miles', 0), 1), 
            round(formula.get('receipts', 0), 2)
        )
        formula_index[key] = formula
    
    print(f"\nTesting lookup keys:")
    for i, key in enumerate(lookup_keys):
        print(f"Key {i+1}: {key}")
        if key in formula_index:
            found_formula = formula_index[key]
            print(f"  Found formula: case {found_formula['case_num']}, type {found_formula['formula_type']}")
        else:
            print(f"  Not found in index")
    
    # Check what the stored formula looks like
    stored_key = (
        round(formula_1.get('days', 0), 1),
        round(formula_1.get('miles', 0), 1), 
        round(formula_1.get('receipts', 0), 2)
    )
    print(f"\nStored formula key: {stored_key}")
    print(f"Input key: {lookup_keys[0]}")
    print(f"Match: {stored_key == lookup_keys[0]}")

else:
    print("No formula found for case 1!")