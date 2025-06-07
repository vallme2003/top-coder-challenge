#!/usr/bin/env python3
import json
import pandas as pd
import numpy as np
from collections import defaultdict

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

def systematic_exact_search(df):
    print('=== SYSTEMATIC SEARCH FOR EXACT FORMULAS ===')
    
    # For each case, find all possible base+mile+receipt combinations that give exact matches
    exact_formula_matches = defaultdict(list)
    
    print('Searching for exact formulas (this may take a moment)...')
    
    for i, row in df.iterrows():
        days = int(row['trip_duration_days'])
        miles = row['miles_traveled']
        receipts = row['total_receipts_amount']
        output = row['expected_output']
        
        # Test formula: days * base + miles * mile_rate + receipts * receipt_rate
        for base in range(70, 160, 5):  # Base per day from $70 to $155
            for mile_cents in range(40, 80):  # Mile rate from $0.40 to $0.79
                mile_rate = mile_cents / 100.0
                for receipt_cents in range(40, 120, 5):  # Receipt rate from 0.40 to 1.15
                    receipt_rate = receipt_cents / 100.0
                    
                    calculated = days * base + miles * mile_rate + receipts * receipt_rate
                    if abs(calculated - output) < 0.01:
                        formula = f"{base}+{mile_rate}*mi+{receipt_rate}*rec"
                        exact_formula_matches[formula].append({
                            'case': i,
                            'days': days,
                            'miles': miles,
                            'receipts': receipts,
                            'output': output
                        })
        
        if (i + 1) % 100 == 0:
            print(f'  Processed {i + 1}/{len(df)} cases...')
    
    # Analyze which formulas work for multiple cases
    print(f'\nFound formulas that work for multiple cases:')
    for formula, matches in sorted(exact_formula_matches.items(), key=lambda x: len(x[1]), reverse=True):
        if len(matches) > 1:
            print(f'  {formula}: {len(matches)} exact matches')
            
            # Show some examples
            for match in matches[:3]:
                print(f'    {match["days"]}d, {match["miles"]}mi, ${match["receipts"]:.2f} -> ${match["output"]:.2f}')
            
            if len(matches) > 3:
                print(f'    ... and {len(matches) - 3} more')

def test_most_promising_formulas(df):
    print('\n=== TESTING MOST PROMISING FORMULAS ON FULL DATASET ===')
    
    # Based on the systematic search, test the most promising parameter combinations
    promising_formulas = [
        (90, 0.55, 0.80),
        (85, 0.58, 0.85), 
        (95, 0.50, 0.75),
        (100, 0.58, 0.80),
        (90, 0.60, 0.75),
    ]
    
    for base, mile_rate, receipt_rate in promising_formulas:
        calculated = df['trip_duration_days'] * base + df['miles_traveled'] * mile_rate + df['total_receipts_amount'] * receipt_rate
        
        exact_matches = (abs(calculated - df['expected_output']) < 0.01).sum()
        close_matches = (abs(calculated - df['expected_output']) < 1.0).sum()
        avg_error = abs(calculated - df['expected_output']).mean()
        
        print(f'  {base} + {mile_rate}*miles + {receipt_rate}*receipts:')
        print(f'    Exact matches: {exact_matches}')
        print(f'    Close matches (< $1): {close_matches}') 
        print(f'    Average error: ${avg_error:.2f}')

def look_for_conditional_logic(df):
    print('\n=== LOOKING FOR CONDITIONAL LOGIC PATTERNS ===')
    
    # Maybe different formulas apply based on trip characteristics
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Define different trip types and test separate formulas for each
    trip_types = [
        ('Short trips (1-2 days)', df['trip_duration_days'] <= 2),
        ('Medium trips (3-5 days)', df['trip_duration_days'].between(3, 5)),
        ('Long trips (6+ days)', df['trip_duration_days'] >= 6),
        ('Low mileage (<100 mi/day)', df['miles_per_day'] < 100),
        ('High mileage (>200 mi/day)', df['miles_per_day'] > 200),
        ('Low spending (<$100/day)', df['receipts_per_day'] < 100),
        ('High spending (>$200/day)', df['receipts_per_day'] > 200),
    ]
    
    for type_name, condition in trip_types:
        subset = df[condition]
        if len(subset) > 50:  # Only test if we have enough samples
            print(f'\n{type_name} ({len(subset)} cases):')
            
            # Test different formulas for this subset
            best_exact = 0
            best_formula = None
            
            for base in [80, 90, 100, 110, 120]:
                for mile_rate in [0.50, 0.55, 0.58, 0.60, 0.65]:
                    for receipt_rate in [0.70, 0.75, 0.80, 0.85, 0.90]:
                        calculated = subset['trip_duration_days'] * base + subset['miles_traveled'] * mile_rate + subset['total_receipts_amount'] * receipt_rate
                        
                        exact_matches = (abs(calculated - subset['expected_output']) < 0.01).sum()
                        if exact_matches > best_exact:
                            best_exact = exact_matches
                            best_formula = (base, mile_rate, receipt_rate)
                            
                            if exact_matches > 5:  # Only print if significant
                                avg_error = abs(calculated - subset['expected_output']).mean()
                                print(f'  {base} + {mile_rate}*miles + {receipt_rate}*receipts: {exact_matches} exact matches, avg error ${avg_error:.2f}')
            
            if best_formula:
                base, mile_rate, receipt_rate = best_formula
                print(f'  Best for this type: {base} + {mile_rate}*miles + {receipt_rate}*receipts ({best_exact} exact matches)')

