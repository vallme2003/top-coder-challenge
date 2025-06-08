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

print("=== DAY PATTERN ANALYSIS ===")

# The residual pattern shows that longer trips get LESS than a linear rate
# This suggests either:
# 1. A different base rate structure
# 2. A penalty for long trips  
# 3. A non-linear day factor

# Let's test if there's a specific per-day rate that varies by trip length
print("Analyzing effective per-day rates:")

for days in sorted(df['days'].unique()):
    day_data = df[df['days'] == days]
    if len(day_data) >= 5:
        
        # Calculate what the effective base rate per day would be 
        # if we subtract out the best receipt and mile factors we found
        receipt_factor = 0.41
        mile_factor = 0.35
        
        day_data = day_data.copy()
        day_data['adjusted_output'] = day_data['output'] - receipt_factor * day_data['receipts'] - mile_factor * day_data['miles']
        day_data['effective_per_day'] = day_data['adjusted_output'] / days
        
        mean_per_day = day_data['effective_per_day'].mean()
        std_per_day = day_data['effective_per_day'].std()
        
        print(f"{days:2d} days: effective rate ${mean_per_day:6.2f}/day ± ${std_per_day:5.2f} ({len(day_data):3d} cases)")

# The pattern is clear! Let me test if there's a specific rate structure
print(f"\n=== TESTING CUSTOM DAY RATES ===")

# Based on the pattern above, let me define custom rates per day
day_rates = {}
for days in sorted(df['days'].unique()):
    day_data = df[df['days'] == days]
    if len(day_data) >= 5:
        # Calculate the empirical rate
        receipt_factor = 0.41
        mile_factor = 0.35
        
        adjusted_outputs = day_data['output'] - receipt_factor * day_data['receipts'] - mile_factor * day_data['miles']
        effective_per_day = (adjusted_outputs / days).mean()
        day_rates[days] = effective_per_day

print("Empirical day rates:")
for days, rate in day_rates.items():
    print(f"  {days:2d} days: ${rate:6.2f}/day")

# Test this custom rate structure
def test_custom_day_rates():
    receipt_factor = 0.41
    mile_factor = 0.35
    
    predicted_outputs = []
    for _, row in df.iterrows():
        days = row['days']
        if days in day_rates:
            base_component = day_rates[days] * days
        else:
            # For days not in our lookup, interpolate or use a fallback
            base_component = 100 * days  # fallback
        
        receipt_component = receipt_factor * row['receipts']
        mile_component = mile_factor * row['miles']
        
        predicted = base_component + receipt_component + mile_component
        predicted_outputs.append(predicted)
    
    df['predicted_custom'] = predicted_outputs
    df['error_custom'] = abs(df['predicted_custom'] - df['output'])
    
    print(f"\nCustom day rate formula results:")
    print(f"Max error: {df['error_custom'].max():.6f}")
    print(f"Mean error: {df['error_custom'].mean():.6f}")
    print(f"Cases with error < 1.0: {(df['error_custom'] < 1.0).sum()}")
    print(f"Cases with error < 0.1: {(df['error_custom'] < 0.1).sum()}")
    print(f"Cases with error < 0.01: {(df['error_custom'] < 0.01).sum()}")

test_custom_day_rates()

# Let me see if the day rates follow a pattern themselves
print(f"\n=== ANALYZING DAY RATE PATTERN ===")

days_list = sorted(day_rates.keys())
rates_list = [day_rates[d] for d in days_list]

print("Day rate sequence:")
for i, (days, rate) in enumerate(zip(days_list, rates_list)):
    diff = rate - rates_list[i-1] if i > 0 else 0
    print(f"  {days:2d} days: ${rate:6.2f}/day (change: {diff:+5.2f})")

# Check if it's a simple decreasing function
# Maybe something like: base_rate - penalty_per_day * (days - 1)
def fit_day_rate_function():
    print(f"\nTrying to fit day rate function:")
    
    # Test linear decrease: rate = base - penalty * (days - 1)
    for base in range(250, 301, 5):
        for penalty in range(0, 21, 1):
            errors = []
            for days in days_list:
                predicted_rate = base - penalty * (days - 1)
                actual_rate = day_rates[days]
                errors.append(abs(predicted_rate - actual_rate))
            
            max_error = max(errors)
            if max_error < 5:  # Good fit
                print(f"  Base: {base}, Penalty: {penalty} -> max error: {max_error:.2f}")
                
                # Test this formula on the actual data
                test_rate_formula(base, penalty)

def test_rate_formula(base_rate, penalty_per_day):
    receipt_factor = 0.41
    mile_factor = 0.35
    
    predicted_outputs = []
    for _, row in df.iterrows():
        days = row['days']
        effective_rate = base_rate - penalty_per_day * (days - 1)
        
        base_component = effective_rate * days
        receipt_component = receipt_factor * row['receipts']
        mile_component = mile_factor * row['miles']
        
        predicted = base_component + receipt_component + mile_component
        predicted_outputs.append(predicted)
    
    errors = [abs(pred - actual) for pred, actual in zip(predicted_outputs, df['output'])]
    max_error = max(errors)
    mean_error = sum(errors) / len(errors)
    perfect_matches = sum(1 for e in errors if e < 0.01)
    
    print(f"    Formula: ({base_rate} - {penalty_per_day} * (days-1)) * days + {receipt_factor} * receipts + {mile_factor} * miles")
    print(f"    Max error: {max_error:.6f}, Mean error: {mean_error:.6f}, Perfect matches: {perfect_matches}")
    
    if max_error < 0.1:
        print(f"    *** EXCELLENT FORMULA! ***")
        return True
    return False

fit_day_rate_function()

# Let me also test if there's a simple mathematical function for the day rates
print(f"\n=== TESTING MATHEMATICAL FUNCTIONS FOR DAY RATES ===")

# Maybe it's something like: rate = a / days + b
# Or: rate = a * exp(-b * days) + c
# Or: rate = a - b * log(days)

import math

for a in range(200, 401, 20):
    for b in range(50, 151, 10):
        # Test: rate = a / days + b
        errors = []
        for days in days_list:
            predicted_rate = a / days + b
            actual_rate = day_rates[days]
            errors.append(abs(predicted_rate - actual_rate))
        
        max_error = max(errors)
        if max_error < 10:
            print(f"Function a/days + b with a={a}, b={b}: max error {max_error:.2f}")

# Test logarithmic decrease
for a in range(250, 351, 10):
    for b in range(1, 51, 5):
        errors = []
        for days in days_list:
            predicted_rate = a - b * math.log(days)
            actual_rate = day_rates[days]
            errors.append(abs(predicted_rate - actual_rate))
        
        max_error = max(errors)
        if max_error < 5:
            print(f"Function a - b*log(days) with a={a}, b={b}: max error {max_error:.2f}")

print("\nSaving day pattern analysis...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/day_pattern_results.csv', index=False)