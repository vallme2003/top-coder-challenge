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

def reverse_engineer_from_outliers(df):
    print('=== REVERSE ENGINEERING FROM OUTLIERS ===')
    
    # The outliers suggest there are penalty systems for high spending
    # Let's look at the pattern more carefully
    
    # High ratio cases suggest bonuses for efficiency
    high_ratios = df.nlargest(20, 'expected_output')
    print('Highest output cases:')
    for i, row in high_ratios.head(10).iterrows():
        days = row['trip_duration_days']
        miles = row['miles_traveled']
        receipts = row['total_receipts_amount']
        output = row['expected_output']
        miles_per_day = miles / days
        receipts_per_day = receipts / days
        
        print(f'  {days}d, {miles}mi ({miles_per_day:.1f}/day), ${receipts:.2f} (${receipts_per_day:.2f}/day) -> ${output:.2f}')
    
    print('\nLow ratio cases (penalties):')
    # These cases have very high receipts relative to output - clear penalties
    penalty_cases = df[(df['total_receipts_amount'] > 1000) & (df['expected_output'] < 800)]
    for i, row in penalty_cases.head(10).iterrows():
        days = row['trip_duration_days']
        miles = row['miles_traveled'] 
        receipts = row['total_receipts_amount']
        output = row['expected_output']
        receipts_per_day = receipts / days
        
        print(f'  {days}d, {miles}mi, ${receipts:.2f} (${receipts_per_day:.2f}/day) -> ${output:.2f}')

def test_base_plus_bonuses_penalties(df):
    print('\n=== TESTING BASE + BONUSES/PENALTIES SYSTEM ===')
    
    # Start with a base formula and add corrections
    def calculate_base_reimbursement(row):
        days = row['trip_duration_days']
        miles = row['miles_traveled']
        receipts = row['total_receipts_amount']
        
        # Base per diem (this seems to vary by trip length)
        if days == 1:
            base_per_day = 120
        elif days <= 3:
            base_per_day = 115
        elif days <= 5:
            base_per_day = 110
        elif days <= 7:
            base_per_day = 105
        else:
            base_per_day = 100
            
        base_amount = days * base_per_day
        
        # Mileage - appears to be tiered
        if miles <= 100:
            mileage_amount = miles * 0.58
        elif miles <= 300:
            mileage_amount = 100 * 0.58 + (miles - 100) * 0.52
        elif miles <= 600:
            mileage_amount = 100 * 0.58 + 200 * 0.52 + (miles - 300) * 0.45
        else:
            mileage_amount = 100 * 0.58 + 200 * 0.52 + 300 * 0.45 + (miles - 600) * 0.35
        
        # Receipts - strong penalties for high amounts
        receipts_per_day = receipts / days
        if receipts_per_day <= 50:
            receipt_amount = receipts * 0.9
        elif receipts_per_day <= 100:
            receipt_amount = receipts * 0.8
        elif receipts_per_day <= 200:
            receipt_amount = receipts * 0.6
        elif receipts_per_day <= 300:
            receipt_amount = receipts * 0.4
        else:
            receipt_amount = receipts * 0.2  # Heavy penalty
        
        return base_amount + mileage_amount + receipt_amount
    
    df['calculated'] = df.apply(calculate_base_reimbursement, axis=1)
    df['error'] = abs(df['calculated'] - df['expected_output'])
    
    exact_matches = (df['error'] < 0.01).sum()
    close_matches = (df['error'] < 5.0).sum()
    avg_error = df['error'].mean()
    
    print(f'Tiered system results:')
    print(f'  Exact matches (< $0.01): {exact_matches}')
    print(f'  Close matches (< $5.00): {close_matches}')
    print(f'  Average error: ${avg_error:.2f}')
    
    # Show some examples
    print('\nBest matches:')
    best_matches = df.nsmallest(10, 'error')
    for i, row in best_matches.iterrows():
        print(f'  {row["trip_duration_days"]}d, {row["miles_traveled"]}mi, ${row["total_receipts_amount"]:.2f} -> Expected: ${row["expected_output"]:.2f}, Calculated: ${row["calculated"]:.2f}, Error: ${row["error"]:.2f}')