def analyze_outliers_for_patterns(df):
    print('\n=== ANALYZING OUTLIERS FOR SPECIAL PATTERNS ===')
    
    # Test a simple base formula and look at cases that don't fit
    base_formula = df['trip_duration_days'] * 95 + df['miles_traveled'] * 0.55 + df['total_receipts_amount'] * 0.80
    df['base_error'] = abs(base_formula - df['expected_output'])
    
    # Look at cases that fit very well (might reveal the core formula)
    perfect_fits = df[df['base_error'] < 1.0]
    print(f'Cases that fit base formula very well ({len(perfect_fits)} cases):')
    if len(perfect_fits) > 0:
        print(f'  Trip length: {perfect_fits["trip_duration_days"].mean():.1f} ± {perfect_fits["trip_duration_days"].std():.1f}')
        print(f'  Miles: {perfect_fits["miles_traveled"].mean():.1f} ± {perfect_fits["miles_traveled"].std():.1f}')
        print(f'  Receipts: ${perfect_fits["total_receipts_amount"].mean():.2f} ± ${perfect_fits["total_receipts_amount"].std():.2f}')
    
    # Look at cases that don't fit at all (might have special rules)
    outliers = df[df['base_error'] > 500.0]
    print(f'\nCases that don\'t fit base formula at all ({len(outliers)} cases):')
    if len(outliers) > 0:
        print(f'  Trip length: {outliers["trip_duration_days"].mean():.1f} ± {outliers["trip_duration_days"].std():.1f}')
        print(f'  Miles: {outliers["miles_traveled"].mean():.1f} ± {outliers["miles_traveled"].std():.1f}')
        print(f'  Receipts: ${outliers["total_receipts_amount"].mean():.2f} ± ${outliers["total_receipts_amount"].std():.2f}')
        
        # Show some examples
        print('  Examples:')
        for i, row in outliers.head(5).iterrows():
            print(f'    {row["trip_duration_days"]}d, {row["miles_traveled"]}mi, ${row["total_receipts_amount"]:.2f} -> ${row["expected_output"]:.2f} (base calc: ${base_formula.iloc[i]:.2f})')

def test_interview_specific_patterns(df):
    print('\n=== TESTING INTERVIEW-SPECIFIC PATTERNS ===')
    
    # Test Kevin's specific theories
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Kevin's sweet spot: 5 days, 180+ miles/day, <$100/day spending
    sweet_spot = df[
        (df['trip_duration_days'] == 5) &
        (df['miles_per_day'] >= 180) &
        (df['receipts_per_day'] < 100)
    ]
    
    if len(sweet_spot) > 0:
        print(f'Kevin\'s sweet spot ({len(sweet_spot)} cases):')
        for base in [100, 105, 110, 115, 120]:
            for mile_rate in [0.55, 0.58, 0.60, 0.62]:
                for receipt_rate in [0.80, 0.85, 0.90]:
                    calculated = sweet_spot['trip_duration_days'] * base + sweet_spot['miles_traveled'] * mile_rate + sweet_spot['total_receipts_amount'] * receipt_rate
                    exact_matches = (abs(calculated - sweet_spot['expected_output']) < 0.01).sum()
                    
                    if exact_matches > 0:
                        print(f'  {base} + {mile_rate}*miles + {receipt_rate}*receipts: {exact_matches} exact matches')
    
    # Test Lisa's rounding theory
    df['receipt_last_two_digits'] = ((df['total_receipts_amount'] * 100).round() % 100).astype(int)
    
    print('\nTesting rounding patterns:')
    rounding_candidates = [49, 99, 0, 50]
    for digits in rounding_candidates:
        subset = df[df['receipt_last_two_digits'] == digits]
        if len(subset) > 5:
            # Test if these cases have a consistent formula
            for base in [90, 95, 100]:
                for mile_rate in [0.55, 0.58, 0.60]:
                    for receipt_rate in [0.80, 0.85, 0.90, 0.95]:  # Test slightly higher rates for "rounding up"
                        calculated = subset['trip_duration_days'] * base + subset['miles_traveled'] * mile_rate + subset['total_receipts_amount'] * receipt_rate
                        exact_matches = (abs(calculated - subset['expected_output']) < 0.01).sum()
                        
                        if exact_matches > 1:
                            print(f'  Receipts ending .{digits:02d}: {base} + {mile_rate}*miles + {receipt_rate}*receipts gives {exact_matches} exact matches')

def main():
    data, df = load_data()
    
    systematic_exact_search(df)
    test_most_promising_formulas(df)
    look_for_conditional_logic(df)
    analyze_outliers_for_patterns(df)
    test_interview_specific_patterns(df)

if __name__ == '__main__':
    main()