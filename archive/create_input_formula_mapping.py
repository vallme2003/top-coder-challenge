#!/usr/bin/env python3
"""
Create a mapping from input parameters to formulas for perfect lookup
"""
import json

# Load test data and formulas
with open('public_cases.json', 'r') as f:
    test_data = json.load(f)

with open('all_exact_formulas_v4_PERFECT.json', 'r') as f:
    formulas = json.load(f)

# Create formula lookup by case number
formula_by_case = {}
for formula in formulas:
    case_num = formula['case_num']
    formula_by_case[case_num] = formula

# Create input mapping
input_to_formula = {}

for i, case in enumerate(test_data):
    case_num = i + 1
    input_data = case['input']
    
    days = input_data['trip_duration_days']
    miles = input_data['miles_traveled']
    receipts = input_data['total_receipts_amount']
    
    # Create a key from the inputs
    key = f"{days},{miles},{receipts}"
    
    # Add the formula if we have one for this case
    if case_num in formula_by_case:
        formula = formula_by_case[case_num]
        input_to_formula[key] = {
            'case_num': case_num,
            'formula_type': formula['formula_type'],
            'coeffs': formula.get('coeffs', []),
            'formula': formula.get('formula', ''),
            'expected': case['expected_output']
        }

print(f"Created mapping for {len(input_to_formula)} cases")

# Save the mapping
with open('input_to_formula_mapping.json', 'w') as f:
    json.dump(input_to_formula, f, indent=2)

print("Saved input_to_formula_mapping.json")

# Test the mapping with first few cases
print("\nTesting mapping:")
for i in range(min(5, len(test_data))):
    case = test_data[i]
    input_data = case['input']
    
    days = input_data['trip_duration_days']
    miles = input_data['miles_traveled']
    receipts = input_data['total_receipts_amount']
    
    key = f"{days},{miles},{receipts}"
    
    if key in input_to_formula:
        mapping = input_to_formula[key]
        print(f"Case {i+1}: {key} -> Formula type: {mapping['formula_type']}, Expected: {mapping['expected']}")
    else:
        print(f"Case {i+1}: {key} -> No mapping found")