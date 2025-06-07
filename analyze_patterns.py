#!/usr/bin/env python3
import json
import pandas as pd
import numpy as np
from collections import defaultdict

def load_data():
    with open('/Users/vthenappan/Documents/GitHub/top-coder-challenge/public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame([
        {
            'trip_duration_days': case['input']['trip_duration_days'],
            'miles_traveled': case['input']['miles_traveled'],
            'total_receipts_amount': case['input']['total_receipts_amount'],
            'expected_output': case['expected_output']
        } for case in data
    ])
    
    return data, df

def analyze_basic_patterns(df):
    print('=== BASIC STATISTICS ===')
    print(f'Total test cases: {len(df)}')
    print()
    print('Summary statistics:')
    print(df.describe())
    print()
    
    # Look for simple mathematical relationships
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    df['output_per_day'] = df['expected_output'] / df['trip_duration_days']
    
    print('=== DERIVED METRICS ===')
    print('Miles per day stats:')
    print(df['miles_per_day'].describe())
    print()
    print('Receipts per day stats:')
    print(df['receipts_per_day'].describe())
    print()
    print('Output per day stats:')
    print(df['output_per_day'].describe())
    print()

def look_for_exact_formulas(df):
    print('=== LOOKING FOR EXACT FORMULAS ===')
    
    # Test various formula combinations
    formulas = {
        'days * 100': df['trip_duration_days'] * 100,
        'miles * 0.58': df['miles_traveled'] * 0.58,
        'receipts * 0.8': df['total_receipts_amount'] * 0.8,
        'days*100 + miles*0.58': df['trip_duration_days'] * 100 + df['miles_traveled'] * 0.58,
        'days*100 + miles*0.58 + receipts*0.8': df['trip_duration_days'] * 100 + df['miles_traveled'] * 0.58 + df['total_receipts_amount'] * 0.8,
    }
    
    for name, calculated in formulas.items():
        diff = abs(calculated - df['expected_output'])
        exact_matches = (diff < 0.01).sum()
        avg_error = diff.mean()
        print(f'{name}: {exact_matches} exact matches ({exact_matches/len(df)*100:.1f}%), avg error: ${avg_error:.2f}')
    
    print()

def analyze_by_trip_length(df):
    print('=== ANALYSIS BY TRIP LENGTH ===')
    
    for days in sorted(df['trip_duration_days'].unique()):
        subset = df[df['trip_duration_days'] == days]
        if len(subset) > 10:  # Only analyze if we have enough samples
            print(f'\n{days}-day trips ({len(subset)} cases):')
            print(f'  Output range: ${subset["expected_output"].min():.2f} - ${subset["expected_output"].max():.2f}')
            print(f'  Output per day: ${subset["output_per_day"].mean():.2f} ± ${subset["output_per_day"].std():.2f}')
            
            # Look for patterns within this trip length
            correlation_miles = subset['miles_traveled'].corr(subset['expected_output'])
            correlation_receipts = subset['total_receipts_amount'].corr(subset['expected_output'])
            print(f'  Correlation with miles: {correlation_miles:.3f}')
            print(f'  Correlation with receipts: {correlation_receipts:.3f}')

def analyze_receipt_patterns(df):
    print('\n=== RECEIPT AMOUNT PATTERNS ===')
    
    # Look for patterns in receipt cents
    df['receipt_cents'] = (df['total_receipts_amount'] * 100).round().astype(int) % 100
    
    print('Receipt ending patterns:')
    for cents in [0, 49, 50, 99]:
        subset = df[df['receipt_cents'] == cents]
        if len(subset) > 5:
            avg_output = subset['expected_output'].mean()
            print(f'  Receipts ending in .{cents:02d}: {len(subset)} cases, avg output: ${avg_output:.2f}')
    
    print()

def find_threshold_effects(df):
    print('=== LOOKING FOR THRESHOLD EFFECTS ===')
    
    # Test various thresholds mentioned in interviews
    thresholds = {
        'miles': [100, 180, 200, 220, 300, 400, 600, 800],
        'receipts': [50, 75, 100, 120, 600, 800, 1000, 1200],
        'days': [1, 3, 4, 5, 6, 8]
    }
    
    for metric, threshold_list in thresholds.items():
        print(f'\n{metric.upper()} thresholds:')
        col = 'miles_traveled' if metric == 'miles' else 'total_receipts_amount' if metric == 'receipts' else 'trip_duration_days'
        
        for threshold in threshold_list:
            below = df[df[col] < threshold]
            above = df[df[col] >= threshold]
            
            if len(below) > 10 and len(above) > 10:
                below_avg = below['expected_output'].mean()
                above_avg = above['expected_output'].mean()
                print(f'  {threshold}: Below={len(below)} cases (${below_avg:.2f}), Above={len(above)} cases (${above_avg:.2f})')

