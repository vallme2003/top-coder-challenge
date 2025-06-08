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

print("=== FINAL FORMULA ATTEMPT ===")

# Since I'm getting 11.5% exact matches with the linear formula, maybe the exact formula
# is a lookup table or has exact business rules

# Let me analyze the 115 exact matches to see if there's a pattern
days_coefficient = 62.839410
receipts_coefficient = 0.436038
miles_coefficient = 0.579790

df['predicted'] = days_coefficient * df['days'] + receipts_coefficient * df['receipts'] + miles_coefficient * df['miles']
df['error'] = abs(df['predicted'] - df['output'])

exact_matches = df[df['error'] < 0.01]
print(f"Analyzing {len(exact_matches)} exact matches...")

print("\nExact matches by trip duration:")
for days in sorted(exact_matches['days'].unique()):
    day_matches = exact_matches[exact_matches['days'] == days]
    print(f"  {days:2.0f} days: {len(day_matches):3d} matches")

print("\nExact matches by receipt ranges:")
for low, high in [(0, 100), (100, 500), (500, 1000), (1000, 2000), (2000, 3000)]:
    range_matches = exact_matches[(exact_matches['receipts'] >= low) & (exact_matches['receipts'] < high)]
    print(f"  ${low}-${high}: {len(range_matches):3d} matches")

# Since there are exact matches, maybe the formula is correct for certain ranges
# but needs adjustments for others

# Let me check if the exact formula might be different for different trip lengths
print(f"\n=== TESTING TRIP-LENGTH-SPECIFIC FORMULAS ===")

best_overall_error = float('inf')
best_overall_formula = None

for target_days in sorted(df['days'].unique()):
    day_data = df[df['days'] == target_days]
    if len(day_data) >= 10:  # Only test if we have enough data
        
        # Fit a specific formula for this trip length
        X = day_data[['receipts', 'miles']].values
        y = day_data['output'].values
        
        # Add constant term
        X_with_const = np.column_stack([X, np.ones(len(X))])
        
        try:
            coeffs = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
            
            # Test this formula on all data of this trip length
            predicted_day = X_with_const @ coeffs
            errors_day = abs(predicted_day - y)
            
            print(f"{target_days:2.0f} days: receipts={coeffs[0]:.6f}, miles={coeffs[1]:.6f}, constant={coeffs[2]:.6f}")
            print(f"          max error: {errors_day.max():.6f}, perfect matches: {(errors_day < 0.01).sum()}")
            
            if errors_day.max() < 0.01:
                print(f"          *** EXACT FORMULA FOR {target_days} DAYS! ***")
                
        except:
            continue

# Maybe it's a multiplicative formula
print(f"\n=== TESTING MULTIPLICATIVE FORMULAS ===")

# Test: output = (a + b * receipts) * (c + d * days) + e * miles
best_mult_error = float('inf')

for a in range(0, 101, 20):
    for b in [0.1, 0.2, 0.3, 0.4, 0.5]:
        for c in range(1, 11, 2):
            for d in range(10, 51, 10):
                for e in [0, 0.1, 0.2, 0.3, 0.4, 0.5]:
                    try:
                        predicted_mult = (a + b * df['receipts']) * (c + d * df['days']) + e * df['miles']
                        max_error_mult = abs(predicted_mult - df['output']).max()
                        
                        if max_error_mult < best_mult_error:
                            best_mult_error = max_error_mult
                            if max_error_mult < 100:  # Good enough to report
                                print(f"({a} + {b}*receipts) * ({c} + {d}*days) + {e}*miles -> max error: {max_error_mult:.3f}")
                        
                        if max_error_mult < 0.01:
                            print(f"*** EXACT MULTIPLICATIVE FORMULA: ({a} + {b}*receipts) * ({c} + {d}*days) + {e}*miles ***")
                    except:
                        continue

