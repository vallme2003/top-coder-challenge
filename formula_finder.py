#!/usr/bin/env python3
import json
import pandas as pd
import numpy as np

def load_data():
    with open('/Users/vthenappan/Documents/GitHub/top-coder-challenge/public_cases.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame([
        {
            'trip_duration_days': case['input']['trip_duration_days'],
            'miles_traveled': case['input']['miles_traveled'],
            'total_receipts_amount': case['input']['total_receipts_amount'],
            'expected_output': case['expected_output']
        } for case in data
    ])
    
    return data, df

def examine_specific_cases(df):
    print('=== EXAMINING SPECIFIC CASES FOR PATTERNS ===')
    
    # Look at the simplest cases first
    print('\nSimplest cases (1 day, low miles, low receipts):')
    simple = df[
        (df['trip_duration_days'] == 1) &
        (df['miles_traveled'] < 100) &
        (df['total_receipts_amount'] < 100)
    ].sort_values('expected_output')
    
    for i, row in simple.head(15).iterrows():
        days = row['trip_duration_days']
        miles = row['miles_traveled']
        receipts = row['total_receipts_amount']
        output = row['expected_output']
        
        # Try different base calculations
        base_100 = 100 + miles * 0.58 + receipts * 0.8
        base_120 = 120 + miles * 0.58 + receipts * 0.8
        base_100_receipts_full = 100 + miles * 0.58 + receipts
        
        print(f'  {days}d, {miles}mi, ${receipts:.2f} -> ${output:.2f}')
        print(f'    Try 100+mi*0.58+rec*0.8: ${base_100:.2f} (diff: ${abs(output-base_100):.2f})')
        print(f'    Try 120+mi*0.58+rec*0.8: ${base_120:.2f} (diff: ${abs(output-base_120):.2f})')
        print(f'    Try 100+mi*0.58+rec*1.0: ${base_100_receipts_full:.2f} (diff: ${abs(output-base_100_receipts_full):.2f})')
        print()

def test_complex_formulas(df):
    print('=== TESTING MORE COMPLEX FORMULAS ===')
    
    # Test formulas with different components
    formulas_to_test = []
    
    # Base per-diem rates
    for base_daily in [100, 110, 120, 130, 140, 150]:
        # Mileage rates
        for mile_rate in [0.50, 0.55, 0.58, 0.60, 0.62, 0.65]:
            # Receipt rates  
            for receipt_rate in [0.6, 0.7, 0.8, 0.9, 1.0]:
                formula = f"days*{base_daily} + miles*{mile_rate} + receipts*{receipt_rate}"
                calculated = (df['trip_duration_days'] * base_daily + 
                            df['miles_traveled'] * mile_rate + 
                            df['total_receipts_amount'] * receipt_rate)
                
                # Check for exact matches
                exact_matches = (abs(calculated - df['expected_output']) < 0.01).sum()
                if exact_matches > 0:
                    avg_error = abs(calculated - df['expected_output']).mean()
                    formulas_to_test.append((formula, exact_matches, avg_error, calculated))
    
    # Sort by number of exact matches
    formulas_to_test.sort(key=lambda x: x[1], reverse=True)
    
    print('Top formulas by exact matches:')
    for formula, matches, avg_error, calculated in formulas_to_test[:10]:
        print(f'  {formula}: {matches} exact matches, avg error: ${avg_error:.2f}')

def test_tiered_systems(df):
    print('\n=== TESTING TIERED SYSTEMS ===')
    
    def calculate_tiered_receipts(receipts, low_rate=0.8, high_rate=0.6, threshold=500):
        if receipts <= threshold:
            return receipts * low_rate
        else:
            return threshold * low_rate + (receipts - threshold) * high_rate
    
    def calculate_tiered_mileage(miles, low_rate=0.58, high_rate=0.45, threshold=200):
        if miles <= threshold:
            return miles * low_rate
        else:
            return threshold * low_rate + (miles - threshold) * high_rate
    
    # Test various tiered combinations
    for base in [100, 120, 140]:
        for mile_thresh in [100, 150, 200, 250]:
            for mile_low in [0.55, 0.58, 0.60]:
                for mile_high in [0.40, 0.45, 0.50]:
                    for receipt_thresh in [300, 500, 800]:
                        for receipt_low in [0.7, 0.8, 0.9]:
                            for receipt_high in [0.5, 0.6, 0.7]:
                                
                                calculated = (df['trip_duration_days'] * base +
                                            df['miles_traveled'].apply(lambda x: calculate_tiered_mileage(x, mile_low, mile_high, mile_thresh)) +
                                            df['total_receipts_amount'].apply(lambda x: calculate_tiered_receipts(x, receipt_low, receipt_high, receipt_thresh)))
                                
                                exact_matches = (abs(calculated - df['expected_output']) < 0.01).sum()
                                if exact_matches > 10:  # Only show promising results
                                    avg_error = abs(calculated - df['expected_output']).mean()
                                    print(f'  Base {base}, Miles {mile_low}/{mile_high}@{mile_thresh}, Receipts {receipt_low}/{receipt_high}@{receipt_thresh}: {exact_matches} exact matches, avg error ${avg_error:.2f}')

