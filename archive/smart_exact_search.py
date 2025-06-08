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

print("=== SMART EXACT SEARCH ===")

# Instead of brute force, let me use mathematical insights
# Since there IS an exact formula, let me try to deduce it more intelligently

# First, let me look at the simplest cases to understand the pattern
print("Analyzing simplest cases to deduce the exact formula...")

# Sort by total complexity (sum of inputs) to find the simplest cases
df['complexity'] = df['days'] + df['miles'] + df['receipts']
simple_cases = df.nsmallest(20, 'complexity')

print("20 simplest cases (lowest complexity):")
for _, row in simple_cases.iterrows():
    days, miles, receipts, output = row['days'], row['miles'], row['receipts'], row['output']
    print(f"Days: {days:2.0f}, Miles: {miles:6.1f}, Receipts: ${receipts:7.2f} -> ${output:8.2f}")

# Let me try to solve for the formula using the simplest cases
# If formula is: output = a * days + b * receipts + c * miles
# Then I can set up a system of equations

print(f"\n=== SOLVING SYSTEM OF EQUATIONS ===")

# Take the first 3 simple cases and solve exactly
case1 = simple_cases.iloc[0]
case2 = simple_cases.iloc[1] 
case3 = simple_cases.iloc[2]

print(f"Using these 3 cases to solve for exact coefficients:")
print(f"Case 1: {case1['days']} * a + {case1['receipts']:.2f} * b + {case1['miles']:.1f} * c = {case1['output']:.2f}")
print(f"Case 2: {case2['days']} * a + {case2['receipts']:.2f} * b + {case2['miles']:.1f} * c = {case2['output']:.2f}")
print(f"Case 3: {case3['days']} * a + {case3['receipts']:.2f} * b + {case3['miles']:.1f} * c = {case3['output']:.2f}")

# Set up matrix equation: A * x = b
A = np.array([
    [case1['days'], case1['receipts'], case1['miles']],
    [case2['days'], case2['receipts'], case2['miles']],
    [case3['days'], case3['receipts'], case3['miles']]
])

b = np.array([case1['output'], case2['output'], case3['output']])

try:
    # Solve for coefficients
    coeffs = np.linalg.solve(A, b)
    
    print(f"\nSolved coefficients:")
    print(f"  Days coefficient (a): {coeffs[0]:.6f}")
    print(f"  Receipts coefficient (b): {coeffs[1]:.6f}")
    print(f"  Miles coefficient (c): {coeffs[2]:.6f}")
    
    # Test this formula on all data
    predicted = coeffs[0] * df['days'] + coeffs[1] * df['receipts'] + coeffs[2] * df['miles']
    errors = abs(predicted - df['output'])
    max_error = errors.max()
    mean_error = errors.mean()
    
    print(f"\nTesting on all 1000 cases:")
    print(f"  Max error: {max_error:.6f}")
    print(f"  Mean error: {mean_error:.6f}")
    print(f"  Perfect matches (error < 0.01): {(errors < 0.01).sum()}")
    
    if max_error < 0.01:
        print(f"\n*** EXACT FORMULA FOUND! ***")
        print(f"Formula: {coeffs[0]:.6f} * days + {coeffs[1]:.6f} * receipts + {coeffs[2]:.6f} * miles")
    else:
        print(f"Formula from 3 cases doesn't generalize perfectly.")
        
except np.linalg.LinAlgError:
    print("Cannot solve - matrix is singular")

# Let me try a different approach - use least squares on more cases
print(f"\n=== LEAST SQUARES APPROACH ===")

# Use more cases for better stability
X = df[['days', 'receipts', 'miles']].values
y = df['output'].values

# Solve least squares
coeffs_ls = np.linalg.lstsq(X, y, rcond=None)[0]

print(f"Least squares coefficients:")
print(f"  Days coefficient: {coeffs_ls[0]:.6f}")
print(f"  Receipts coefficient: {coeffs_ls[1]:.6f}")
print(f"  Miles coefficient: {coeffs_ls[2]:.6f}")

# Test this formula
predicted_ls = X @ coeffs_ls
errors_ls = abs(predicted_ls - y)
max_error_ls = errors_ls.max()
mean_error_ls = errors_ls.mean()

print(f"\nLeast squares results:")
print(f"  Max error: {max_error_ls:.6f}")
print(f"  Mean error: {mean_error_ls:.6f}")
print(f"  Perfect matches (error < 0.01): {(errors_ls < 0.01).sum()}")

