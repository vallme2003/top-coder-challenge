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

print("=== FINAL EXACT DISCOVERY ATTEMPT ===")

# Since linear approaches aren't working, let me think about this differently
# Maybe the formula involves business logic with exact cutoffs, multipliers, or lookup tables

# Let me examine the data more carefully for exact patterns
print("Looking for exact mathematical relationships...")

# Check if there are cases where the output has exact relationships
def find_exact_multiples():
    print("Checking for exact multiples or simple relationships...")
    
    exact_found = []
    
    for i in range(min(100, len(df))):  # Check first 100 cases
        row = df.iloc[i]
        days, miles, receipts, output = row['days'], row['miles'], row['receipts'], row['output']
        
        # Test many possible exact formulas
        formulas_to_test = [
            ("100 * days + receipts", 100 * days + receipts),
            ("120 * days + receipts", 120 * days + receipts),
            ("days * (100 + receipts)", days * (100 + receipts)),
            ("days * (80 + receipts)", days * (80 + receipts)),
            ("days * 100 + receipts * 0.8", days * 100 + receipts * 0.8),
            ("days * 120 + receipts * 0.7", days * 120 + receipts * 0.7),
            ("receipts * 100 + days * 100", receipts * 100 + days * 100),
            ("(receipts + days) * 100", (receipts + days) * 100),
            ("receipts * (100 + days * 10)", receipts * (100 + days * 10)),
            ("receipts * (100 + miles * 0.1)", receipts * (100 + miles * 0.1)),
            ("100 * days + 0.5 * receipts + 0.6 * miles", 100 * days + 0.5 * receipts + 0.6 * miles),
            ("80 * days + 0.7 * receipts + 0.4 * miles", 80 * days + 0.7 * receipts + 0.4 * miles),
        ]
        
        for formula_name, predicted in formulas_to_test:
            if abs(predicted - output) < 0.01:
                exact_found.append((i, formula_name, predicted, output, days, miles, receipts))
                print(f"EXACT: Case {i+1}, {formula_name} = {predicted:.2f} vs actual {output:.2f}")
                print(f"       Days: {days}, Miles: {miles:.1f}, Receipts: ${receipts:.2f}")
    
    return exact_found

exact_matches = find_exact_multiples()

if exact_matches:
    print(f"\nFound {len(exact_matches)} exact matches!")
    # Test if any of these formulas work for all cases
    for i, (case_idx, formula_name, _, _, _, _, _) in enumerate(exact_matches):
        print(f"\nTesting formula: {formula_name}")
        
        # Extract the formula and test on all data
        if "100 * days + receipts" in formula_name:
            predicted_all = 100 * df['days'] + df['receipts']
        elif "120 * days + receipts" in formula_name:
            predicted_all = 120 * df['days'] + df['receipts']
        elif "days * (100 + receipts)" in formula_name:
            predicted_all = df['days'] * (100 + df['receipts'])
        elif "days * (80 + receipts)" in formula_name:
            predicted_all = df['days'] * (80 + df['receipts'])
        elif "days * 100 + receipts * 0.8" in formula_name:
            predicted_all = df['days'] * 100 + df['receipts'] * 0.8
        elif "days * 120 + receipts * 0.7" in formula_name:
            predicted_all = df['days'] * 120 + df['receipts'] * 0.7
        elif "receipts * 100 + days * 100" in formula_name:
            predicted_all = df['receipts'] * 100 + df['days'] * 100
        elif "(receipts + days) * 100" in formula_name:
            predicted_all = (df['receipts'] + df['days']) * 100
        elif "receipts * (100 + days * 10)" in formula_name:
            predicted_all = df['receipts'] * (100 + df['days'] * 10)
        elif "receipts * (100 + miles * 0.1)" in formula_name:
            predicted_all = df['receipts'] * (100 + df['miles'] * 0.1)
        elif "100 * days + 0.5 * receipts + 0.6 * miles" in formula_name:
            predicted_all = 100 * df['days'] + 0.5 * df['receipts'] + 0.6 * df['miles']
        elif "80 * days + 0.7 * receipts + 0.4 * miles" in formula_name:
            predicted_all = 80 * df['days'] + 0.7 * df['receipts'] + 0.4 * df['miles']
        else:
            continue
        
        errors = abs(predicted_all - df['output'])
        max_error = errors.max()
        perfect_count = (errors < 0.01).sum()
        
        print(f"  Applied to all cases: Max error {max_error:.6f}, Perfect matches: {perfect_count}")
        
        if max_error < 0.01:
            print(f"  *** EXACT FORMULA FOR ALL CASES: {formula_name} ***")

# Let me try a different approach - maybe there are lookup tables or piecewise functions
print(f"\n=== LOOKING FOR PIECEWISE OR LOOKUP PATTERNS ===")

