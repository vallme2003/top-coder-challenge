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

def analyze_by_categories(df):
    print('=== ANALYZING BY TRIP CATEGORIES ===')
    
    # Based on Kevin's comment about different calculation paths
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Define categories mentioned in interviews
    categories = []
    
    # Short high-mileage trips
    short_high = df[(df['trip_duration_days'] <= 3) & (df['miles_per_day'] > 100)]
    if len(short_high) > 0:
        categories.append(('Short High-Mileage', short_high))
    
    # Long low-mileage trips  
    long_low = df[(df['trip_duration_days'] >= 7) & (df['miles_per_day'] < 100)]
    if len(long_low) > 0:
        categories.append(('Long Low-Mileage', long_low))
    
    # Medium balanced trips
    medium_balanced = df[
        (df['trip_duration_days'].between(4, 6)) & 
        (df['miles_per_day'].between(50, 200)) &
        (df['receipts_per_day'].between(50, 200))
    ]
    if len(medium_balanced) > 0:
        categories.append(('Medium Balanced', medium_balanced))
    
    # High efficiency trips (Kevin's sweet spot)
    high_efficiency = df[
        (df['miles_per_day'].between(180, 220)) &
        (df['receipts_per_day'] < 100)
    ]
    if len(high_efficiency) > 0:
        categories.append(('High Efficiency', high_efficiency))
    
    # "Vacation penalty" trips
    vacation_penalty = df[
        (df['trip_duration_days'] >= 8) &
        (df['receipts_per_day'] > 120)
    ]
    if len(vacation_penalty) > 0:
        categories.append(('Vacation Penalty', vacation_penalty))
    
    for name, subset in categories:
        print(f'\n{name} ({len(subset)} cases):')
        print(f'  Days: {subset["trip_duration_days"].mean():.1f} ± {subset["trip_duration_days"].std():.1f}')
        print(f'  Miles/day: {subset["miles_per_day"].mean():.1f} ± {subset["miles_per_day"].std():.1f}')
        print(f'  Receipts/day: {subset["receipts_per_day"].mean():.1f} ± {subset["receipts_per_day"].std():.1f}')
        print(f'  Output: ${subset["expected_output"].mean():.2f} ± ${subset["expected_output"].std():.2f}')
        print(f'  Output/day: ${(subset["expected_output"] / subset["trip_duration_days"]).mean():.2f}')
        
        # Try to find patterns within each category
        if len(subset) > 10:
            # Test simple formulas within category
            test_category_formula(subset, name)

def test_category_formula(subset, category_name):
    print(f'    Testing formulas for {category_name}:')
    
    # Try different base formulas for this specific category
    for base_per_day in [80, 90, 100, 110, 120, 130, 140, 150]:
        for mile_rate in [0.45, 0.50, 0.55, 0.58, 0.60, 0.65]:
            for receipt_rate in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                calculated = (subset['trip_duration_days'] * base_per_day + 
                            subset['miles_traveled'] * mile_rate + 
                            subset['total_receipts_amount'] * receipt_rate)
                
                exact_matches = (abs(calculated - subset['expected_output']) < 0.01).sum()
                if exact_matches > 0:
                    avg_error = abs(calculated - subset['expected_output']).mean()
                    print(f'      {base_per_day} + {mile_rate}*miles + {receipt_rate}*receipts: {exact_matches} exact matches, avg error ${avg_error:.2f}')

def look_for_threshold_driven_rules(df):
    print('\n=== LOOKING FOR THRESHOLD-DRIVEN RULES ===')
    
    # Look for sudden changes in reimbursement patterns at specific thresholds
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Test various thresholds for sudden rule changes
    print('Testing mile thresholds:')
    for threshold in [50, 100, 150, 200, 250, 300, 400, 500]:
        below = df[df['miles_traveled'] < threshold]
        above = df[df['miles_traveled'] >= threshold]
        
        if len(below) > 20 and len(above) > 20:
            below_ratio = (below['expected_output'] / (below['trip_duration_days'] * 100 + below['miles_traveled'] * 0.58 + below['total_receipts_amount'] * 0.8)).mean()
            above_ratio = (above['expected_output'] / (above['trip_duration_days'] * 100 + above['miles_traveled'] * 0.58 + above['total_receipts_amount'] * 0.8)).mean()
            
            if abs(below_ratio - above_ratio) > 0.1:  # Significant difference
                print(f'  {threshold} miles: Below ratio {below_ratio:.3f}, Above ratio {above_ratio:.3f}')
    
    print('\nTesting receipt per day thresholds:')
    for threshold in [30, 50, 75, 100, 125, 150, 200, 250, 300]:
        below = df[df['receipts_per_day'] < threshold]
        above = df[df['receipts_per_day'] >= threshold]
        
        if len(below) > 20 and len(above) > 20:
            below_ratio = (below['expected_output'] / (below['trip_duration_days'] * 100 + below['miles_traveled'] * 0.58 + below['total_receipts_amount'] * 0.8)).mean()
            above_ratio = (above['expected_output'] / (above['trip_duration_days'] * 100 + above['miles_traveled'] * 0.58 + above['total_receipts_amount'] * 0.8)).mean()
            
            if abs(below_ratio - above_ratio) > 0.1:  # Significant difference
                print(f'  ${threshold}/day receipts: Below ratio {below_ratio:.3f}, Above ratio {above_ratio:.3f}')

