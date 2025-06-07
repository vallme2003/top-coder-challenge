#!/usr/bin/env python3
import json
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Try different hypothesis for the formula
print("Testing different formula hypotheses:\n")

# Hypothesis 1: Simple linear combination
print("1. Linear: output = a*days + b*miles + c*receipts + d")
X = []
y = []
for case in cases:
    inp = case['input']
    X.append([inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'], 1])
    y.append(case['expected_output'])

X = np.array(X)
y = np.array(y)

model = LinearRegression()
model.fit(X, y)
pred = model.predict(X)
mae = np.mean(np.abs(pred - y))
print(f"   Coefficients: days={model.coef_[0]:.2f}, miles={model.coef_[1]:.2f}, receipts={model.coef_[2]:.2f}, intercept={model.coef_[3]:.2f}")
print(f"   MAE: ${mae:.2f}")

# Hypothesis 2: Per diem + mileage rate + receipt percentage
print("\n2. Classic travel: output = days*per_diem + miles*rate + receipts*percentage")
# This is essentially the same as above, just different interpretation

# Hypothesis 3: Include efficiency (miles/day)
print("\n3. With efficiency: includes miles/day")
X = []
for case in cases:
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    mpd = miles / days if days > 0 else 0
    X.append([days, miles, receipts, mpd, 1])

X = np.array(X)
model = LinearRegression()
model.fit(X, y)
pred = model.predict(X)
mae = np.mean(np.abs(pred - y))
print(f"   MAE: ${mae:.2f}")

# Hypothesis 4: Separate models for different trip lengths
print("\n4. Different models by trip length:")
for max_days in [3, 7, 14]:
    indices = [i for i, case in enumerate(cases) if case['input']['trip_duration_days'] <= max_days]
    if len(indices) > 10:
        X_subset = X[indices]
        y_subset = y[indices]
        model = LinearRegression()
        model.fit(X_subset, y_subset)
        pred = model.predict(X_subset)
        mae = np.mean(np.abs(pred - y_subset))
        print(f"   Days <= {max_days}: MAE=${mae:.2f}, n={len(indices)}")

# Hypothesis 5: Polynomial features
print("\n5. Polynomial (degree 2) features:")
poly_model = Pipeline([
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
    ('linear', Ridge(alpha=0.1))
])

X_simple = []
for case in cases:
    inp = case['input']
    X_simple.append([inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']])

X_simple = np.array(X_simple)
poly_model.fit(X_simple, y)
pred = poly_model.predict(X_simple)
mae = np.mean(np.abs(pred - y))
print(f"   MAE: ${mae:.2f}")

# Hypothesis 6: Look for patterns in residuals
print("\n6. Analyzing patterns in simple linear model residuals:")
X = []
for case in cases:
    inp = case['input']
    X.append([inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount']])

X = np.array(X)
model = LinearRegression()
model.fit(X, y)
pred = model.predict(X)
residuals = y - pred

# Group by characteristics
print("   Average residuals by trip length:")
for days in range(1, 15):
    indices = [i for i, case in enumerate(cases) if case['input']['trip_duration_days'] == days]
    if indices:
        avg_residual = np.mean(residuals[indices])
        print(f"     {days} days: ${avg_residual:.2f} (n={len(indices)})")

print("\n   Average residuals by receipt ranges:")
ranges = [(0, 50), (50, 200), (200, 500), (500, 1000), (1000, 3000)]
for low, high in ranges:
    indices = [i for i, case in enumerate(cases) 
               if low <= case['input']['total_receipts_amount'] < high]
    if indices:
        avg_residual = np.mean(residuals[indices])
        print(f"     ${low}-${high}: ${avg_residual:.2f} (n={len(indices)})")

# Hypothesis 7: Piecewise linear for receipts
print("\n7. Testing receipt caps/tiers:")
for case in cases[:20]:
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    output = case['expected_output']
    
    # Calculate base (without receipts)
    base = days * 100 + miles * 0.5  # Rough estimate
    receipt_portion = output - base
    receipt_rate = receipt_portion / receipts if receipts > 0 else 0
    
    print(f"   Receipts=${receipts:.2f}, Output=${output:.2f}, Base≈${base:.2f}, Receipt rate={receipt_rate:.3f}")