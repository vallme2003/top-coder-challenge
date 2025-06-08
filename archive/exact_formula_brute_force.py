#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd
import itertools

# Load the data
with open('/Users/vthenappan/Documents/GitHub/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame([{
    'days': case['input']['trip_duration_days'],
    'miles': case['input']['miles_traveled'], 
    'receipts': case['input']['total_receipts_amount'],
    'output': case['expected_output']
} for case in data])

print("=== EXACT FORMULA BRUTE FORCE SEARCH ===")

# Since there must be an exact analytical function, let me try ALL reasonable combinations
# with high precision

def test_formula_exact(base_rate, receipt_factor, mile_factor):
    """Test exact formula: base_rate * days + receipt_factor * receipts + mile_factor * miles"""
    predicted = base_rate * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
    max_error = abs(predicted - df['output']).max()
    return max_error

print("Brute force searching for EXACT formula (max error < 0.01)...")
print("This will test thousands of combinations...")

# Search ranges with high precision
base_rates = np.arange(50, 201, 0.5)
receipt_factors = np.arange(0.1, 1.01, 0.01) 
mile_factors = np.arange(0.1, 1.01, 0.01)

exact_matches = []
best_error = float('inf')
best_formula = None

total_combinations = len(base_rates) * len(receipt_factors) * len(mile_factors)
print(f"Testing {total_combinations:,} combinations...")

tested = 0
for base_rate in base_rates:
    if tested % 10000 == 0:
        print(f"Tested {tested:,} combinations... Best error so far: {best_error:.6f}")
    
    for receipt_factor in receipt_factors:
        for mile_factor in mile_factors:
            tested += 1
            
            max_error = test_formula_exact(base_rate, receipt_factor, mile_factor)
            
            if max_error < best_error:
                best_error = max_error
                best_formula = (base_rate, receipt_factor, mile_factor)
            
            if max_error < 0.01:  # Exact match!
                exact_matches.append((base_rate, receipt_factor, mile_factor, max_error))
                print(f"EXACT MATCH: base={base_rate:.1f}, receipt={receipt_factor:.2f}, mile={mile_factor:.2f}, error={max_error:.6f}")

print(f"\nCompleted brute force search!")
print(f"Total combinations tested: {tested:,}")

if exact_matches:
    print(f"\nFound {len(exact_matches)} exact matches:")
    for base_rate, receipt_factor, mile_factor, error in exact_matches:
        print(f"  Formula: {base_rate:.1f} * days + {receipt_factor:.2f} * receipts + {mile_factor:.2f} * miles")
        print(f"  Max error: {error:.6f}")
else:
    print(f"\nNo exact matches found.")
    print(f"Best formula: {best_formula[0]:.1f} * days + {best_formula[1]:.2f} * receipts + {best_formula[2]:.2f} * miles")
    print(f"Best max error: {best_error:.6f}")

# If no exact matches, maybe I need to consider different formulations
if not exact_matches:
    print(f"\n=== ALTERNATIVE FORMULATIONS ===")
    
    # Maybe it's not a simple linear combination
    # Let's try some mathematical transformations
    
    # Test: a * days + b * sqrt(receipts) + c * miles
    print("Testing with sqrt(receipts)...")
    df['sqrt_receipts'] = np.sqrt(df['receipts'])
    
    for base_rate in range(50, 201, 10):
        for receipt_factor in range(1, 101, 5):
            for mile_factor in range(1, 101, 5):
                predicted = base_rate * df['days'] + receipt_factor * df['sqrt_receipts'] + mile_factor * df['miles']
                max_error = abs(predicted - df['output']).max()
                
                if max_error < 1.0:
                    print(f"  {base_rate} * days + {receipt_factor} * sqrt(receipts) + {mile_factor} * miles -> error: {max_error:.3f}")
    
    # Test: a * days + b * log(receipts + 1) + c * miles
    print("Testing with log(receipts + 1)...")
    df['log_receipts'] = np.log(df['receipts'] + 1)
    
    for base_rate in range(50, 201, 10):
        for receipt_factor in range(1, 501, 25):
            for mile_factor in range(1, 101, 5):
                predicted = base_rate * df['days'] + receipt_factor * df['log_receipts'] + mile_factor * df['miles']
                max_error = abs(predicted - df['output']).max()
                
                if max_error < 1.0:
                    print(f"  {base_rate} * days + {receipt_factor} * log(receipts+1) + {mile_factor} * miles -> error: {max_error:.3f}")
    
    # Test: a * days^2 + b * receipts + c * miles
    print("Testing with days^2...")
    df['days_squared'] = df['days'] ** 2
    
    for base_rate in range(1, 51, 2):
        for receipt_factor in range(1, 101, 5):
            for mile_factor in range(1, 101, 5):
                predicted = base_rate * df['days_squared'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
                max_error = abs(predicted - df['output']).max()
                
                if max_error < 1.0:
                    print(f"  {base_rate} * days^2 + {receipt_factor} * receipts + {mile_factor} * miles -> error: {max_error:.3f}")

    # Test multiplicative: (a + b * receipts) * (c + d * days) + e * miles
    print("Testing multiplicative formulation...")
    
    for a in range(0, 101, 10):
        for b in range(1, 11, 1):
            for c in range(50, 151, 10):
                for d in range(0, 21, 5):
                    for e in range(0, 11, 1):
                        try:
                            predicted = (a + b * df['receipts']) * (c + d * df['days']) + e * df['miles']
                            max_error = abs(predicted - df['output']).max()
                            
                            if max_error < 1.0:
                                print(f"  ({a} + {b} * receipts) * ({c} + {d} * days) + {e} * miles -> error: {max_error:.3f}")
                        except:
                            continue

print("\nSaving brute force results...")
if exact_matches:
    # Use the first exact match
    base_rate, receipt_factor, mile_factor, _ = exact_matches[0]
    df['predicted_exact'] = base_rate * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
    df['error_exact'] = abs(df['predicted_exact'] - df['output'])
else:
    # Use the best approximation
    base_rate, receipt_factor, mile_factor = best_formula
    df['predicted_best'] = base_rate * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
    df['error_best'] = abs(df['predicted_best'] - df['output'])

df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/brute_force_results.csv', index=False)