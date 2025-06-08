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

print("=== SIMPLE PATTERN CHECK ===")

# Let me step back and look for very simple patterns
# Maybe I'm overcomplicating this

# From the interviews, people mentioned that the system can be figured out
# Kevin claims to predict within 15% accuracy
# This suggests there IS a discoverable pattern

print("Looking for exact matches with simple arithmetic...")

# Let me test VERY simple formulas first
def test_simple_formulas():
    simple_tests = []
    
    # Test basic combinations
    for base in [100, 110, 120, 130, 140, 150]:
        for receipt_mult in range(100, 151, 10):  # 100, 110, 120, etc.
            # Formula: base * days + receipts * receipt_mult
            predicted = base * df['days'] + df['receipts'] * receipt_mult
            max_error = abs(predicted - df['output']).max()
            
            if max_error < 100:  # Reasonable match
                simple_tests.append((f"{base} * days + {receipt_mult} * receipts", max_error))
    
    # Sort by error
    simple_tests.sort(key=lambda x: x[1])
    
    print("Simple two-component formulas (base * days + receipts * factor):")
    for formula, error in simple_tests[:10]:
        print(f"  {formula:<30} Max error: {error:.3f}")

test_simple_formulas()

# Let me examine specific cases to understand the pattern better
print(f"\n=== EXAMINING SPECIFIC PATTERNS ===")

# Look at cases where two variables are similar but one differs
def find_similar_cases():
    print("Looking for cases with similar inputs...")
    
    # Find cases with same days and similar receipts
    for target_days in [1, 2, 3, 4, 5]:
        day_cases = df[df['days'] == target_days]
        
        if len(day_cases) >= 3:
            # Sort by receipts to see the pattern
            day_cases_sorted = day_cases.sort_values('receipts')
            
            print(f"\n{target_days}-day trips (first 5, sorted by receipts):")
            for _, row in day_cases_sorted.head(5).iterrows():
                ratio_receipts = row['output'] / row['receipts'] if row['receipts'] > 0 else 0
                ratio_miles = row['output'] / row['miles'] if row['miles'] > 0 else 0
                print(f"  Miles: {row['miles']:6.1f}, Receipts: ${row['receipts']:7.2f}, Output: ${row['output']:7.2f}")
                print(f"    Output/Receipts: {ratio_receipts:6.2f}, Output/Miles: {ratio_miles:6.2f}")

find_similar_cases()

# Let me check if there are any exact integer relationships
print(f"\n=== CHECKING FOR EXACT INTEGER RELATIONSHIPS ===")

def check_exact_relationships():
    print("Testing exact integer multipliers...")
    
    # Check first 20 cases for exact patterns
    for i in range(min(20, len(df))):
        row = df.iloc[i]
        days, miles, receipts, output = row['days'], row['miles'], row['receipts'], row['output']
        
        print(f"\nCase {i+1}: Days={days}, Miles={miles:.1f}, Receipts=${receipts:.2f}, Output=${output:.2f}")
        
        # Test if output is exactly some combination
        # Test: receipts * 120 + days * 100
        test1 = receipts * 120 + days * 100
        if abs(test1 - output) < 0.01:
            print(f"  EXACT: receipts * 120 + days * 100 = {test1:.2f}")
        
        # Test: receipts * 100 + days * 120
        test2 = receipts * 100 + days * 120
        if abs(test2 - output) < 0.01:
            print(f"  EXACT: receipts * 100 + days * 120 = {test2:.2f}")
        
        # Test: receipts * 80 + days * 100 + miles * 0.5
        test3 = receipts * 80 + days * 100 + miles * 0.5
        if abs(test3 - output) < 0.01:
            print(f"  EXACT: receipts * 80 + days * 100 + miles * 0.5 = {test3:.2f}")
        
        # Test: receipts * days * some_factor
        for factor in [80, 90, 100, 110, 120]:
            test4 = receipts * days * factor
            if abs(test4 - output) < 0.01:
                print(f"  EXACT: receipts * days * {factor} = {test4:.2f}")
        
        # More targeted tests based on the high receipt correlation
        # Test: receipts * (100 + some adjustment based on days/miles)
        day_adj = days * 10
        mile_adj = miles / 10
        test5 = receipts * (100 + day_adj)
        test6 = receipts * (100 + mile_adj)
        
        if abs(test5 - output) < 1.0:
            print(f"  Close: receipts * (100 + days*10) = {test5:.2f} (error: {abs(test5-output):.3f})")
        
        if abs(test6 - output) < 1.0:
            print(f"  Close: receipts * (100 + miles/10) = {test6:.2f} (error: {abs(test6-output):.3f})")

