#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd
from itertools import product

# Load the data
with open('/Users/vthenappan/Documents/GitHub/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame([{
    'days': case['input']['trip_duration_days'],
    'miles': case['input']['miles_traveled'], 
    'receipts': case['input']['total_receipts_amount'],
    'output': case['expected_output']
} for case in data])

print("=== DEEP MATHEMATICAL ANALYSIS ===")

# The correlation with receipts is very high (0.704) - this suggests receipts are a major component
# Let's see if we can find a pattern where receipts are multiplied by some factor

# Look for patterns where output relates directly to receipts
df['output_per_receipt'] = df['output'] / df['receipts']
print(f"Output per receipt - Mean: {df['output_per_receipt'].mean():.2f}, Std: {df['output_per_receipt'].std():.2f}")

# The standard deviation is very high, suggesting this isn't a simple multiplication

# Let's test if there are different formulas for different ranges
print("\n=== TESTING RECEIPT-BASED FORMULAS ===")

# Test: output = receipts * days * factor
df['receipts_times_days'] = df['receipts'] * df['days']
df['output_per_receipts_days'] = df['output'] / df['receipts_times_days']
print(f"Output per (receipts * days) - Mean: {df['output_per_receipts_days'].mean():.2f}, Std: {df['output_per_receipts_days'].std():.2f}")

# Test: Maybe there's a base component plus receipts component
print("\n=== LOOKING FOR BASE + RECEIPTS PATTERN ===")

# If formula is: output = base_per_day * days + receipts * factor
# Then: (output - receipts * factor) / days should be constant

for factor in [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]:
    df[f'adjusted_per_day_{factor}'] = (df['output'] - df['receipts'] * factor) / df['days']
    std_dev = df[f'adjusted_per_day_{factor}'].std()
    mean_val = df[f'adjusted_per_day_{factor}'].mean()
    print(f"Factor {factor}: Mean base per day = {mean_val:.2f}, Std = {std_dev:.2f}")

# Let's also test the reverse: base + (receipts * days * factor)
print("\n=== TESTING BASE + (RECEIPTS * DAYS) FORMULA ===")

for base in [100, 120, 140, 160, 180, 200]:
    for factor in [50, 60, 70, 80, 90, 100, 110, 120]:
        df['predicted'] = base * df['days'] + df['receipts'] * factor
        df['error'] = abs(df['predicted'] - df['output'])
        max_error = df['error'].max()
        mean_error = df['error'].mean()
        if max_error < 50:  # Look for very close matches
            print(f"Base {base}, Factor {factor}: Max error {max_error:.3f}, Mean error {mean_error:.3f}")

# Let's examine the patterns more systematically
print("\n=== SYSTEMATIC FORMULA TESTING ===")

# Test formula: base * days + receipts * days * factor
def test_formula_systematic():
    best_error = float('inf')
    best_params = None
    
    for base in range(80, 201, 10):
        for factor in range(50, 151, 5):
            predicted = base * df['days'] + df['receipts'] * factor
            error = ((predicted - df['output']) ** 2).mean() ** 0.5  # RMSE
            
            if error < best_error:
                best_error = error
                best_params = (base, factor)
    
    print(f"Best base + receipts*factor: base={best_params[0]}, factor={best_params[1]}, RMSE={best_error:.3f}")
    return best_params

best_base, best_factor = test_formula_systematic()

# Test the best formula
df['predicted_best'] = best_base * df['days'] + df['receipts'] * best_factor
df['error_best'] = abs(df['predicted_best'] - df['output'])
print(f"Best formula max error: {df['error_best'].max():.3f}")
print(f"Best formula mean error: {df['error_best'].mean():.3f}")

# Check if miles factor into the calculation
print("\n=== TESTING MILES COMPONENT ===")

# Maybe it's: base * days + receipts * factor + miles * mile_factor
def test_three_component():
    best_error = float('inf')
    best_params = None
    
    for base in range(50, 151, 20):
        for receipt_factor in range(70, 131, 10):
            for mile_factor in range(1, 21, 2):
                predicted = base * df['days'] + df['receipts'] * receipt_factor + df['miles'] * mile_factor
                error = ((predicted - df['output']) ** 2).mean() ** 0.5
                
                if error < best_error:
                    best_error = error
                    best_params = (base, receipt_factor, mile_factor)
    
    print(f"Best 3-component: base={best_params[0]}, receipt_factor={best_params[1]}, mile_factor={best_params[2]}, RMSE={best_error:.3f}")
    return best_params