if max_error_ls < 0.01:
    print(f"\n*** EXACT FORMULA FOUND WITH LEAST SQUARES! ***")
    print(f"Formula: {coeffs_ls[0]:.6f} * days + {coeffs_ls[1]:.6f} * receipts + {coeffs_ls[2]:.6f} * miles")

# Maybe the formula has integer or simple fractional coefficients
print(f"\n=== TESTING INTEGER/SIMPLE COEFFICIENTS ===")

# Round the least squares coefficients to simple values and test
def round_to_simple(val):
    """Round to simple fractions or integers"""
    # Test common fractions
    simple_values = [0, 0.1, 0.2, 0.25, 0.3, 0.33, 0.4, 0.5, 0.6, 0.67, 0.7, 0.75, 0.8, 0.9, 1.0]
    simple_values += list(range(1, 201))  # integers 1-200
    
    return min(simple_values, key=lambda x: abs(x - val))

days_coeff_simple = round_to_simple(coeffs_ls[0])
receipts_coeff_simple = round_to_simple(coeffs_ls[1])
miles_coeff_simple = round_to_simple(coeffs_ls[2])

print(f"Rounded to simple values:")
print(f"  Days: {coeffs_ls[0]:.6f} -> {days_coeff_simple}")
print(f"  Receipts: {coeffs_ls[1]:.6f} -> {receipts_coeff_simple}")
print(f"  Miles: {coeffs_ls[2]:.6f} -> {miles_coeff_simple}")

# Test the simple coefficients
predicted_simple = days_coeff_simple * df['days'] + receipts_coeff_simple * df['receipts'] + miles_coeff_simple * df['miles']
errors_simple = abs(predicted_simple - df['output'])
max_error_simple = errors_simple.max()
mean_error_simple = errors_simple.mean()

print(f"\nSimple coefficients results:")
print(f"  Max error: {max_error_simple:.6f}")
print(f"  Mean error: {mean_error_simple:.6f}")
print(f"  Perfect matches (error < 0.01): {(errors_simple < 0.01).sum()}")

if max_error_simple < 0.01:
    print(f"\n*** EXACT FORMULA WITH SIMPLE COEFFICIENTS! ***")
    print(f"Formula: {days_coeff_simple} * days + {receipts_coeff_simple} * receipts + {miles_coeff_simple} * miles")

# Let me also test if there's a constant term
print(f"\n=== TESTING WITH CONSTANT TERM ===")

# Add constant term: output = a * days + b * receipts + c * miles + d
X_with_const = np.column_stack([X, np.ones(len(X))])
coeffs_const = np.linalg.lstsq(X_with_const, y, rcond=None)[0]

print(f"With constant term:")
print(f"  Days coefficient: {coeffs_const[0]:.6f}")
print(f"  Receipts coefficient: {coeffs_const[1]:.6f}")
print(f"  Miles coefficient: {coeffs_const[2]:.6f}")
print(f"  Constant term: {coeffs_const[3]:.6f}")

predicted_const = X_with_const @ coeffs_const
errors_const = abs(predicted_const - y)
max_error_const = errors_const.max()

print(f"  Max error: {max_error_const:.6f}")

if max_error_const < 0.01:
    print(f"\n*** EXACT FORMULA WITH CONSTANT TERM! ***")
    print(f"Formula: {coeffs_const[0]:.6f} * days + {coeffs_const[1]:.6f} * receipts + {coeffs_const[2]:.6f} * miles + {coeffs_const[3]:.6f}")

# Show the best formula found
best_formulas = [
    ("Least Squares", coeffs_ls, max_error_ls),
    ("Simple Coefficients", [days_coeff_simple, receipts_coeff_simple, miles_coeff_simple], max_error_simple),
    ("With Constant", coeffs_const, max_error_const)
]

best_formulas.sort(key=lambda x: x[2])  # Sort by error

print(f"\n=== BEST FORMULA FOUND ===")
best_name, best_coeffs, best_error = best_formulas[0]
print(f"Method: {best_name}")
print(f"Max error: {best_error:.6f}")

if len(best_coeffs) == 3:
    print(f"Formula: {best_coeffs[0]:.6f} * days + {best_coeffs[1]:.6f} * receipts + {best_coeffs[2]:.6f} * miles")
else:
    print(f"Formula: {best_coeffs[0]:.6f} * days + {best_coeffs[1]:.6f} * receipts + {best_coeffs[2]:.6f} * miles + {best_coeffs[3]:.6f}")

if best_error < 0.01:
    print(f"\n*** EXACT ANALYTICAL FORMULA DISCOVERED! ***")

print("\nSaving smart search results...")
df['predicted_best'] = predicted_ls
df['error_best'] = errors_ls
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/smart_search_results.csv', index=False)