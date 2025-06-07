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

def improved_formula(row):
    """
    Based on the analysis, this appears to be the core algorithm:
    1. Base per-diem that decreases with trip length
    2. Tiered mileage rates (full rate up to a threshold, then reduced)
    3. Receipt reimbursement that varies dramatically based on spending per day
    """
    days = row['trip_duration_days']
    miles = row['miles_traveled']
    receipts = row['total_receipts_amount']
    
    # Base per-diem calculation - decreases with longer trips
    if days == 1:
        base_per_day = 120
    elif days == 2:
        base_per_day = 115  
    elif days == 3:
        base_per_day = 110
    elif days <= 5:
        base_per_day = 105
    elif days <= 7:
        base_per_day = 100
    elif days <= 10:
        base_per_day = 95
    else:
        base_per_day = 90
    
    base_amount = days * base_per_day
    
    # Mileage calculation - tiered system
    if miles <= 150:
        mileage_amount = miles * 0.58
    elif miles <= 400:
        mileage_amount = 150 * 0.58 + (miles - 150) * 0.50
    elif miles <= 800:
        mileage_amount = 150 * 0.58 + 250 * 0.50 + (miles - 400) * 0.42
    else:
        mileage_amount = 150 * 0.58 + 250 * 0.50 + 400 * 0.42 + (miles - 800) * 0.35
    
    # Receipt processing - heavily dependent on per-day spending
    receipts_per_day = receipts / days
    
    if receipts_per_day <= 30:
        # Very low receipts get a penalty (you should be spending something)
        receipt_amount = receipts * 0.2
    elif receipts_per_day <= 75:
        # Reasonable spending gets good treatment
        receipt_amount = receipts * 0.85
    elif receipts_per_day <= 125:
        # Moderate spending still good
        receipt_amount = receipts * 0.75
    elif receipts_per_day <= 200:
        # Higher spending gets reduced rate
        receipt_amount = receipts * 0.55
    elif receipts_per_day <= 300:
        # High spending gets penalties
        receipt_amount = receipts * 0.35
    else:
        # Very high spending gets severe penalties
        receipt_amount = receipts * 0.15
    
    return base_amount + mileage_amount + receipt_amount

def test_improved_formula(df):
    print('=== TESTING IMPROVED FORMULA ===')
    
    df['calculated'] = df.apply(improved_formula, axis=1)
    df['error'] = abs(df['calculated'] - df['expected_output'])
    
    exact_matches = (df['error'] < 0.01).sum()
    close_matches_1 = (df['error'] < 1.0).sum()
    close_matches_5 = (df['error'] < 5.0).sum()
    close_matches_10 = (df['error'] < 10.0).sum()
    avg_error = df['error'].mean()
    median_error = df['error'].median()
    
    print(f'Results:')
    print(f'  Exact matches (< $0.01): {exact_matches}')
    print(f'  Very close (< $1.00): {close_matches_1}')
    print(f'  Close (< $5.00): {close_matches_5}')
    print(f'  Good (< $10.00): {close_matches_10}')
    print(f'  Average error: ${avg_error:.2f}')
    print(f'  Median error: ${median_error:.2f}')
    
    # Show best matches
    print('\nBest matches:')
    best = df.nsmallest(15, 'error')
    for i, row in best.iterrows():
        print(f'  {row["trip_duration_days"]}d, {row["miles_traveled"]}mi, ${row["total_receipts_amount"]:.2f} -> Expected: ${row["expected_output"]:.2f}, Calc: ${row["calculated"]:.2f}, Error: ${row["error"]:.2f}')
    
    # Show worst matches to understand what we're missing
    print('\nWorst matches:')
    worst = df.nlargest(10, 'error')
    for i, row in worst.iterrows():
        print(f'  {row["trip_duration_days"]}d, {row["miles_traveled"]}mi, ${row["total_receipts_amount"]:.2f} -> Expected: ${row["expected_output"]:.2f}, Calc: ${row["calculated"]:.2f}, Error: ${row["error"]:.2f}')