best_base3, best_receipt_factor3, best_mile_factor3 = test_three_component()

# Test this formula
df['predicted_3comp'] = best_base3 * df['days'] + df['receipts'] * best_receipt_factor3 + df['miles'] * best_mile_factor3
df['error_3comp'] = abs(df['predicted_3comp'] - df['output'])
print(f"3-component formula max error: {df['error_3comp'].max():.3f}")
print(f"3-component formula mean error: {df['error_3comp'].mean():.3f}")

# Let's look for an exact match by testing decimal precision
print("\n=== TESTING HIGH-PRECISION FORMULAS ===")

# Test with decimal precision
def test_precise_formula():
    best_error = float('inf')
    best_params = None
    
    # Narrow down around the best values found
    base_range = np.arange(best_base3 - 10, best_base3 + 11, 0.5)
    receipt_range = np.arange(best_receipt_factor3 - 10, best_receipt_factor3 + 11, 0.5)
    mile_range = np.arange(best_mile_factor3 - 2, best_mile_factor3 + 3, 0.1)
    
    for base in base_range:
        for receipt_factor in receipt_range:
            for mile_factor in mile_range:
                predicted = base * df['days'] + df['receipts'] * receipt_factor + df['miles'] * mile_factor
                max_error = abs(predicted - df['output']).max()
                
                if max_error < best_error:
                    best_error = max_error
                    best_params = (base, receipt_factor, mile_factor)
                
                if max_error < 0.01:  # Perfect match
                    print(f"EXACT MATCH FOUND: base={base:.1f}, receipt_factor={receipt_factor:.1f}, mile_factor={mile_factor:.1f}")
                    return base, receipt_factor, mile_factor
    
    print(f"Best precise formula: base={best_params[0]:.1f}, receipt_factor={best_params[1]:.1f}, mile_factor={best_params[2]:.1f}, max_error={best_error:.6f}")
    return best_params

precise_params = test_precise_formula()

# Let's also test some business-logical values that might make sense
print("\n=== TESTING BUSINESS-LOGICAL VALUES ===")

# Standard business rates
business_tests = [
    (100, 100, 0.56),  # $100/day + receipts*100 + $0.56/mile
    (120, 100, 0.58),  # $120/day + receipts*100 + $0.58/mile (standard mileage)
    (100, 120, 0.50),  # $100/day + receipts*120 + $0.50/mile
    (80, 120, 1.0),    # $80/day + receipts*120 + $1.00/mile
]

for base, receipt_factor, mile_factor in business_tests:
    predicted = base * df['days'] + df['receipts'] * receipt_factor + df['miles'] * mile_factor
    max_error = abs(predicted - df['output']).max()
    mean_error = abs(predicted - df['output']).mean()
    print(f"Base {base}, Receipt factor {receipt_factor}, Mile factor {mile_factor}: Max error {max_error:.3f}, Mean error {mean_error:.3f}")

# Let's examine edge cases to understand the formula better
print("\n=== EXAMINING EDGE CASES ===")

# Look at cases with very low receipts
low_receipt_cases = df[df['receipts'] < 5].copy()
print(f"Low receipt cases (< $5): {len(low_receipt_cases)} cases")
if len(low_receipt_cases) > 0:
    print("Low receipt case analysis:")
    for _, row in low_receipt_cases.head(5).iterrows():
        print(f"  Days: {row['days']}, Miles: {row['miles']:.1f}, Receipts: ${row['receipts']:.2f} -> ${row['output']:.2f}")

# Look at cases with very high receipts
high_receipt_cases = df[df['receipts'] > 1000].copy()
print(f"High receipt cases (> $1000): {len(high_receipt_cases)} cases")
if len(high_receipt_cases) > 0:
    print("High receipt case analysis:")
    for _, row in high_receipt_cases.head(5).iterrows():
        print(f"  Days: {row['days']}, Miles: {row['miles']:.1f}, Receipts: ${row['receipts']:.2f} -> ${row['output']:.2f}")

print("\nSaving detailed analysis...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/detailed_analysis.csv', index=False)