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

print("=== ANALYZING HIGH-ERROR CASES ===")

# Current formula
days_coefficient = 62.839410
receipts_coefficient = 0.436038
miles_coefficient = 0.579790

df['predicted'] = days_coefficient * df['days'] + receipts_coefficient * df['receipts'] + miles_coefficient * df['miles']
df['error'] = abs(df['predicted'] - df['output'])

# Find the worst cases
worst_cases = df.nlargest(10, 'error')

print("Top 10 worst predictions:")
for _, row in worst_cases.iterrows():
    print(f"Days: {row['days']:2.0f}, Miles: {row['miles']:6.1f}, Receipts: ${row['receipts']:7.2f}")
    print(f"  Expected: ${row['output']:7.2f}, Predicted: ${row['predicted']:7.2f}, Error: ${row['error']:7.2f}")
    
    # Calculate what coefficients would work for this case
    # If we fix two coefficients and solve for the third
    residual_after_days = row['output'] - days_coefficient * row['days']
    residual_after_receipts = row['output'] - receipts_coefficient * row['receipts']
    residual_after_miles = row['output'] - miles_coefficient * row['miles']
    
    if row['receipts'] > 0 and row['miles'] > 0:
        needed_receipt_coeff = residual_after_days / row['receipts'] - miles_coefficient * row['miles'] / row['receipts']
        needed_mile_coeff = residual_after_days / row['miles'] - receipts_coefficient * row['receipts'] / row['miles']
        
        print(f"  To fix: need receipt_coeff={needed_receipt_coeff:.3f} or mile_coeff={needed_mile_coeff:.3f}")
    print()

# Look for patterns in the errors
print("=== ERROR PATTERN ANALYSIS ===")

# Check if errors correlate with input variables
print(f"Error correlations:")
print(f"  Days: {df['error'].corr(df['days']):.3f}")
print(f"  Miles: {df['error'].corr(df['miles']):.3f}")
print(f"  Receipts: {df['error'].corr(df['receipts']):.3f}")

# Check if there are threshold effects causing large errors
print(f"\nError by trip length:")
for days in sorted(df['days'].unique()):
    day_data = df[df['days'] == days]
    if len(day_data) >= 5:
        print(f"  {days:2.0f} days: avg error {day_data['error'].mean():6.2f}, max error {day_data['error'].max():6.2f}")

print(f"\nError by receipt amount ranges:")
receipt_ranges = [(0, 100), (100, 500), (500, 1000), (1000, 2000), (2000, 3000)]
for low, high in receipt_ranges:
    range_data = df[(df['receipts'] >= low) & (df['receipts'] < high)]
    if len(range_data) > 0:
        print(f"  ${low}-${high}: {len(range_data):3d} cases, avg error {range_data['error'].mean():6.2f}, max error {range_data['error'].max():6.2f}")

print(f"\nError by mileage ranges:")
mile_ranges = [(0, 100), (100, 300), (300, 600), (600, 1000), (1000, 2000)]
for low, high in mile_ranges:
    range_data = df[(df['miles'] >= low) & (df['miles'] < high)]
    if len(range_data) > 0:
        print(f"  {low}-{high} miles: {len(range_data):3d} cases, avg error {range_data['error'].mean():6.2f}, max error {range_data['error'].max():6.2f}")

# Check for the interview insights - do high receipt cases get penalized?
print(f"\n=== TESTING INTERVIEW INSIGHTS ===")

# High spending penalty
high_spending = df[df['receipts'] > 1500]
low_spending = df[df['receipts'] <= 1500]

print(f"High spending (>$1500): {len(high_spending)} cases")
print(f"  Avg actual output: ${high_spending['output'].mean():.2f}")
print(f"  Avg predicted: ${high_spending['predicted'].mean():.2f}")
print(f"  Avg error: ${high_spending['error'].mean():.2f}")