def fine_tune_parameters(df):
    print('\n=== FINE-TUNING PARAMETERS ===')
    
    # Test slight variations of the parameters to find exact matches
    best_exact_matches = 0
    best_params = None
    
    # Test base per-day rates
    for base_adjust in [-5, -2, 0, 2, 5]:
        # Test mileage tier thresholds  
        for tier1_thresh in [140, 150, 160]:
            for tier1_rate in [0.56, 0.58, 0.60]:
                for tier2_rate in [0.48, 0.50, 0.52]:
                    # Test receipt thresholds
                    for receipt_thresh1 in [70, 75, 80]:
                        for receipt_rate1 in [0.80, 0.85, 0.90]:
                            
                            def test_formula(row):
                                days = row['trip_duration_days']
                                miles = row['miles_traveled']
                                receipts = row['total_receipts_amount']
                                
                                # Adjusted base rates
                                if days == 1:
                                    base_per_day = 120 + base_adjust
                                elif days == 2:
                                    base_per_day = 115 + base_adjust
                                elif days == 3:
                                    base_per_day = 110 + base_adjust
                                elif days <= 5:
                                    base_per_day = 105 + base_adjust
                                elif days <= 7:
                                    base_per_day = 100 + base_adjust
                                elif days <= 10:
                                    base_per_day = 95 + base_adjust
                                else:
                                    base_per_day = 90 + base_adjust
                                
                                base_amount = days * base_per_day
                                
                                # Adjusted mileage tiers
                                if miles <= tier1_thresh:
                                    mileage_amount = miles * tier1_rate
                                elif miles <= 400:
                                    mileage_amount = tier1_thresh * tier1_rate + (miles - tier1_thresh) * tier2_rate
                                elif miles <= 800:
                                    mileage_amount = tier1_thresh * tier1_rate + (400 - tier1_thresh) * tier2_rate + (miles - 400) * 0.42
                                else:
                                    mileage_amount = tier1_thresh * tier1_rate + (400 - tier1_thresh) * tier2_rate + 400 * 0.42 + (miles - 800) * 0.35
                                
                                # Adjusted receipt processing
                                receipts_per_day = receipts / days
                                
                                if receipts_per_day <= 30:
                                    receipt_amount = receipts * 0.2
                                elif receipts_per_day <= receipt_thresh1:
                                    receipt_amount = receipts * receipt_rate1
                                elif receipts_per_day <= 125:
                                    receipt_amount = receipts * 0.75
                                elif receipts_per_day <= 200:
                                    receipt_amount = receipts * 0.55
                                elif receipts_per_day <= 300:
                                    receipt_amount = receipts * 0.35
                                else:
                                    receipt_amount = receipts * 0.15
                                
                                return base_amount + mileage_amount + receipt_amount
                            
                            calculated = df.apply(test_formula, axis=1)
                            exact_matches = (abs(calculated - df['expected_output']) < 0.01).sum()
                            
                            if exact_matches > best_exact_matches:
                                best_exact_matches = exact_matches
                                best_params = {
                                    'base_adjust': base_adjust,
                                    'tier1_thresh': tier1_thresh,
                                    'tier1_rate': tier1_rate,
                                    'tier2_rate': tier2_rate,
                                    'receipt_thresh1': receipt_thresh1,
                                    'receipt_rate1': receipt_rate1
                                }
                                
                                if exact_matches > 5:  # Only print promising results
                                    avg_error = abs(calculated - df['expected_output']).mean()
                                    print(f'  Found {exact_matches} exact matches with params: {best_params}, avg error: ${avg_error:.2f}')
    
    print(f'\nBest configuration found: {best_exact_matches} exact matches')
    print(f'Best parameters: {best_params}')

def analyze_remaining_patterns(df):
    print('\n=== ANALYZING REMAINING PATTERNS ===')
    
    # Apply our best formula and look at the residuals
    df['calculated'] = df.apply(improved_formula, axis=1)
    df['residual'] = df['expected_output'] - df['calculated']
    
    # Look for patterns in the residuals
    print('Residual patterns by trip characteristics:')
    
    # By trip length
    for days in range(1, 8):
        subset = df[df['trip_duration_days'] == days]
        if len(subset) > 10:
            avg_residual = subset['residual'].mean()
            std_residual = subset['residual'].std()
            print(f'  {days}-day trips: avg residual ${avg_residual:.2f} ± ${std_residual:.2f}')
    
    # By receipt ending (test the rounding theory)
    df['receipt_cents'] = ((df['total_receipts_amount'] * 100).round() % 100).astype(int)
    
    for cents in [0, 25, 49, 50, 75, 99]:
        subset = df[df['receipt_cents'] == cents]
        if len(subset) > 5:
            avg_residual = subset['residual'].mean()
            print(f'  Receipts ending .{cents:02d}: avg residual ${avg_residual:.2f} ({len(subset)} cases)')

def main():
    data, df = load_data()
    
    test_improved_formula(df)
    fine_tune_parameters(df)
    analyze_remaining_patterns(df)

if __name__ == '__main__':
    main()