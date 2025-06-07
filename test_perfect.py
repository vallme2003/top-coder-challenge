#!/usr/bin/env python3
"""
Test the perfect score attempt against some public cases
"""

import json
import subprocess
import numpy as np

# Load some public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

def get_prediction(script, days, miles, receipts):
    """Get prediction from a script"""
    try:
        if script == "current":
            result = subprocess.run(['./run.sh', str(days), str(miles), str(receipts)], 
                                  capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(['python3', 'perfect_score_attempt.py', str(days), str(miles), str(receipts)], 
                                  capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            return float(result.stdout.strip())
        else:
            print(f"Error running {script}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception running {script}: {e}")
        return None

print("Testing Perfect Score Attempt vs Current Model")
print("=" * 60)

# Test on first 20 cases for speed
test_cases = cases[:20]
current_errors = []
perfect_errors = []

for i, case in enumerate(test_cases):
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    expected = case['expected_output']
    
    current_pred = get_prediction("current", days, miles, receipts)
    perfect_pred = get_prediction("perfect", days, miles, receipts)
    
    if current_pred is not None and perfect_pred is not None:
        current_error = abs(current_pred - expected)
        perfect_error = abs(perfect_pred - expected)
        
        current_errors.append(current_error)
        perfect_errors.append(perfect_error)
        
        print(f"Case {i+1}: {days}d, {miles:.0f}mi, ${receipts:.2f}")
        print(f"  Expected: ${expected:.2f}")
        print(f"  Current:  ${current_pred:.2f} (error: ${current_error:.2f})")
        print(f"  Perfect:  ${perfect_pred:.2f} (error: ${perfect_error:.2f})")
        
        if perfect_error < current_error:
            print("  ✅ Perfect is better!")
        elif current_error < perfect_error:
            print("  ❌ Current is better")
        else:
            print("  ➖ Same performance")
        print()

if current_errors and perfect_errors:
    print("Summary Results:")
    print(f"Current Model - Average Error: ${np.mean(current_errors):.2f}")
    print(f"Perfect Model - Average Error: ${np.mean(perfect_errors):.2f}")
    
    perfect_wins = sum(1 for i in range(len(current_errors)) if perfect_errors[i] < current_errors[i])
    current_wins = sum(1 for i in range(len(current_errors)) if current_errors[i] < perfect_errors[i])
    
    print(f"Perfect model wins: {perfect_wins}/{len(test_cases)} cases")
    print(f"Current model wins: {current_wins}/{len(test_cases)} cases")
    
    if np.mean(perfect_errors) < np.mean(current_errors):
        print("\n🎯 Perfect model shows improvement! Consider switching.")
    else:
        print("\n📊 Current model still better on average. Perfect model needs refinement.")