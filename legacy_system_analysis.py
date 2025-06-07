#!/usr/bin/env python3
import json
import pandas as pd
import numpy as np
from collections import defaultdict
import math

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

def analyze_legacy_quirks_and_bugs(df):
    print('=== ANALYZING POTENTIAL LEGACY QUIRKS AND BUGS ===')
    
    # Look for patterns that suggest legacy computation artifacts
    
    # 1. Floating point precision issues
    df['output_cents'] = ((df['expected_output'] * 100).round() % 100).astype(int)
    print('Output cent distribution (looking for precision artifacts):')
    cent_counts = df['output_cents'].value_counts().head(10)
    for cents, count in cent_counts.items():
        print(f'  Ends in .{cents:02d}: {count} cases')
    
    # 2. Rounding patterns that suggest old algorithms
    print('\nLooking for rounding patterns:')
    # Check if outputs are consistent with specific rounding rules
    for divisor in [5, 10, 25, 50]:
        rounded_outputs = (df['expected_output'] / divisor).round() * divisor
        exact_matches = (abs(rounded_outputs - df['expected_output']) < 0.01).sum()
        print(f'  Outputs exactly divisible by {divisor}: {exact_matches} cases')
    
    # 3. Look for fixed amounts that appear suspiciously often
    print('\nMost common exact output amounts (potential hardcoded values):')
    output_counts = df['expected_output'].value_counts().head(10)
    for amount, count in output_counts.items():
        if count > 1:
            print(f'  ${amount:.2f}: appears {count} times')

def test_legacy_computation_patterns(df):
    print('\n=== TESTING LEGACY COMPUTATION PATTERNS ===')
    
    # Maybe the system uses integer arithmetic or fixed-point math
    # which could explain inconsistencies
    
    # Test if the system might be doing integer calculations
    def test_integer_based_formula(row):
        days = int(row['trip_duration_days'])
        miles = int(row['miles_traveled'])  # Truncate to integer
        receipts_cents = int(row['total_receipts_amount'] * 100)  # Convert to cents
        
        # Try integer-based calculations that get converted back to dollars
        # This is how old systems often worked to avoid floating point issues
        
        base_cents = days * 10000  # $100 per day in cents
        mile_cents = miles * 58    # $0.58 per mile in cents
        receipt_cents = receipts_cents * 80 // 100  # 80% of receipts, integer division
        
        total_cents = base_cents + mile_cents + receipt_cents
        return total_cents / 100.0  # Convert back to dollars
    
    df['integer_calc'] = df.apply(test_integer_based_formula, axis=1)
    df['integer_error'] = abs(df['integer_calc'] - df['expected_output'])
    
    exact_matches = (df['integer_error'] < 0.01).sum()
    close_matches = (df['integer_error'] < 1.0).sum()
    print(f'Integer-based calculation results:')
    print(f'  Exact matches: {exact_matches}')
    print(f'  Close matches (< $1): {close_matches}')
    print(f'  Average error: ${df["integer_error"].mean():.2f}')

def look_for_lookup_tables_or_brackets(df):
    print('\n=== LOOKING FOR LOOKUP TABLES OR TAX BRACKET-STYLE SYSTEMS ===')
    
    # Old systems often used lookup tables or bracket systems
    # Look for evidence of stepped/bracketed calculations
    
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    df['output_per_day'] = df['expected_output'] / df['trip_duration_days']
    
    # Look for clustering in output per day values (suggests brackets)
    print('Output per day clustering (suggests bracket system):')
    output_per_day_rounded = (df['output_per_day'] / 10).round() * 10  # Round to nearest $10
    clusters = output_per_day_rounded.value_counts().head(10)
    for amount, count in clusters.items():
        if count > 5:
            print(f'  Around ${amount:.0f}/day: {count} cases')
    
    # Test if there are clear breakpoints in reimbursement rates
    print('\nTesting for bracket breakpoints:')
    
    # Sort by total inputs and look for sudden changes in output ratio
    df['total_input_estimate'] = df['trip_duration_days'] * 100 + df['miles_traveled'] * 0.5 + df['total_receipts_amount'] * 0.7
    df['output_ratio'] = df['expected_output'] / df['total_input_estimate']
    
    df_sorted = df.sort_values('total_input_estimate')
    
    # Look for sudden changes in ratio (suggests bracket boundaries)
    for i in range(100, len(df_sorted) - 100, 100):
        before_ratio = df_sorted.iloc[i-50:i]['output_ratio'].mean()
        after_ratio = df_sorted.iloc[i:i+50]['output_ratio'].mean()
        
        if abs(before_ratio - after_ratio) > 0.1:  # Significant change
            boundary_value = df_sorted.iloc[i]['total_input_estimate']
            print(f'  Potential bracket boundary around ${boundary_value:.0f}: ratio changes from {before_ratio:.3f} to {after_ratio:.3f}')