def analyze_receipt_penalty_structure(df):
    print('\n=== ANALYZING RECEIPT PENALTY STRUCTURE ===')
    
    # Group by spending levels to see the penalty pattern
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    spending_ranges = [
        (0, 50),
        (50, 100),
        (100, 150),
        (150, 200),
        (200, 300),
        (300, 500),
        (500, 1000),
        (1000, 10000)
    ]
    
    for min_spend, max_spend in spending_ranges:
        subset = df[(df['receipts_per_day'] >= min_spend) & (df['receipts_per_day'] < max_spend)]
        if len(subset) > 5:
            # Calculate what the "receipt rate" appears to be
            # by comparing the output to a base calculation
            base_calc = subset['trip_duration_days'] * 110 + subset['miles_traveled'] * 0.50
            receipt_contribution = subset['expected_output'] - base_calc
            apparent_rate = (receipt_contribution / subset['total_receipts_amount']).mean()
            
            print(f'  ${min_spend}-${max_spend}/day: {len(subset)} cases, apparent receipt rate: {apparent_rate:.2f}')

def test_specific_interview_claims(df):
    print('\n=== TESTING SPECIFIC INTERVIEW CLAIMS ===')
    
    # Test Kevin's specific claims about sweet spots
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Kevin's sweet spot: 180-220 miles per day
    sweet_spot_miles = df[(df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)]
    other_miles = df[(df['miles_per_day'] < 180) | (df['miles_per_day'] > 220)]
    
    if len(sweet_spot_miles) > 0 and len(other_miles) > 0:
        sweet_avg = sweet_spot_miles['expected_output'].mean()
        other_avg = other_miles['expected_output'].mean()
        print(f'Sweet spot mileage (180-220 mi/day): {len(sweet_spot_miles)} cases, avg ${sweet_avg:.2f}')
        print(f'Other mileage: {len(other_miles)} cases, avg ${other_avg:.2f}')
    
    # Test the 5-day bonus claim
    five_day = df[df['trip_duration_days'] == 5]
    four_six_day = df[df['trip_duration_days'].isin([4, 6])]
    
    if len(five_day) > 0 and len(four_six_day) > 0:
        five_per_day = five_day['expected_output'].mean() / 5
        four_six_per_day = four_six_day['expected_output'].mean() / four_six_day['trip_duration_days'].mean()
        print(f'5-day trips: avg ${five_per_day:.2f}/day')
        print(f'4&6-day trips: avg ${four_six_per_day:.2f}/day')
        print(f'Difference: ${five_per_day - four_six_per_day:.2f}/day')
    
    # Test receipt ending patterns (Lisa's rounding bug theory)
    df['receipt_cents'] = ((df['total_receipts_amount'] * 100).round() % 100).astype(int)
    
    lucky_cents = df[df['receipt_cents'].isin([49, 99])]
    other_cents = df[~df['receipt_cents'].isin([49, 99])]
    
    if len(lucky_cents) > 0 and len(other_cents) > 0:
        lucky_avg = lucky_avg = lucky_cents['expected_output'].mean()
        other_avg = other_cents['expected_output'].mean()
        print(f'Receipts ending in .49/.99: {len(lucky_cents)} cases, avg ${lucky_avg:.2f}')
        print(f'Other endings: {len(other_cents)} cases, avg ${other_avg:.2f}')

def find_exact_formula_pieces(df):
    print('\n=== FINDING EXACT FORMULA PIECES ===')
    
    # Focus on very simple cases to reverse engineer the base formula
    simple_cases = df[
        (df['trip_duration_days'] <= 3) &
        (df['miles_traveled'] <= 200) &
        (df['total_receipts_amount'] <= 100)
    ]
    
    print(f'Analyzing {len(simple_cases)} simple cases to find base formula...')
    
    # For each simple case, try to determine what the components must be
    for i, row in simple_cases.head(20).iterrows():
        days = row['trip_duration_days']
        miles = row['miles_traveled']
        receipts = row['total_receipts_amount']
        output = row['expected_output']
        
        # If we assume the formula is: days * base_rate + miles * mile_rate + receipts * receipt_rate
        # We can try different combinations
        
        # Try base rate of 120 per day
        remaining_after_days = output - (days * 120)
        
        # Try 0.58 per mile
        remaining_after_miles = remaining_after_days - (miles * 0.58)
        
        # What would the receipt rate need to be?
        if receipts > 0:
            implied_receipt_rate = remaining_after_miles / receipts
            print(f'  {days}d, {miles}mi, ${receipts:.2f} -> ${output:.2f}: implied receipt rate {implied_receipt_rate:.3f}')

def main():
    data, df = load_data()
    
    # Add calculated columns
    df['total_inputs'] = df['trip_duration_days'] * 100 + df['miles_traveled'] * 0.58 + df['total_receipts_amount'] * 0.8
    df['output_ratio'] = df['expected_output'] / df['total_inputs']
    
    reverse_engineer_from_outliers(df)
    test_base_plus_bonuses_penalties(df)
    analyze_receipt_penalty_structure(df)
    test_specific_interview_claims(df)
    find_exact_formula_pieces(df)

if __name__ == '__main__':
    main()