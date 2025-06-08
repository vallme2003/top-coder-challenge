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

print("=== TARGETED FORMULA SEARCH ===")

# From the pattern analysis, I saw that the linear fit coefficients were fairly consistent:
# - Receipt factor around 0.41-0.49
# - Mile factor around 0.25-0.68  
# - Base increases with days (around 100-150 per day)

# Let me be more strategic and test key values
def test_targeted_formulas():
    # Test specific combinations that seem promising
    candidates = []
    
    # Based on the linear regression results, test around these values
    base_candidates = [100, 110, 115, 120, 125, 130]
    receipt_candidates = [0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49]
    mile_candidates = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
    
    print("Testing targeted combinations...")
    
    for base in base_candidates:
        for receipt_factor in receipt_candidates:
            for mile_factor in mile_candidates:
                predicted = base * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
                max_error = abs(predicted - df['output']).max()
                mean_error = abs(predicted - df['output']).mean()
                
                candidates.append((base, receipt_factor, mile_factor, max_error, mean_error))
                
                if max_error < 1.0:  # Very good match
                    print(f"Good match: base={base}, receipt={receipt_factor:.2f}, mile={mile_factor:.2f}")
                    print(f"  Max error: {max_error:.3f}, Mean error: {mean_error:.3f}")
    
    # Sort by max error
    candidates.sort(key=lambda x: x[3])
    
    print(f"\nTop 10 best formulas:")
    for i, (base, receipt_factor, mile_factor, max_error, mean_error) in enumerate(candidates[:10]):
        print(f"{i+1}. Base: {base}, Receipt: {receipt_factor:.2f}, Mile: {mile_factor:.2f}")
        print(f"   Max error: {max_error:.3f}, Mean error: {mean_error:.3f}")
    
    return candidates[0]  # Return the best one

best_formula = test_targeted_formulas()

# Test the best formula found
base, receipt_factor, mile_factor, max_error, mean_error = best_formula
print(f"\n=== TESTING BEST FORMULA ===")
print(f"Formula: {base} * days + {receipt_factor:.3f} * receipts + {mile_factor:.3f} * miles")

df['predicted'] = base * df['days'] + receipt_factor * df['receipts'] + mile_factor * df['miles']
df['error'] = abs(df['predicted'] - df['output'])

print(f"Max error: {df['error'].max():.6f}")
print(f"Mean error: {df['error'].mean():.6f}")
print(f"Std error: {df['error'].std():.6f}")
print(f"Cases with error < 0.1: {(df['error'] < 0.1).sum()}")
print(f"Cases with error < 0.01: {(df['error'] < 0.01).sum()}")

# Show examples of best and worst predictions
print(f"\nBest predictions (lowest errors):")
best_predictions = df.nsmallest(5, 'error')
for _, row in best_predictions.iterrows():
    print(f"Days: {row['days']}, Miles: {row['miles']:.1f}, Receipts: ${row['receipts']:.2f}")
    print(f"  Predicted: ${row['predicted']:.2f}, Actual: ${row['output']:.2f}, Error: {row['error']:.6f}")

print(f"\nWorst predictions (highest errors):")
worst_predictions = df.nlargest(5, 'error')
for _, row in worst_predictions.iterrows():
    print(f"Days: {row['days']}, Miles: {row['miles']:.1f}, Receipts: ${row['receipts']:.2f}")
    print(f"  Predicted: ${row['predicted']:.2f}, Actual: ${row['output']:.2f}, Error: {row['error']:.6f}")

# Let's also test if there might be a different approach - maybe the formula isn't linear
print(f"\n=== TESTING NON-LINEAR PATTERNS ===")

# Check if there are threshold effects or piecewise functions
def analyze_residuals():
    df['residual'] = df['output'] - df['predicted']
    
    print(f"Residual analysis:")
    print(f"Residual mean: {df['residual'].mean():.6f}")
    print(f"Residual std: {df['residual'].std():.6f}")
    
    # Check if residuals correlate with any input variables
    print(f"Residual correlations:")
    print(f"  With days: {df['residual'].corr(df['days']):.6f}")
    print(f"  With miles: {df['residual'].corr(df['miles']):.6f}")
    print(f"  With receipts: {df['residual'].corr(df['receipts']):.6f}")
    
    # Check for patterns in residuals by trip length
    print(f"\nResidual patterns by trip length:")
    for days in sorted(df['days'].unique()):
        day_residuals = df[df['days'] == days]['residual']
        if len(day_residuals) > 5:
            print(f"  {days} days: mean residual {day_residuals.mean():.3f}, std {day_residuals.std():.3f}")

analyze_residuals()

# Let me try a slightly different approach - maybe there are integer coefficients
print(f"\n=== TESTING PRECISE INTEGER-LIKE VALUES ===")

# Test variations around the best formula with more precision
base_best = base
receipt_best = receipt_factor
mile_best = mile_factor

# Test small variations
for base_adj in [-2, -1, 0, 1, 2]:
    for receipt_adj in [-0.01, -0.005, 0, 0.005, 0.01]:
        for mile_adj in [-0.01, -0.005, 0, 0.005, 0.01]:
            test_base = base_best + base_adj
            test_receipt = receipt_best + receipt_adj
            test_mile = mile_best + mile_adj
            
            predicted = test_base * df['days'] + test_receipt * df['receipts'] + test_mile * df['miles']
            max_error = abs(predicted - df['output']).max()
            
            if max_error < 0.1:  # Very precise match
                print(f"Precise match: base={test_base}, receipt={test_receipt:.3f}, mile={test_mile:.3f}")
                print(f"  Max error: {max_error:.6f}")

print("\nSaving targeted search results...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/targeted_search_results.csv', index=False)