# Maybe it's based on specific value ranges or combinations
def analyze_by_input_ranges():
    print("Analyzing patterns by input value ranges...")
    
    # Group by different characteristics and look for patterns
    
    # Group by days and see if there's a simple formula within each day group
    for days in sorted(df['days'].unique())[:7]:  # First 7 day values
        day_data = df[df['days'] == days].head(10)  # First 10 cases for each day
        
        print(f"\n{days}-day trips (first 10):")
        
        for _, row in day_data.iterrows():
            miles, receipts, output = row['miles'], row['receipts'], row['output']
            
            # Test simple patterns for this day length
            test_formulas = [
                f"{receipts:.2f} * 100 = {receipts * 100:.2f}",
                f"{receipts:.2f} * 120 = {receipts * 120:.2f}",
                f"{receipts:.2f} * 80 = {receipts * 80:.2f}",
                f"100 * {days} + {receipts:.2f} = {100 * days + receipts:.2f}",
                f"120 * {days} + {receipts:.2f} = {120 * days + receipts:.2f}",
            ]
            
            print(f"  Miles: {miles:6.1f}, Receipts: ${receipts:7.2f}, Output: ${output:8.2f}")
            
            for formula in test_formulas:
                predicted_val = float(formula.split(' = ')[1])
                if abs(predicted_val - output) < 0.01:
                    print(f"    MATCH: {formula}")

analyze_by_input_ranges()

# One more approach - maybe I'm missing a simple transformation
print(f"\n=== TESTING SIMPLE BUSINESS FORMULAS ===")

# Common business formulas that might apply
business_formulas = [
    # Base per day + receipt percentage + mileage
    ("100 * days + 0.8 * receipts + 0.56 * miles", 100, 0.8, 0.56),
    ("120 * days + 0.8 * receipts + 0.5 * miles", 120, 0.8, 0.5),
    ("100 * days + 0.75 * receipts + 0.6 * miles", 100, 0.75, 0.6),
    ("80 * days + 1.0 * receipts + 0.5 * miles", 80, 1.0, 0.5),
    
    # Exact business rates
    ("100 * days + receipts + 0.56 * miles", 100, 1.0, 0.56),
    ("125 * days + 0.8 * receipts + 0.5 * miles", 125, 0.8, 0.5),
]

for formula_name, day_rate, receipt_rate, mile_rate in business_formulas:
    predicted = day_rate * df['days'] + receipt_rate * df['receipts'] + mile_rate * df['miles']
    errors = abs(predicted - df['output'])
    max_error = errors.max()
    perfect_count = (errors < 0.01).sum()
    
    print(f"{formula_name}:")
    print(f"  Max error: {max_error:.6f}, Perfect matches: {perfect_count}")
    
    if max_error < 0.01:
        print(f"  *** EXACT BUSINESS FORMULA FOUND! ***")

# Last attempt - maybe there's an exact formula with specific decimal places
print(f"\n=== HIGH-PRECISION COEFFICIENT SEARCH ===")

# Use the least squares result as a starting point and search around it with high precision
ls_days = 62.839410
ls_receipts = 0.436038
ls_miles = 0.579790

print(f"Searching around least squares solution with high precision...")

best_error = float('inf')
best_formula = None

# Search in a small range around the least squares solution
for days_coeff in np.arange(ls_days - 5, ls_days + 6, 0.1):
    for receipts_coeff in np.arange(ls_receipts - 0.1, ls_receipts + 0.11, 0.01):
        for miles_coeff in np.arange(ls_miles - 0.1, ls_miles + 0.11, 0.01):
            predicted = days_coeff * df['days'] + receipts_coeff * df['receipts'] + miles_coeff * df['miles']
            max_error = abs(predicted - df['output']).max()
            
            if max_error < best_error:
                best_error = max_error
                best_formula = (days_coeff, receipts_coeff, miles_coeff)
            
            if max_error < 0.01:
                print(f"EXACT: {days_coeff:.1f} * days + {receipts_coeff:.2f} * receipts + {miles_coeff:.2f} * miles")
                print(f"Max error: {max_error:.6f}")

print(f"\nBest formula found in precision search:")
if best_formula:
    days_c, receipts_c, miles_c = best_formula
    print(f"Formula: {days_c:.3f} * days + {receipts_c:.3f} * receipts + {miles_c:.3f} * miles")
    print(f"Max error: {best_error:.6f}")
    
    if best_error < 0.01:
        print(f"\n*** EXACT ANALYTICAL FORMULA DISCOVERED! ***")
        
        # Save the exact formula
        df['predicted_exact'] = days_c * df['days'] + receipts_c * df['receipts'] + miles_c * df['miles']
        df['error_exact'] = abs(df['predicted_exact'] - df['output'])
        
        print(f"FINAL EXACT FORMULA:")
        print(f"{days_c:.6f} * trip_duration_days + {receipts_c:.6f} * total_receipts_amount + {miles_c:.6f} * miles_traveled")

print("\nSaving final discovery results...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/final_discovery_results.csv', index=False)