print(f"Low spending (≤$1500): {len(low_spending)} cases")
print(f"  Avg actual output: ${low_spending['output'].mean():.2f}")
print(f"  Avg predicted: ${low_spending['predicted'].mean():.2f}")
print(f"  Avg error: ${low_spending['error'].mean():.2f}")

# The linear model seems to overestimate high-spending cases
# Maybe there's a cap or penalty for high receipts

print(f"\n=== TESTING RECEIPT PENALTY HYPOTHESIS ===")

# Test if there's a cap on receipt reimbursement
for cap in [800, 1000, 1200, 1500, 2000]:
    df[f'capped_receipts_{cap}'] = np.minimum(df['receipts'], cap)
    
    # Re-fit with capped receipts
    X = df[['days', f'capped_receipts_{cap}', 'miles']].values
    y = df['output'].values
    
    coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
    predicted_capped = X @ coeffs
    errors_capped = abs(predicted_capped - y)
    
    print(f"Receipt cap at ${cap}:")
    print(f"  Coefficients: days={coeffs[0]:.3f}, receipts={coeffs[1]:.3f}, miles={coeffs[2]:.3f}")
    print(f"  Max error: {errors_capped.max():.2f}, Mean error: {errors_capped.mean():.2f}")
    print(f"  Perfect matches: {(errors_capped < 0.01).sum()}")

# Test diminishing returns for receipts
print(f"\n=== TESTING DIMINISHING RETURNS ===")

# Test sqrt(receipts) 
df['sqrt_receipts'] = np.sqrt(df['receipts'])
X_sqrt = df[['days', 'sqrt_receipts', 'miles']].values
coeffs_sqrt = np.linalg.lstsq(X_sqrt, df['output'].values, rcond=None)[0]
predicted_sqrt = X_sqrt @ coeffs_sqrt
errors_sqrt = abs(predicted_sqrt - df['output'])

print(f"Using sqrt(receipts):")
print(f"  Coefficients: days={coeffs_sqrt[0]:.3f}, sqrt_receipts={coeffs_sqrt[1]:.3f}, miles={coeffs_sqrt[2]:.3f}")
print(f"  Max error: {errors_sqrt.max():.2f}, Mean error: {errors_sqrt.mean():.2f}")
print(f"  Perfect matches: {(errors_sqrt < 0.01).sum()}")

# Test log(receipts + 1)
df['log_receipts'] = np.log(df['receipts'] + 1)
X_log = df[['days', 'log_receipts', 'miles']].values
coeffs_log = np.linalg.lstsq(X_log, df['output'].values, rcond=None)[0]
predicted_log = X_log @ coeffs_log
errors_log = abs(predicted_log - df['output'])

print(f"Using log(receipts + 1):")
print(f"  Coefficients: days={coeffs_log[0]:.3f}, log_receipts={coeffs_log[1]:.3f}, miles={coeffs_log[2]:.3f}")
print(f"  Max error: {errors_log.max():.2f}, Mean error: {errors_log.mean():.2f}")
print(f"  Perfect matches: {(errors_log < 0.01).sum()}")

# Find the best approach
approaches = [
    ("Linear", df['error'], "Original linear"),
    ("Capped 1000", errors_capped, "Receipts capped at $1000"),
    ("Sqrt receipts", errors_sqrt, "Square root of receipts"),
    ("Log receipts", errors_log, "Log of receipts"),
]

approaches.sort(key=lambda x: x[1].max())

print(f"\n=== BEST APPROACH ===")
best_name, best_errors, best_desc = approaches[0]
print(f"Best approach: {best_name}")
print(f"Description: {best_desc}")
print(f"Max error: {best_errors.max():.6f}")
print(f"Mean error: {best_errors.mean():.6f}")
print(f"Perfect matches: {(best_errors < 0.01).sum()}")

if best_errors.max() < 0.01:
    print(f"\n*** EXACT FORMULA FOUND! ***")

print("\nSaving failure analysis...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/failure_analysis.csv', index=False)