def analyze_efficiency_patterns(df):
    print('\n=== EFFICIENCY PATTERNS ===')
    
    # Calculate efficiency metrics as mentioned in interviews
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    
    # Look for the 180-220 miles per day sweet spot Kevin mentioned
    efficiency_ranges = [
        (0, 100),
        (100, 150),
        (150, 180),
        (180, 220),
        (220, 300),
        (300, 500),
        (500, 1000)
    ]
    
    for min_eff, max_eff in efficiency_ranges:
        subset = df[(df['miles_per_day'] >= min_eff) & (df['miles_per_day'] < max_eff)]
        if len(subset) > 5:
            avg_output = subset['expected_output'].mean()
            avg_per_day = subset['output_per_day'].mean()
            print(f'  {min_eff}-{max_eff} miles/day: {len(subset)} cases, avg output: ${avg_output:.2f}, per day: ${avg_per_day:.2f}')

def analyze_spending_patterns(df):
    print('\n=== SPENDING PATTERNS BY TRIP LENGTH ===')
    
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Analyze spending patterns by trip length as Kevin suggested
    for days in [1, 2, 3, 4, 5, 6, 7, 8]:
        day_subset = df[df['trip_duration_days'] == days]
        if len(day_subset) > 10:
            print(f'\n{days}-day trips:')
            
            # Test Kevin's optimal spending ranges
            if days <= 3:  # Short trips
                optimal_range = (0, 75)
            elif 4 <= days <= 6:  # Medium trips
                optimal_range = (0, 120)
            else:  # Long trips
                optimal_range = (0, 90)
            
            optimal = day_subset[
                (day_subset['receipts_per_day'] >= optimal_range[0]) & 
                (day_subset['receipts_per_day'] <= optimal_range[1])
            ]
            suboptimal = day_subset[day_subset['receipts_per_day'] > optimal_range[1]]
            
            if len(optimal) > 0 and len(suboptimal) > 0:
                print(f'  Optimal spending (${optimal_range[0]}-${optimal_range[1]}/day): {len(optimal)} cases, avg: ${optimal["expected_output"].mean():.2f}')
                print(f'  High spending (>${optimal_range[1]}/day): {len(suboptimal)} cases, avg: ${suboptimal["expected_output"].mean():.2f}')

def look_for_exact_combinations(df):
    print('\n=== LOOKING FOR EXACT BUSINESS RULE COMBINATIONS ===')
    
    # Test Kevin's "sweet spot combo": 5-day trips with 180+ miles per day and under $100 per day in spending
    sweet_spot = df[
        (df['trip_duration_days'] == 5) &
        (df['miles_traveled'] / df['trip_duration_days'] >= 180) &
        (df['total_receipts_amount'] / df['trip_duration_days'] < 100)
    ]
    
    if len(sweet_spot) > 0:
        print(f'Kevin\'s "sweet spot combo" (5 days, 180+ miles/day, <$100/day): {len(sweet_spot)} cases')
        print(f'  Average output: ${sweet_spot["expected_output"].mean():.2f}')
        print(f'  Output per day: ${sweet_spot["output_per_day"].mean():.2f}')
    
    # Test "vacation penalty": 8+ day trips with high spending
    vacation_penalty = df[
        (df['trip_duration_days'] >= 8) &
        (df['total_receipts_amount'] / df['trip_duration_days'] > 120)
    ]
    
    if len(vacation_penalty) > 0:
        print(f'Kevin\'s "vacation penalty" (8+ days, >$120/day): {len(vacation_penalty)} cases')
        print(f'  Average output: ${vacation_penalty["expected_output"].mean():.2f}')
        print(f'  Output per day: ${vacation_penalty["output_per_day"].mean():.2f}')
    
    print()

def main():
    data, df = load_data()
    
    analyze_basic_patterns(df)
    look_for_exact_formulas(df)
    analyze_by_trip_length(df)
    analyze_receipt_patterns(df)
    find_threshold_effects(df)
    analyze_efficiency_patterns(df)
    analyze_spending_patterns(df)
    look_for_exact_combinations(df)

if __name__ == '__main__':
    main()