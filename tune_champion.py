#!/usr/bin/env python3
"""
Tune the champion model by analyzing actual vs predicted on public cases.
"""

import json
import numpy as np

# Load public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Load our current predictions
import subprocess

def get_current_prediction(days, miles, receipts):
    """Get prediction from current fast_champion.py"""
    result = subprocess.run(['python3', 'fast_champion.py', str(days), str(miles), str(receipts)], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        return float(result.stdout.strip())
    else:
        return 0.0

print("Analyzing current fast_champion performance...")

predictions = []
actuals = []
errors = []

for i, case in enumerate(cases[:100]):  # Sample first 100 for speed
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    expected = case['expected_output']
    
    predicted = get_current_prediction(days, miles, receipts)
    error = abs(predicted - expected)
    
    predictions.append(predicted)
    actuals.append(expected)
    errors.append(error)
    
    if i < 10:
        print(f"Case {i+1}: Days={days}, Miles={miles:.1f}, Receipts=${receipts:.2f}")
        print(f"  Expected=${expected:.2f}, Predicted=${predicted:.2f}, Error=${error:.2f}")

mae = np.mean(errors)
print(f"\\nCurrent MAE on sample: ${mae:.2f}")

# Analyze patterns
print(f"\\nError analysis:")
print(f"Mean error: ${np.mean(errors):.2f}")
print(f"Median error: ${np.median(errors):.2f}")
print(f"Max error: ${np.max(errors):.2f}")

# Look at systematic biases
pred_array = np.array(predictions)
actual_array = np.array(actuals)
bias = np.mean(pred_array - actual_array)
print(f"Systematic bias: ${bias:.2f} (positive = overestimating)")

# Find the worst cases
worst_indices = np.argsort(errors)[-10:]
print(f"\\nWorst cases:")
for idx in worst_indices:
    case = cases[idx]
    inp = case['input']
    print(f"Days={inp['trip_duration_days']}, Miles={inp['miles_traveled']:.0f}, Receipts=${inp['total_receipts_amount']:.0f}")
    print(f"  Expected=${actuals[idx]:.2f}, Predicted=${predictions[idx]:.2f}, Error=${errors[idx]:.2f}")

# Simple linear correction
from sklearn.linear_model import LinearRegression
lr = LinearRegression()
lr.fit(np.array(predictions).reshape(-1, 1), actual_array)

print(f"\\nLinear correction:")
print(f"Slope: {lr.coef_[0]:.4f}")
print(f"Intercept: {lr.intercept_:.2f}")
print(f"Corrected formula: actual = {lr.coef_[0]:.4f} * predicted + {lr.intercept_:.2f}")

# Test the correction
corrected_predictions = lr.predict(np.array(predictions).reshape(-1, 1))
corrected_mae = np.mean(np.abs(corrected_predictions - actual_array))
print(f"Corrected MAE: ${corrected_mae:.2f}")

# Generate improved formula
slope = lr.coef_[0]
intercept = lr.intercept_

improvement_code = f"""
# Add this correction to fast_champion.py:
# At the end of fast_predict function, before return:
prediction = prediction * {slope:.6f} + {intercept:.2f}
"""

print(improvement_code)

# Quick analysis of receipt patterns
print("\\nReceipt pattern analysis:")
for case, pred, actual in zip(cases[:20], predictions[:20], actuals[:20]):
    inp = case['input']
    receipts = inp['total_receipts_amount']
    inv_receipts = 1.0 / (1.0 + receipts)
    ratio = actual / pred if pred > 0 else 0
    print(f"Receipts=${receipts:6.2f}, inv_receipts={inv_receipts:.6f}, ratio={ratio:.3f}")