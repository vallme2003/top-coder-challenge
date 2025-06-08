#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd
from collections import defaultdict

# Load the data
with open('/Users/vthenappan/Documents/GitHub/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame([{
    'days': case['input']['trip_duration_days'],
    'miles': case['input']['miles_traveled'], 
    'receipts': case['input']['total_receipts_amount'],
    'output': case['expected_output']
} for case in data])

print("=== PATTERN DISCOVERY ANALYSIS ===")

# Let's look at the exact patterns by examining specific relationships
# Since receipts have the highest correlation, let's see if there are multipliers

print("Analyzing individual cases for patterns...")

# Look for cases where we can deduce the exact formula
def analyze_patterns():
    # Group by similar characteristics to find patterns
    patterns = []
    
    # Sort by receipts to see if there's a clear pattern
    df_sorted = df.sort_values('receipts')
    
    print("First 20 cases sorted by receipts:")
    for i, (_, row) in enumerate(df_sorted.head(20).iterrows()):
        ratio = row['output'] / row['receipts'] if row['receipts'] > 0 else 0
        print(f"Receipts: ${row['receipts']:.2f}, Output: ${row['output']:.2f}, Ratio: {ratio:.2f}, Days: {row['days']}, Miles: {row['miles']:.1f}")
    
    print("\nLast 20 cases sorted by receipts:")
    for i, (_, row) in enumerate(df_sorted.tail(20).iterrows()):
        ratio = row['output'] / row['receipts'] if row['receipts'] > 0 else 0
        print(f"Receipts: ${row['receipts']:.2f}, Output: ${row['output']:.2f}, Ratio: {ratio:.2f}, Days: {row['days']}, Miles: {row['miles']:.1f}")

analyze_patterns()

# Let's try a different approach - maybe the formula is multiplicative rather than additive
print("\n=== TESTING MULTIPLICATIVE FORMULAS ===")

# Test: output = (base + factor1 * receipts) * (1 + factor2 * miles/100) * days
def test_multiplicative():
    best_error = float('inf')
    best_params = None
    
    for base in range(50, 201, 10):
        for factor1 in range(1, 21, 2):
            for factor2 in np.arange(0.1, 2.1, 0.1):
                predicted = (base + factor1 * df['receipts']) * (1 + factor2 * df['miles']/100) * df['days']
                max_error = abs(predicted - df['output']).max()
                
                if max_error < best_error:
                    best_error = max_error
                    best_params = (base, factor1, factor2)
                
                if max_error < 1.0:  # Very close match
                    print(f"Close match: base={base}, factor1={factor1}, factor2={factor2:.1f}, max_error={max_error:.3f}")
    
    print(f"Best multiplicative: base={best_params[0]}, factor1={best_params[1]}, factor2={best_params[2]:.1f}, max_error={best_error:.3f}")

test_multiplicative()

# Let's look at the business logic more carefully
# From interviews: there are thresholds, tiers, bonuses
print("\n=== TESTING BUSINESS LOGIC PATTERNS ===")

# Maybe there's a formula that depends on ranges/tiers
def analyze_by_ranges():
    # Look at different day ranges
    print("Analysis by trip duration:")
    for days in sorted(df['days'].unique()):
        day_data = df[df['days'] == days]
        if len(day_data) >= 3:  # Only analyze if we have enough data
            print(f"\n{days} day trips ({len(day_data)} cases):")
            
            # Look for patterns within this day range
            correlations = {}
            correlations['miles'] = day_data['miles'].corr(day_data['output'])
            correlations['receipts'] = day_data['receipts'].corr(day_data['output'])
            correlations['miles_receipts'] = (day_data['miles'] * day_data['receipts']).corr(day_data['output'])
            
            print(f"  Correlations - Miles: {correlations['miles']:.3f}, Receipts: {correlations['receipts']:.3f}, Miles*Receipts: {correlations['miles_receipts']:.3f}")
            
            # Try to find a simple formula for this day range
            # Test: output = a * receipts + b * miles + c
            if len(day_data) >= 3:
                X = day_data[['receipts', 'miles']].values
                X = np.column_stack([X, np.ones(len(X))])  # Add constant term
                y = day_data['output'].values
                
                try:
                    # Solve linear system
                    coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
                    predicted = X @ coeffs
                    max_error = abs(predicted - y).max()
                    mean_error = abs(predicted - y).mean()
                    
                    print(f"  Linear fit: {coeffs[0]:.3f}*receipts + {coeffs[1]:.3f}*miles + {coeffs[2]:.3f}")
                    print(f"  Max error: {max_error:.3f}, Mean error: {mean_error:.3f}")
                    
                    if max_error < 0.1:  # Very good fit
                        print(f"  *** EXCELLENT FIT for {days} days! ***")
                
                except:
                    print("  Could not fit linear model")

