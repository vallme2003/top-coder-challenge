#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd
import math

# Load the data
with open('/Users/vthenappan/Documents/GitHub/top-coder-challenge/public_cases.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame([{
    'days': case['input']['trip_duration_days'],
    'miles': case['input']['miles_traveled'], 
    'receipts': case['input']['total_receipts_amount'],
    'output': case['expected_output']
} for case in data])

print("=== FINAL FORMULA SEARCH ===")

# From the day pattern analysis, I can see that the effective day rates follow a pattern
# Let me try to find the exact mathematical relationship

# The day rates I found were:
day_rates = {
    1: 246.48, 2: 184.37, 3: 133.96, 4: 120.03, 5: 121.66, 6: 118.00, 7: 110.67,
    8: 88.80, 9: 83.58, 10: 75.62, 11: 73.52, 12: 69.29, 13: 72.21, 14: 66.94
}

# Let me test if these follow a specific mathematical pattern
days_list = sorted(day_rates.keys())
rates_list = [day_rates[d] for d in days_list]

print("Looking for mathematical pattern in day rates...")

# Test various functions
def test_function(func_name, func, params_ranges):
    print(f"\nTesting {func_name}:")
    best_error = float('inf')
    best_params = None
    
    # Generate all parameter combinations
    param_combinations = []
    if len(params_ranges) == 1:
        for p1 in params_ranges[0]:
            param_combinations.append((p1,))
    elif len(params_ranges) == 2:
        for p1 in params_ranges[0]:
            for p2 in params_ranges[1]:
                param_combinations.append((p1, p2))
    elif len(params_ranges) == 3:
        for p1 in params_ranges[0]:
            for p2 in params_ranges[1]:
                for p3 in params_ranges[2]:
                    param_combinations.append((p1, p2, p3))
    
    for params in param_combinations:
        try:
            errors = []
            for days in days_list:
                predicted_rate = func(days, *params)
                actual_rate = day_rates[days]
                errors.append(abs(predicted_rate - actual_rate))
            
            max_error = max(errors)
            if max_error < best_error:
                best_error = max_error
                best_params = params
                
            if max_error < 1.0:  # Very good fit
                print(f"  Params {params}: max error {max_error:.6f}")
                
        except:
            continue
    
    if best_params:
        print(f"  Best: {best_params}, max error: {best_error:.6f}")
        return best_params, best_error
    return None, float('inf')

# Test a/days + b
def func1(days, a, b):
    return a / days + b

# Test a - b * log(days)  
def func2(days, a, b):
    return a - b * math.log(days)

# Test a * days^(-b) + c
def func3(days, a, b, c):
    return a * (days ** (-b)) + c

# Test the functions
params1, error1 = test_function("a/days + b", func1, 
                                [range(100, 301, 10), range(50, 151, 5)])

params2, error2 = test_function("a - b*log(days)", func2,
                                [range(200, 301, 5), range(30, 71, 2)])

params3, error3 = test_function("a * days^(-b) + c", func3,
                                [range(100, 251, 10), [0.5, 0.6, 0.7, 0.8, 0.9, 1.0], range(50, 101, 5)])

# Use the best function to create the complete formula
best_functions = [(params1, error1, func1, "a/days + b"),
                  (params2, error2, func2, "a - b*log(days)"),
                  (params3, error3, func3, "a * days^(-b) + c")]

best_functions.sort(key=lambda x: x[1])
best_params, best_error, best_func, best_name = best_functions[0]

print(f"\nBest day rate function: {best_name}")
print(f"Parameters: {best_params}")
print(f"Max error: {best_error:.6f}")

# Now test the complete formula with this day rate function
def test_complete_formula():
    print(f"\n=== TESTING COMPLETE FORMULA ===")
    
    # Test various receipt and mile factors with the best day rate function
    best_overall_error = float('inf')
    best_overall_params = None
    
    for receipt_factor in [0.40, 0.41, 0.42, 0.43, 0.44, 0.45]:
        for mile_factor in [0.30, 0.35, 0.40, 0.45, 0.50]:
            predicted_outputs = []
            
            for _, row in df.iterrows():
                days = row['days']
                
                # Calculate day rate using best function
                day_rate = best_func(days, *best_params)
                
                base_component = day_rate * days
                receipt_component = receipt_factor * row['receipts']
                mile_component = mile_factor * row['miles']
                
                predicted = base_component + receipt_component + mile_component
                predicted_outputs.append(predicted)
            
            errors = [abs(pred - actual) for pred, actual in zip(predicted_outputs, df['output'])]
            max_error = max(errors)
            mean_error = sum(errors) / len(errors)
            
            if max_error < best_overall_error:
                best_overall_error = max_error
                best_overall_params = (receipt_factor, mile_factor)
            
            if max_error < 5.0:  # Good results
                print(f"Receipt: {receipt_factor:.2f}, Mile: {mile_factor:.2f} -> Max error: {max_error:.6f}, Mean: {mean_error:.6f}")
    
    print(f"\nBest overall: Receipt {best_overall_params[0]:.2f}, Mile {best_overall_params[1]:.2f}")
    print(f"Best max error: {best_overall_error:.6f}")
    
    # Test the best combination
    receipt_factor, mile_factor = best_overall_params
    predicted_outputs = []
    
    for _, row in df.iterrows():
        days = row['days']
        day_rate = best_func(days, *best_params)
        
        base_component = day_rate * days
        receipt_component = receipt_factor * row['receipts']
        mile_component = mile_factor * row['miles']
        
        predicted = base_component + receipt_component + mile_component
        predicted_outputs.append(predicted)
    
    df['predicted_final'] = predicted_outputs
    df['error_final'] = abs(df['predicted_final'] - df['output'])
    
    print(f"\nFinal formula results:")
    print(f"Day rate function: {best_name} with params {best_params}")
    print(f"Receipt factor: {receipt_factor}")
    print(f"Mile factor: {mile_factor}")
    print(f"Max error: {df['error_final'].max():.6f}")
    print(f"Mean error: {df['error_final'].mean():.6f}")
    print(f"Perfect matches (error < 0.01): {(df['error_final'] < 0.01).sum()}")
    print(f"Very close (error < 0.1): {(df['error_final'] < 0.1).sum()}")
    print(f"Close (error < 1.0): {(df['error_final'] < 1.0).sum()}")
    
    # Show the exact formula
    if best_name == "a/days + b":
        a, b = best_params
        print(f"\nEXACT FORMULA:")
        print(f"output = ({a}/days + {b}) * days + {receipt_factor} * receipts + {mile_factor} * miles")
        print(f"output = {a} + {b} * days + {receipt_factor} * receipts + {mile_factor} * miles")
    elif best_name == "a - b*log(days)":
        a, b = best_params
        print(f"\nEXACT FORMULA:")
        print(f"output = ({a} - {b} * log(days)) * days + {receipt_factor} * receipts + {mile_factor} * miles")
    elif best_name == "a * days^(-b) + c":
        a, b, c = best_params
        print(f"\nEXACT FORMULA:")
        print(f"output = ({a} * days^(-{b}) + {c}) * days + {receipt_factor} * receipts + {mile_factor} * miles")
    
    if df['error_final'].max() < 0.01:
        print(f"\n*** EXACT ANALYTICAL FORMULA FOUND! ***")
    
    return receipt_factor, mile_factor

test_complete_formula()

print("\nSaving final results...")
df.to_csv('/Users/vthenappan/Documents/GitHub/top-coder-challenge/final_formula_results.csv', index=False)