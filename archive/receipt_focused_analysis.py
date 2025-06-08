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

print("=== RECEIPT-FOCUSED ANALYSIS ===")

# Since receipts have the highest correlation (0.704), let's focus on that relationship
# Maybe the formula is simpler than I thought

# Let me check if output is approximately equal to receipts * some_factor
print("Testing if output ≈ receipts * factor:")

df['receipt_factor'] = df['output'] / df['receipts']
print(f"Receipt factor (output/receipts) statistics:")
print(f"  Mean: {df['receipt_factor'].mean():.3f}")
print(f"  Median: {df['receipt_factor'].median():.3f}")
print(f"  Std: {df['receipt_factor'].std():.3f}")
print(f"  Min: {df['receipt_factor'].min():.3f}")
print(f"  Max: {df['receipt_factor'].max():.3f}")

# Look at the distribution
print(f"\nReceipt factor percentiles:")
for p in [10, 25, 50, 75, 90, 95, 99]:
    val = np.percentile(df['receipt_factor'], p)
    print(f"  {p:2d}th percentile: {val:.3f}")

# The variation is huge (std dev of ~10), so it's not just receipts * constant
# But maybe there's a base component plus receipts

# Let me test: output = base + receipts * factor
print(f"\n=== TESTING OUTPUT = BASE + RECEIPTS * FACTOR ===")

# If output = base + receipts * factor, then:
# (output - receipts * factor) should be approximately constant (the base)

for factor in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]:
    residuals = df['output'] - df['receipts'] * factor
    residual_std = residuals.std()
    residual_mean = residuals.mean()
    print(f"Factor {factor:.1f}: Base = {residual_mean:7.2f} ± {residual_std:6.2f}")

# Let me also test per-day base: output = base_per_day * days + receipts * factor
print(f"\n=== TESTING OUTPUT = BASE_PER_DAY * DAYS + RECEIPTS * FACTOR ===")

for factor in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    df[f'residual_{factor}'] = (df['output'] - df['receipts'] * factor) / df['days']
    residual_std = df[f'residual_{factor}'].std()
    residual_mean = df[f'residual_{factor}'].mean()
    print(f"Factor {factor:.1f}: Base per day = {residual_mean:7.2f} ± {residual_std:6.2f}")

# The 0.7 factor looks promising (lowest std dev)
# Let me examine this more closely

factor = 0.7
df['base_per_day'] = (df['output'] - df['receipts'] * factor) / df['days']

print(f"\nWith receipts factor {factor}, analyzing base per day by trip length:")
for days in sorted(df['days'].unique()):
    day_data = df[df['days'] == days]
    if len(day_data) >= 5:
        mean_base = day_data['base_per_day'].mean()
        std_base = day_data['base_per_day'].std()
        print(f"  {days:2d} days: base = {mean_base:6.2f} ± {std_base:5.2f} ({len(day_data):3d} cases)")

# Let me see if this gives us good predictions
print(f"\n=== TESTING REFINED FORMULA ===")

# Use the pattern I see: base decreases with longer trips
# Let me use a simple lookup for now
day_bases = {
    1: 246, 2: 184, 3: 134, 4: 120, 5: 122, 6: 118, 7: 111,
    8: 89, 9: 84, 10: 76, 11: 74, 12: 69, 13: 72, 14: 67
}

def test_lookup_formula():
    predicted_outputs = []
    receipt_factor = 0.7
    
    for _, row in df.iterrows():
        days = row['days']
        base_rate = day_bases.get(days, 100)  # fallback to 100 if day not in lookup
        
        predicted = base_rate * days + receipt_factor * row['receipts']
        predicted_outputs.append(predicted)
    
    df['predicted_lookup'] = predicted_outputs
    df['error_lookup'] = abs(df['predicted_lookup'] - df['output'])
    
    print(f"Lookup table formula (base_per_day[days] * days + 0.7 * receipts):")
    print(f"  Max error: {df['error_lookup'].max():.3f}")
    print(f"  Mean error: {df['error_lookup'].mean():.3f}")
    print(f"  Perfect matches (error < 0.01): {(df['error_lookup'] < 0.01).sum()}")
    print(f"  Very close (error < 0.1): {(df['error_lookup'] < 0.1).sum()}")
    print(f"  Close (error < 1.0): {(df['error_lookup'] < 1.0).sum()}")

test_lookup_formula()

# Maybe I need to include miles in a simple way
print(f"\n=== ADDING MILES COMPONENT ===")

def test_three_component_simple():
    best_error = float('inf')
    best_params = None
    
    # Test simple integer-like values
    for receipt_factor in [0.6, 0.65, 0.7, 0.75, 0.8]:
        for mile_factor in [0.1, 0.2, 0.3, 0.4, 0.5]:
            predicted_outputs = []
            
            for _, row in df.iterrows():
                days = row['days']
                base_rate = day_bases.get(days, 100)
                
                predicted = base_rate * days + receipt_factor * row['receipts'] + mile_factor * row['miles']
                predicted_outputs.append(predicted)
            
            errors = [abs(pred - actual) for pred, actual in zip(predicted_outputs, df['output'])]
            max_error = max(errors)
            mean_error = sum(errors) / len(errors)
            
            if max_error < best_error:
                best_error = max_error
                best_params = (receipt_factor, mile_factor)
            
            if max_error < 100:  # Reasonable results
                print(f"  Receipt: {receipt_factor:.2f}, Mile: {mile_factor:.2f} -> Max: {max_error:.3f}, Mean: {mean_error:.3f}")
    
    print(f"\nBest: Receipt {best_params[0]:.2f}, Mile {best_params[1]:.2f}, Max error: {best_error:.3f}")
    return best_params

best_receipt, best_mile = test_three_component_simple()

# Let me try to find the exact formula by testing more precisely around the best values
print(f"\n=== PRECISE SEARCH AROUND BEST VALUES ===")

def precise_search():
    best_error = float('inf')
    best_formula = None
    
    # Test precise values around the best
    receipt_range = np.arange(best_receipt - 0.05, best_receipt + 0.06, 0.01)
    mile_range = np.arange(best_mile - 0.05, best_mile + 0.06, 0.01)
    
    for receipt_factor in receipt_range:
        for mile_factor in mile_range:
            predicted_outputs = []
            
            for _, row in df.iterrows():
                days = row['days']
                base_rate = day_bases.get(days, 100)
                
                predicted = base_rate * days + receipt_factor * row['receipts'] + mile_factor * row['miles']
                predicted_outputs.append(predicted)
            
            errors = [abs(pred - actual) for pred, actual in zip(predicted_outputs, df['output'])]
            max_error = max(errors)
            
            if max_error < best_error:
                best_error = max_error
                best_formula = (receipt_factor, mile_factor)
            
            if max_error < 0.1:  # Very precise
                print(f"VERY PRECISE: Receipt {receipt_factor:.3f}, Mile {mile_factor:.3f} -> Max error: {max_error:.6f}")
    
    if best_formula:
        receipt_factor, mile_factor = best_formula
        print(f"\nBest precise formula found:")
        print(f"Receipt factor: {receipt_factor:.3f}")
        print(f"Mile factor: {mile_factor:.3f}")
        print(f"Max error: {best_error:.6f}")
        
        if best_error < 0.01:
            print(f"\n*** EXACT FORMULA FOUND! ***")
            print(f"Formula: lookup_base_per_day[days] * days + {receipt_factor:.3f} * receipts + {mile_factor:.3f} * miles")
            print(f"Where lookup_base_per_day = {day_bases}")

precise_search()

print("\nSaving receipt-focused analysis...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/receipt_focused_results.csv', index=False)