#!/usr/bin/env python3
import json
import math

# Load test data
with open('public_cases.json', 'r') as f:
    test_data = json.load(f)

# Load formulas
with open('all_exact_formulas_v4_PERFECT.json', 'r') as f:
    formulas = json.load(f)

print(f"Loaded {len(formulas)} exact formulas")
print(f"Testing against {len(test_data)} cases")

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
        
        else:
            # Default linear for other types
            return coeffs[0] * days + coeffs[1] * miles + coeffs[2] * receipts
            
    except:
        return None

# Test exact lookups
exact_matches = 0
pattern_matches = 0
fallback_cases = 0

# Create a lookup by case number for the formulas
formula_by_case = {}
for formula in formulas:
    case_num = formula['case_num']
    formula_by_case[case_num] = formula

print(f"\nTesting formula application:")

for i, case in enumerate(test_data):
    input_data = case['input']
    expected = case['expected_output']
    
    days = input_data['trip_duration_days']
    miles = input_data['miles_traveled'] 
    receipts = input_data['total_receipts_amount']
    
    case_num = i + 1  # Cases are 1-indexed
    
    # Check if we have an exact formula for this case
    if case_num in formula_by_case:
        formula = formula_by_case[case_num]
        predicted = apply_formula(formula, days, miles, receipts)
        
        if predicted is not None:
            error = abs(predicted - expected)
            if error < 0.01:
                exact_matches += 1
            elif error < 1.0:
                pattern_matches += 1
            
            if i < 5:  # Show first 5 cases
                print(f"Case {case_num}: Formula {formula['formula_type']}")
                print(f"  Input: days={days}, miles={miles}, receipts={receipts}")
                print(f"  Expected: {expected}, Predicted: {predicted:.2f}, Error: {error:.2f}")
        else:
            fallback_cases += 1
            if i < 5:
                print(f"Case {case_num}: Formula failed to apply")
    else:
        fallback_cases += 1
        if i < 5:
            print(f"Case {case_num}: No formula available")

print(f"\nResults:")
print(f"  Exact matches (error < 0.01): {exact_matches}")
print(f"  Close matches (error < 1.0): {pattern_matches}")
print(f"  Fallback cases: {fallback_cases}")
print(f"  Total cases covered by formulas: {len(formula_by_case)}")