def test_efficiency_bonuses(df):
    print('\n=== TESTING EFFICIENCY BONUSES ===')
    
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    
    def calculate_efficiency_bonus(miles_per_day):
        if 180 <= miles_per_day <= 220:
            return 50  # Bonus amount
        elif 150 <= miles_per_day < 180:
            return 25
        elif 220 < miles_per_day <= 300:
            return 25
        else:
            return 0
    
    for base in [100, 120]:
        for mile_rate in [0.55, 0.58, 0.60]:
            for receipt_rate in [0.7, 0.8, 0.9]:
                calculated = (df['trip_duration_days'] * base +
                            df['miles_traveled'] * mile_rate +
                            df['total_receipts_amount'] * receipt_rate +
                            df['miles_per_day'].apply(calculate_efficiency_bonus))
                
                exact_matches = (abs(calculated - df['expected_output']) < 0.01).sum()
                if exact_matches > 5:
                    avg_error = abs(calculated - df['expected_output']).mean()
                    print(f'  Base {base} + miles*{mile_rate} + receipts*{receipt_rate} + efficiency bonus: {exact_matches} exact matches, avg error ${avg_error:.2f}')

def analyze_residuals(df):
    print('\n=== ANALYZING RESIDUALS FOR PATTERNS ===')
    
    # Use a simple base formula and analyze what's left
    base_formula = df['trip_duration_days'] * 120 + df['miles_traveled'] * 0.58 + df['total_receipts_amount'] * 0.8
    residuals = df['expected_output'] - base_formula
    
    df['residuals'] = residuals
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    print(f'Residual statistics after base formula (days*120 + miles*0.58 + receipts*0.8):')
    print(f'  Mean: ${residuals.mean():.2f}')
    print(f'  Std: ${residuals.std():.2f}')
    print(f'  Min: ${residuals.min():.2f}')
    print(f'  Max: ${residuals.max():.2f}')
    
    # Look for patterns in residuals
    print('\nResidual patterns by trip characteristics:')
    
    # By trip length
    for days in range(1, 8):
        subset = df[df['trip_duration_days'] == days]
        if len(subset) > 10:
            avg_residual = subset['residuals'].mean()
            print(f'  {days}-day trips: avg residual ${avg_residual:.2f}')
    
    # By efficiency
    high_eff = df[df['miles_per_day'] > 200]
    low_eff = df[df['miles_per_day'] <= 200]
    print(f'  High efficiency (>200 mi/day): avg residual ${high_eff["residuals"].mean():.2f}')
    print(f'  Low efficiency (<=200 mi/day): avg residual ${low_eff["residuals"].mean():.2f}')

def examine_outliers(df):
    print('\n=== EXAMINING OUTLIERS FOR CLUES ===')
    
    # Find cases with unusually high or low outputs relative to inputs
    df['total_inputs'] = df['trip_duration_days'] * 100 + df['miles_traveled'] * 0.58 + df['total_receipts_amount'] * 0.8
    df['output_ratio'] = df['expected_output'] / df['total_inputs']
    
    # High ratio cases (getting more than expected)
    high_ratio = df.nlargest(10, 'output_ratio')
    print('Cases with highest output ratios:')
    for i, row in high_ratio.iterrows():
        print(f'  {row["trip_duration_days"]}d, {row["miles_traveled"]}mi, ${row["total_receipts_amount"]:.2f} -> ${row["expected_output"]:.2f} (ratio: {row["output_ratio"]:.2f})')
    
    # Low ratio cases (getting less than expected)
    low_ratio = df.nsmallest(10, 'output_ratio')
    print('\nCases with lowest output ratios:')
    for i, row in low_ratio.iterrows():
        print(f'  {row["trip_duration_days"]}d, {row["miles_traveled"]}mi, ${row["total_receipts_amount"]:.2f} -> ${row["expected_output"]:.2f} (ratio: {row["output_ratio"]:.2f})')

def main():
    data, df = load_data()
    
    examine_specific_cases(df)
    test_complex_formulas(df)
    test_tiered_systems(df)
    test_efficiency_bonuses(df)
    analyze_residuals(df)
    examine_outliers(df)

if __name__ == '__main__':
    main()