analyze_by_ranges()

# Let's try a different approach - look for exact mathematical relationships
print("\n=== LOOKING FOR EXACT MATHEMATICAL RELATIONSHIPS ===")

# Let's see if there are any cases with integer or simple fractional relationships
def find_exact_relationships():
    print("Looking for exact integer/fractional relationships...")
    
    for i, row in df.head(50).iterrows():  # Check first 50 cases
        days, miles, receipts, output = row['days'], row['miles'], row['receipts'], row['output']
        
        # Test various exact formulas
        tests = [
            ('receipts * 100 + days * 100', receipts * 100 + days * 100),
            ('receipts * days * 100', receipts * days * 100),
            ('(receipts + days) * 100', (receipts + days) * 100),
            ('receipts * 120 + days * 80', receipts * 120 + days * 80),
            ('receipts * 100 + miles * 1', receipts * 100 + miles * 1),
            ('receipts * 80 + days * 120', receipts * 80 + days * 120),
        ]
        
        for formula_name, predicted in tests:
            if abs(predicted - output) < 0.01:  # Exact match
                print(f"EXACT MATCH: {formula_name} = {predicted:.2f} vs actual {output:.2f}")
                print(f"  Days: {days}, Miles: {miles:.1f}, Receipts: ${receipts:.2f}")

find_exact_relationships()

# Let's also check if the interviews give us clues about specific cases
print("\n=== TESTING INTERVIEW INSIGHTS ===")

# Kevin mentioned 5-day trips with 180+ miles/day and <$100/day spending get bonuses
print("Testing Kevin's 'sweet spot' theory:")
sweet_spot_cases = df[
    (df['days'] == 5) & 
    (df['miles'] / df['days'] >= 180) & 
    (df['receipts'] / df['days'] <= 100)
]
print(f"Sweet spot cases: {len(sweet_spot_cases)}")
if len(sweet_spot_cases) > 0:
    print("Sweet spot case details:")
    for _, row in sweet_spot_cases.head(10).iterrows():
        efficiency = row['miles'] / row['days']
        spending_per_day = row['receipts'] / row['days']
        print(f"  Miles/day: {efficiency:.1f}, Spending/day: ${spending_per_day:.2f}, Output: ${row['output']:.2f}")

# Let's examine the exact relationship by looking at simpler cases first
print("\n=== EXAMINING SIMPLE CASES ===")

# Find cases with round numbers that might reveal the formula
simple_cases = df[
    (df['days'].isin([1, 2, 3, 5])) & 
    (df['miles'] <= 100) & 
    (df['receipts'] <= 50)
].copy()

print(f"Simple cases (1-5 days, ≤100 miles, ≤$50 receipts): {len(simple_cases)}")
simple_cases = simple_cases.sort_values(['days', 'miles', 'receipts'])

for _, row in simple_cases.head(15).iterrows():
    # Try to reverse engineer the formula
    days, miles, receipts, output = row['days'], row['miles'], row['receipts'], row['output']
    
    # What would the per-day rate be if we subtract mileage and receipts?
    per_day_base = (output - miles * 0.5 - receipts * 100) / days
    per_day_base2 = (output - miles * 1.0 - receipts * 80) / days
    
    print(f"Days: {days}, Miles: {miles:.1f}, Receipts: ${receipts:.2f}, Output: ${output:.2f}")
    print(f"  If mileage=$0.50/mi, receipts*100: base would be ${per_day_base:.2f}/day")
    print(f"  If mileage=$1.00/mi, receipts*80: base would be ${per_day_base2:.2f}/day")

print("\nSaving pattern analysis...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/pattern_analysis.csv', index=False)