def test_multi_component_formulas(df):
    print('\n=== TESTING MULTI-COMPONENT FORMULAS ===')
    
    # Maybe there are separate calculations that get added together
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Test formulas with conditional bonuses/penalties
    def complex_formula(row):
        days = row['trip_duration_days']
        miles = row['miles_traveled']
        receipts = row['total_receipts_amount']
        miles_per_day = row['miles_per_day']
        receipts_per_day = row['receipts_per_day']
        
        # Base component
        base = days * 100
        
        # Mileage component
        if miles <= 200:
            mileage = miles * 0.58
        else:
            mileage = 200 * 0.58 + (miles - 200) * 0.45
        
        # Receipt component with penalties for high spending
        if receipts_per_day <= 75:
            receipt_comp = receipts * 0.8
        elif receipts_per_day <= 150:
            receipt_comp = receipts * 0.6
        elif receipts_per_day <= 300:
            receipt_comp = receipts * 0.4
        else:
            receipt_comp = receipts * 0.2
        
        # Efficiency bonuses
        efficiency_bonus = 0
        if 180 <= miles_per_day <= 220 and days >= 4:
            efficiency_bonus = days * 20
        
        # Trip length adjustments
        length_adjustment = 0
        if days == 5:
            length_adjustment = 25  # Lisa's 5-day bonus
        elif days >= 8:
            length_adjustment = -days * 5  # Penalty for very long trips
        
        return base + mileage + receipt_comp + efficiency_bonus + length_adjustment
    
    df['complex_calc'] = df.apply(complex_formula, axis=1)
    df['complex_error'] = abs(df['complex_calc'] - df['expected_output'])
    
    exact_matches = (df['complex_error'] < 0.01).sum()
    close_matches = (df['complex_error'] < 5.0).sum()
    avg_error = df['complex_error'].mean()
    
    print(f'Complex multi-component formula:')
    print(f'  Exact matches: {exact_matches}')
    print(f'  Close matches (< $5): {close_matches}')
    print(f'  Average error: ${avg_error:.2f}')
    
    if close_matches > 0:
        print('\nBest matches:')
        best = df.nsmallest(10, 'complex_error')
        for i, row in best.iterrows():
            print(f'  {row["trip_duration_days"]}d, {row["miles_traveled"]}mi, ${row["total_receipts_amount"]:.2f} -> Expected: ${row["expected_output"]:.2f}, Calc: ${row["complex_calc"]:.2f}, Error: ${row["complex_error"]:.2f}')

def find_exact_pattern_in_simple_cases(df):
    print('\n=== FINDING EXACT PATTERNS IN SIMPLE CASES ===')
    
    # Look at the absolute simplest cases to reverse engineer
    simple = df[
        (df['trip_duration_days'] <= 2) &
        (df['miles_traveled'] <= 100) &
        (df['total_receipts_amount'] <= 50)
    ].sort_values(['trip_duration_days', 'miles_traveled', 'total_receipts_amount'])
    
    print(f'Analyzing {len(simple)} simple cases...')
    
    for i, row in simple.head(20).iterrows():
        days = int(row['trip_duration_days'])
        miles = int(row['miles_traveled'])
        receipts = row['total_receipts_amount']
        output = row['expected_output']
        
        print(f'\n{days} days, {miles} miles, ${receipts:.2f} -> ${output:.2f}')
        
        # Try to find exact mathematical relationship
        # Test if it's exactly: base + miles * rate + receipts * rate
        for base in range(80, 160, 5):
            for mile_cents in range(50, 70):  # 0.50 to 0.69
                mile_rate = mile_cents / 100.0
                for receipt_cents in range(50, 100, 5):  # 0.50 to 0.95
                    receipt_rate = receipt_cents / 100.0
                    
                    calculated = days * base + miles * mile_rate + receipts * receipt_rate
                    if abs(calculated - output) < 0.01:
                        print(f'  EXACT MATCH: {days}*{base} + {miles}*{mile_rate} + {receipts:.2f}*{receipt_rate} = {calculated:.2f}')
                        
                        # Test this formula on other similar cases
                        test_cases = df[
                            (df['trip_duration_days'] == days) &
                            (df['miles_traveled'] <= 150) &
                            (df['total_receipts_amount'] <= 100)
                        ]
                        
                        if len(test_cases) > 1:
                            test_calc = test_cases['trip_duration_days'] * base + test_cases['miles_traveled'] * mile_rate + test_cases['total_receipts_amount'] * receipt_rate
                            test_matches = (abs(test_calc - test_cases['expected_output']) < 0.01).sum()
                            print(f'    Testing on {len(test_cases)} similar cases: {test_matches} exact matches')

def main():
    data, df = load_data()
    
    analyze_by_categories(df)
    look_for_threshold_driven_rules(df)
    test_multi_component_formulas(df)
    find_exact_pattern_in_simple_cases(df)

if __name__ == '__main__':
    main()