def test_calendar_or_external_factors(df):
    print('\n=== TESTING FOR CALENDAR OR EXTERNAL FACTOR INFLUENCES ===')
    
    # The interviews mentioned timing effects - maybe the system uses some external factors
    # Since we don't have dates, we can't test calendar effects directly,
    # but we can look for patterns that suggest external influences
    
    # Test if there are "random" variations that could be external factors
    # Group by identical inputs and see if outputs vary
    input_groups = df.groupby(['trip_duration_days', 'miles_traveled', 'total_receipts_amount'])
    
    varying_outputs = []
    for inputs, group in input_groups:
        if len(group) > 1:  # Multiple cases with identical inputs
            output_std = group['expected_output'].std()
            if output_std > 0.01:  # Outputs vary
                varying_outputs.append({
                    'inputs': inputs,
                    'count': len(group),
                    'outputs': group['expected_output'].tolist(),
                    'std': output_std
                })
    
    print(f'Cases with identical inputs but different outputs: {len(varying_outputs)}')
    if varying_outputs:
        print('Examples (suggests randomness or external factors):')
        for case in varying_outputs[:5]:
            days, miles, receipts = case['inputs']
            print(f'  {days}d, {miles}mi, ${receipts:.2f} -> outputs: {[f"${x:.2f}" for x in case["outputs"]]} (std: ${case["std"]:.2f})')

def test_legacy_algorithm_patterns(df):
    print('\n=== TESTING LEGACY ALGORITHM PATTERNS ===')
    
    # Test patterns that were common in old business systems
    
    # 1. Multiple calculation methods based on ranges
    def legacy_style_calculation(row):
        days = row['trip_duration_days']
        miles = row['miles_traveled']
        receipts = row['total_receipts_amount']
        
        # Method selection based on trip characteristics (common in old systems)
        if days == 1:
            # Single day calculation
            base = 120
            mile_rate = 0.58 if miles <= 200 else 0.50
            receipt_rate = 0.80 if receipts <= 100 else 0.60
        elif days <= 5:
            # Short trip calculation
            base = 100
            mile_rate = 0.55 if miles <= 300 else 0.45
            receipt_rate = 0.75 if receipts <= 500 else 0.50
        else:
            # Long trip calculation
            base = 90
            mile_rate = 0.50 if miles <= 500 else 0.40
            receipt_rate = 0.70 if receipts <= 1000 else 0.30
        
        return days * base + miles * mile_rate + receipts * receipt_rate
    
    df['legacy_calc'] = df.apply(legacy_style_calculation, axis=1)
    df['legacy_error'] = abs(df['legacy_calc'] - df['expected_output'])
    
    exact_matches = (df['legacy_error'] < 0.01).sum()
    close_matches = (df['legacy_error'] < 10.0).sum()
    
    print(f'Legacy-style multi-method calculation:')
    print(f'  Exact matches: {exact_matches}')
    print(f'  Close matches (< $10): {close_matches}')
    print(f'  Average error: ${df["legacy_error"].mean():.2f}')

def extract_exact_business_rules(df):
    print('\n=== EXTRACTING EXACT BUSINESS RULES FROM BEST MATCHES ===')
    
    # Focus on the cases where we got very close matches and try to extract rules
    df['total_error'] = 999999  # Initialize with large error
    
    # Test the best formula variations we found earlier
    formula_variations = [
        (90, 0.50, 0.70),
        (95, 0.55, 0.75),
        (100, 0.58, 0.80),
        (85, 0.60, 0.85),
        (110, 0.52, 0.78),
    ]
    
    for base, mile_rate, receipt_rate in formula_variations:
        calculated = df['trip_duration_days'] * base + df['miles_traveled'] * mile_rate + df['total_receipts_amount'] * receipt_rate
        error = abs(calculated - df['expected_output'])
        
        # Keep track of the best match for each case
        better_mask = error < df['total_error']
        df.loc[better_mask, 'total_error'] = error[better_mask]
        df.loc[better_mask, 'best_formula'] = f"{base}+{mile_rate}*mi+{receipt_rate}*rec"
    
    # Analyze which cases work well with which formulas
    print('Formula effectiveness by case characteristics:')
    
    for formula in df['best_formula'].unique():
        if pd.notna(formula):
            subset = df[df['best_formula'] == formula]
            good_matches = subset[subset['total_error'] < 5.0]
            
            if len(good_matches) > 10:
                print(f'\n{formula} works well for {len(good_matches)} cases:')
                print(f'  Days: {good_matches["trip_duration_days"].mean():.1f} ± {good_matches["trip_duration_days"].std():.1f}')
                print(f'  Miles: {good_matches["miles_traveled"].mean():.1f} ± {good_matches["miles_traveled"].std():.1f}')
                print(f'  Receipts: ${good_matches["total_receipts_amount"].mean():.2f} ± ${good_matches["total_receipts_amount"].std():.2f}')
                print(f'  Average error: ${good_matches["total_error"].mean():.2f}')

def main():
    data, df = load_data()
    
    analyze_legacy_quirks_and_bugs(df)
    test_legacy_computation_patterns(df)
    look_for_lookup_tables_or_brackets(df)
    test_calendar_or_external_factors(df)
    test_legacy_algorithm_patterns(df)
    extract_exact_business_rules(df)

if __name__ == '__main__':
    main()