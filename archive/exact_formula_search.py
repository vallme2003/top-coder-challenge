#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd

# Load the data
with open('/Users/vthenappan/Documents/GitHub/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame([{
    'days': case['input']['trip_duration_days'],
    'miles': case['input']['miles_traveled'], 
    'receipts': case['input']['total_receipts_amount'],
    'output': case['expected_output']
} for case in data])

print("=== EXACT FORMULA SEARCH ===")

# From the linear fit analysis, I see patterns around:
# - Receipt coefficient around 0.4-0.5
# - Mile coefficient around 0.3-0.7  
# - Base term that increases with days

# Let me test if there's a universal formula of the form:
# output = base_per_day * days + receipt_factor * receipts + mile_factor * miles

def test_exact_formula():
    best_error = float('inf')
    best_params = None
    
    # Test with high precision around the patterns I observed
    receipt_factors = np.arange(0.3, 0.6, 0.001)
    mile_factors = np.arange(0.2, 0.8, 0.001)
    base_rates = np.arange(80, 200, 0.1)
    
    print("Testing high-precision formula: base_rate * days + receipt_factor * receipts + mile_factor * miles")
    print("This will take a moment...")
    
    total_tests = 0
    for i, base_rate in enumerate(base_rates):
        if i % 50 == 0:
            print(f"Testing base rate {base_rate:.1f}...")
            
        for receipt_factor in receipt_factors:
            for mile_factor in mile_factors:
                predicted = base_rate * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
                max_error = abs(predicted - df['output']).max()
                
                total_tests += 1
                
                if max_error < best_error:
                    best_error = max_error
                    best_params = (base_rate, receipt_factor, mile_factor)
                
                if max_error < 0.01:  # Perfect or near-perfect match
                    print(f"EXCELLENT MATCH: base={base_rate:.3f}, receipt_factor={receipt_factor:.3f}, mile_factor={mile_factor:.3f}")
                    print(f"Max error: {max_error:.6f}")
                    return base_rate, receipt_factor, mile_factor
    
    print(f"Tested {total_tests} combinations")
    print(f"Best found: base={best_params[0]:.3f}, receipt_factor={best_params[1]:.3f}, mile_factor={best_params[2]:.3f}")
    print(f"Best max error: {best_error:.6f}")
    return best_params

# Run the search
best_params = test_exact_formula()

if best_params:
    base_rate, receipt_factor, mile_factor = best_params
    
    # Test this formula on all data
    df['predicted'] = base_rate * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
    df['error'] = abs(df['predicted'] - df['output'])
    
    print(f"\n=== TESTING BEST FORMULA ===")
    print(f"Formula: {base_rate:.3f} * days + {receipt_factor:.3f} * receipts + {mile_factor:.3f} * miles")
    print(f"Max error: {df['error'].max():.6f}")
    print(f"Mean error: {df['error'].mean():.6f}")
    print(f"Number of perfect matches (error < 0.01): {(df['error'] < 0.01).sum()}")
    
    # Show some examples
    print(f"\nFirst 10 predictions vs actual:")
    for i in range(10):
        row = df.iloc[i]
        print(f"Days: {row['days']}, Miles: {row['miles']:.1f}, Receipts: ${row['receipts']:.2f}")
        print(f"  Predicted: ${row['predicted']:.2f}, Actual: ${row['output']:.2f}, Error: {row['error']:.3f}")
    
    # Check if this is the exact formula
    if df['error'].max() < 0.01:
        print("\n*** EXACT FORMULA FOUND! ***")
        print(f"Formula: {base_rate:.3f} * trip_duration_days + {receipt_factor:.3f} * total_receipts_amount + {mile_factor:.3f} * miles_traveled")
    else:
        print(f"\nClose but not exact. Max error: {df['error'].max():.6f}")

# Let's also try some business-logical rounded values
print(f"\n=== TESTING ROUNDED BUSINESS VALUES ===")

business_values = [
    (100, 0.5, 0.5),    # Nice round numbers
    (120, 0.4, 0.6),    
    (125, 0.4, 0.5),
    (100, 0.45, 0.55),
    (110, 0.45, 0.5),
    (100, 0.47, 0.4),
    (115, 0.41, 0.47),
]

for base_rate, receipt_factor, mile_factor in business_values:
    predicted = base_rate * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
    max_error = abs(predicted - df['output']).max()
    mean_error = abs(predicted - df['output']).mean()
    
    print(f"Base: {base_rate}, Receipt: {receipt_factor}, Mile: {mile_factor}")
    print(f"  Max error: {max_error:.3f}, Mean error: {mean_error:.3f}")
    
    if max_error < 0.01:
        print(f"  *** EXACT MATCH with business values! ***")

# Let's also search for integer values that might be the exact formula
print(f"\n=== TESTING INTEGER COEFFICIENTS ===")

for base_rate in range(100, 151):
    for receipt_factor_int in range(40, 51):  # 0.40 to 0.50 as integers * 100
        for mile_factor_int in range(30, 71):  # 0.30 to 0.70 as integers * 100
            receipt_factor = receipt_factor_int / 100.0
            mile_factor = mile_factor_int / 100.0
            
            predicted = base_rate * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
            max_error = abs(predicted - df['output']).max()
            
            if max_error < 0.01:
                print(f"EXACT INTEGER MATCH: base={base_rate}, receipt_factor={receipt_factor:.2f}, mile_factor={mile_factor:.2f}")
                print(f"Max error: {max_error:.6f}")

print("\nSaving exact formula search results...")
if 'predicted' in df.columns:
    df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/exact_formula_results.csv', index=False)