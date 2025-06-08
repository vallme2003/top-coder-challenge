#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt

# Load the data
with open('/Users/vthenappan/Documents/GitHub/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame for easier analysis
df = pd.DataFrame([{
    'days': case['input']['trip_duration_days'],
    'miles': case['input']['miles_traveled'], 
    'receipts': case['input']['total_receipts_amount'],
    'output': case['expected_output']
} for case in data])

print("Data Overview:")
print(f"Total cases: {len(df)}")
print(f"Days range: {df['days'].min()} - {df['days'].max()}")
print(f"Miles range: {df['miles'].min()} - {df['miles'].max()}")
print(f"Receipts range: {df['receipts'].min()} - {df['receipts'].max()}")
print(f"Output range: {df['output'].min()} - {df['output'].max()}")
print()

# Analyze base patterns
print("=== BASIC PATTERN ANALYSIS ===")

# Check if there's a base per-day rate
df['per_day'] = df['output'] / df['days']
print(f"Output per day - Mean: {df['per_day'].mean():.2f}, Std: {df['per_day'].std():.2f}")

# Check mileage patterns
df['per_mile'] = df['output'] / df['miles']
print(f"Output per mile - Mean: {df['per_mile'].mean():.2f}, Std: {df['per_mile'].std():.2f}")

# Look for simple linear relationships
print("\n=== CORRELATION ANALYSIS ===")
print(f"Days vs Output: {df['days'].corr(df['output']):.3f}")
print(f"Miles vs Output: {df['miles'].corr(df['output']):.3f}")
print(f"Receipts vs Output: {df['receipts'].corr(df['output']):.3f}")

# Test Kevin's theories about efficiency (miles per day)
df['efficiency'] = df['miles'] / df['days']
print(f"Efficiency (miles/day) vs Output: {df['efficiency'].corr(df['output']):.3f}")

# Test spending per day patterns
df['spending_per_day'] = df['receipts'] / df['days']
print(f"Spending per day vs Output: {df['spending_per_day'].corr(df['output']):.3f}")

# Look for Kevin's "sweet spot" around 180-220 miles per day
sweet_spot = df[(df['efficiency'] >= 180) & (df['efficiency'] <= 220)]
print(f"\nSweet spot (180-220 miles/day): {len(sweet_spot)} cases")
if len(sweet_spot) > 0:
    print(f"Sweet spot average output: {sweet_spot['output'].mean():.2f}")
    print(f"Overall average output: {df['output'].mean():.2f}")

# Test for threshold effects mentioned in interviews
print("\n=== THRESHOLD ANALYSIS ===")

# Lisa mentioned $100/day base rate
base_rate = 100
print(f"If base rate is $100/day:")
for days in sorted(df['days'].unique()):
    day_data = df[df['days'] == days]
    expected_base = days * base_rate
    avg_output = day_data['output'].mean()
    print(f"  {days} day(s): Expected ${expected_base}, Actual avg ${avg_output:.2f}, Diff ${avg_output - expected_base:.2f}")

# Look for the 5-day bonus Lisa mentioned
five_day_data = df[df['days'] == 5]
if len(five_day_data) > 0:
    print(f"\n5-day trips: {len(five_day_data)} cases, avg output: {five_day_data['output'].mean():.2f}")
    four_day_data = df[df['days'] == 4]
    six_day_data = df[df['days'] == 6]
    if len(four_day_data) > 0:
        print(f"4-day trips: {len(four_day_data)} cases, avg output: {four_day_data['output'].mean():.2f}")
    if len(six_day_data) > 0:
        print(f"6-day trips: {len(six_day_data)} cases, avg output: {six_day_data['output'].mean():.2f}")

# Test mileage tiers Lisa mentioned
print("\n=== MILEAGE TIER ANALYSIS ===")
low_miles = df[df['miles'] <= 100]
high_miles = df[df['miles'] > 100]
print(f"Low mileage (≤100): {len(low_miles)} cases, avg per mile: ${low_miles['per_mile'].mean():.3f}")
print(f"High mileage (>100): {len(high_miles)} cases, avg per mile: ${high_miles['per_mile'].mean():.3f}")

# Look for receipt amount thresholds
print("\n=== RECEIPT THRESHOLD ANALYSIS ===")
for threshold in [50, 100, 200, 500, 800, 1000]:
    low_receipts = df[df['receipts'] <= threshold]
    high_receipts = df[df['receipts'] > threshold]
    if len(low_receipts) > 0 and len(high_receipts) > 0:
        print(f"Receipts ≤${threshold}: avg output ${low_receipts['output'].mean():.2f}")
        print(f"Receipts >${threshold}: avg output ${high_receipts['output'].mean():.2f}")

# Let's look for exact patterns by examining specific cases
print("\n=== EXACT PATTERN SEARCH ===")

# Try to find cases with identical inputs except one variable
def find_similar_cases(df, tolerance=0.01):
    similar_groups = []
    for i, row1 in df.iterrows():
        group = [i]
        for j, row2 in df.iterrows():
            if i != j:
                # Check if two cases differ by only one variable
                days_same = row1['days'] == row2['days']
                miles_close = abs(row1['miles'] - row2['miles']) <= 5
                receipts_close = abs(row1['receipts'] - row2['receipts']) <= tolerance
                
                if sum([days_same, miles_close, receipts_close]) >= 2:
                    group.append(j)
        
        if len(group) > 1:
            similar_groups.append(group)
    
    return similar_groups

# Look for the exact mathematical function
print("\n=== SEARCHING FOR EXACT FUNCTION ===")

# Test various hypotheses from the interviews
def test_formula(df, formula_func, name):
    df['predicted'] = df.apply(formula_func, axis=1)
    df['error'] = abs(df['predicted'] - df['output'])
    max_error = df['error'].max()
    mean_error = df['error'].mean()
    print(f"{name}: Max error {max_error:.3f}, Mean error {mean_error:.3f}")
    return max_error < 0.01  # Perfect match threshold

# Hypothesis 1: Base rate + mileage + receipt adjustments
def formula1(row):
    base = row['days'] * 100  # $100/day base
    mileage = row['miles'] * 0.58  # Standard mileage rate
    receipts = row['receipts'] * 0.8  # 80% reimbursement
    return base + mileage + receipts

test_formula(df, formula1, "Base + Linear mileage + Linear receipts")

# Hypothesis 2: Include efficiency bonus
def formula2(row):
    base = row['days'] * 100
    # Tiered mileage
    if row['miles'] <= 100:
        mileage = row['miles'] * 0.58
    else:
        mileage = 100 * 0.58 + (row['miles'] - 100) * 0.45
    
    # Receipt processing with diminishing returns
    if row['receipts'] <= 100:
        receipts = row['receipts'] * 0.9
    else:
        receipts = 100 * 0.9 + (row['receipts'] - 100) * 0.6
    
    # Efficiency bonus
    efficiency = row['miles'] / row['days']
    if 180 <= efficiency <= 220:
        bonus = 50
    else:
        bonus = 0
        
    return base + mileage + receipts + bonus

test_formula(df, formula2, "Tiered rates + Efficiency bonus")

# Let's examine some specific patterns
print("\n=== SPECIFIC CASE ANALYSIS ===")
print("First 10 cases:")
for i in range(min(10, len(df))):
    row = df.iloc[i]
    print(f"Days: {row['days']}, Miles: {row['miles']}, Receipts: ${row['receipts']:.2f} -> ${row['output']:.2f}")

print("\nSaving analysis results...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/analysis_results.csv', index=False)