# Let me try one more approach - maybe it's a lookup table based on rounded values
print(f"\n=== TESTING LOOKUP TABLE HYPOTHESIS ===")

# Maybe the inputs are rounded to certain values before calculation
def test_rounded_inputs():
    # Test rounding receipts to nearest $10, $50, $100
    for round_receipts in [10, 50, 100]:
        df[f'rounded_receipts_{round_receipts}'] = np.round(df['receipts'] / round_receipts) * round_receipts
        
        X = df[['days', f'rounded_receipts_{round_receipts}', 'miles']].values
        y = df['output'].values
        
        coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
        predicted_rounded = X @ coeffs
        errors_rounded = abs(predicted_rounded - y)
        
        perfect_matches = (errors_rounded < 0.01).sum()
        if perfect_matches > 115:  # Better than current
            print(f"Rounding receipts to ${round_receipts}: {perfect_matches} perfect matches")
            print(f"  Coefficients: days={coeffs[0]:.6f}, receipts={coeffs[1]:.6f}, miles={coeffs[2]:.6f}")

test_rounded_inputs()

# One final attempt - maybe there are integer coefficients
print(f"\n=== TESTING INTEGER COEFFICIENTS ===")

# Test simple integer coefficients
best_int_error = float('inf')
best_int_formula = None

for days_coeff in range(50, 101):
    for receipts_coeff_int in range(30, 61):  # 0.30 to 0.60 as integers/100
        for miles_coeff_int in range(40, 81):  # 0.40 to 0.80 as integers/100
            receipts_coeff = receipts_coeff_int / 100.0
            miles_coeff = miles_coeff_int / 100.0
            
            predicted_int = days_coeff * df['days'] + receipts_coeff * df['receipts'] + miles_coeff * df['miles']
            max_error_int = abs(predicted_int - df['output']).max()
            perfect_matches_int = (abs(predicted_int - df['output']) < 0.01).sum()
            
            if max_error_int < best_int_error:
                best_int_error = max_error_int
                best_int_formula = (days_coeff, receipts_coeff, miles_coeff)
            
            if perfect_matches_int > 115:  # Better than current
                print(f"Integer formula: {days_coeff} * days + {receipts_coeff:.2f} * receipts + {miles_coeff:.2f} * miles")
                print(f"  Perfect matches: {perfect_matches_int}, Max error: {max_error_int:.6f}")
            
            if max_error_int < 0.01:
                print(f"*** EXACT INTEGER FORMULA: {days_coeff} * days + {receipts_coeff:.2f} * receipts + {miles_coeff:.2f} * miles ***")

print(f"\nBest integer formula found:")
if best_int_formula:
    days_c, receipts_c, miles_c = best_int_formula
    print(f"Formula: {days_c} * days + {receipts_c:.2f} * receipts + {miles_c:.2f} * miles")
    print(f"Max error: {best_int_error:.6f}")

# Since I can't find the exact formula, let me at least optimize the current approach
print(f"\n=== OPTIMIZING CURRENT APPROACH ===")

# Use the log receipts approach which had the lowest max error
df['log_receipts'] = np.log(df['receipts'] + 1)
X_log = df[['days', 'log_receipts', 'miles']].values
coeffs_log = np.linalg.lstsq(X_log, df['output'].values, rcond=None)[0]

print(f"Best formula for implementation:")
print(f"output = {coeffs_log[0]:.6f} * days + {coeffs_log[1]:.6f} * log(receipts + 1) + {coeffs_log[2]:.6f} * miles")

predicted_final = X_log @ coeffs_log
errors_final = abs(predicted_final - df['output'])
print(f"Max error: {errors_final.max():.6f}")
print(f"Mean error: {errors_final.mean():.6f}")
print(f"Perfect matches: {(errors_final < 0.01).sum()}")

print("\nSaving final attempt results...")
df['predicted_final'] = predicted_final
df['error_final'] = errors_final
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/final_attempt_results.csv', index=False)