check_exact_relationships()

# Let me try a completely different approach - maybe it's a lookup table or has discrete values
print(f"\n=== CHECKING FOR DISCRETE/LOOKUP PATTERNS ===")

def check_discrete_patterns():
    # Maybe the outputs fall into discrete buckets
    print("Checking if outputs cluster around specific values...")
    
    # Round outputs to nearest dollar and see if there are patterns
    df['output_rounded'] = df['output'].round(0)
    output_counts = df['output_rounded'].value_counts()
    
    print(f"Most common output values:")
    for output_val, count in output_counts.head(10).items():
        if count > 1:
            print(f"  ${output_val:.0f}: {count} cases")
    
    # Check if there are formulaic relationships for the most common values
    for common_output in output_counts.head(5).index:
        cases_with_output = df[df['output_rounded'] == common_output]
        if len(cases_with_output) > 1:
            print(f"\nCases with output ~${common_output:.0f}:")
            for _, row in cases_with_output.iterrows():
                print(f"  Days: {row['days']}, Miles: {row['miles']:.1f}, Receipts: ${row['receipts']:.2f}")

check_discrete_patterns()

# Last attempt - maybe I need to think about this differently
# What if the formula uses integer arithmetic or has specific business rules?
print(f"\n=== BUSINESS RULE ANALYSIS ===")

def analyze_business_rules():
    print("Looking for business rule patterns...")
    
    # From interviews, Kevin mentioned specific combinations that trigger bonuses
    # Let's look for threshold effects
    
    # Check the "5-day sweet spot"
    five_day_cases = df[df['days'] == 5]
    print(f"\n5-day trips analysis ({len(five_day_cases)} cases):")
    print(f"  Output range: ${five_day_cases['output'].min():.2f} - ${five_day_cases['output'].max():.2f}")
    print(f"  Average output: ${five_day_cases['output'].mean():.2f}")
    
    # Look for the efficiency bonus Kevin mentioned
    df['efficiency'] = df['miles'] / df['days']
    sweet_spot = df[(df['efficiency'] >= 180) & (df['efficiency'] <= 220)]
    print(f"\nHigh efficiency trips (180-220 miles/day): {len(sweet_spot)} cases")
    if len(sweet_spot) > 0:
        print(f"  Average output: ${sweet_spot['output'].mean():.2f}")
        print(f"  Average for all trips: ${df['output'].mean():.2f}")
    
    # Look for spending per day effects
    df['spending_per_day'] = df['receipts'] / df['days']
    
    # Test Kevin's spending thresholds
    for threshold in [75, 90, 100, 120]:
        low_spenders = df[df['spending_per_day'] <= threshold]
        high_spenders = df[df['spending_per_day'] > threshold]
        
        if len(low_spenders) > 10 and len(high_spenders) > 10:
            print(f"\nSpending ≤${threshold}/day: avg output ${low_spenders['output'].mean():.2f}")
            print(f"Spending >${threshold}/day: avg output ${high_spenders['output'].mean():.2f}")

analyze_business_rules()

print("\nSaving simple pattern check results...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/simple_pattern_results.csv', index=False)