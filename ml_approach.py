#!/usr/bin/env python3
import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Prepare features and targets
X = []
y = []

for case in cases:
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    # Create features
    features = [
        days,
        miles,
        receipts,
        miles / days if days > 0 else 0,  # miles per day
        receipts / days if days > 0 else 0,  # receipts per day
        days ** 2,  # quadratic terms
        miles ** 2,
        receipts ** 2,
        days * miles,  # interaction terms
        days * receipts,
        miles * receipts,
        1 if days == 5 else 0,  # 5-day indicator
        1 if receipts < 50 else 0,  # small receipt indicator
        1 if receipts > 1000 else 0,  # high receipt indicator
        np.log1p(miles),  # log transforms
        np.log1p(receipts),
        int(receipts * 100) % 100,  # cents portion
        1 if int(receipts * 100) % 100 == 49 else 0,  # ends in 49
        1 if int(receipts * 100) % 100 == 99 else 0,  # ends in 99
    ]
    
    X.append(features)
    y.append(case['expected_output'])

X = np.array(X)
y = np.array(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error on test set: ${mae:.2f}")

# Feature importance
feature_names = [
    'days', 'miles', 'receipts', 'mpd', 'rpd', 
    'days^2', 'miles^2', 'receipts^2',
    'days*miles', 'days*receipts', 'miles*receipts',
    '5day', 'small_receipt', 'high_receipt',
    'log_miles', 'log_receipts', 'cents',
    'ends_49', 'ends_99'
]

importances = model.feature_importances_
for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
    print(f"{name}: {imp:.4f}")

# Save model
joblib.dump(model, 'reimbursement_model.pkl')

# Test on full dataset
y_pred_full = model.predict(X)
errors = np.abs(y_pred_full - y)
print(f"\nFull dataset MAE: ${np.mean(errors):.2f}")
print(f"Exact matches (within $0.01): {np.sum(errors <= 0.01)}")
print(f"Close matches (within $1.00): {np.sum(errors <= 1.00)}")

# Save predictions for analysis
predictions = []
for i, case in enumerate(cases):
    predictions.append({
        'input': case['input'],
        'expected': case['expected_output'],
        'predicted': float(y_pred_full[i]),
        'error': float(errors[i])
    })

# Find worst predictions
worst = sorted(predictions, key=lambda x: x['error'], reverse=True)[:10]
print("\nWorst predictions:")
for p in worst:
    inp = p['input']
    print(f"Days={inp['trip_duration_days']}, Miles={inp['miles_traveled']}, Receipts={inp['total_receipts_amount']:.2f}")
    print(f"  Expected: ${p['expected']:.2f}, Predicted: ${p['predicted']:.2f}, Error: ${p['error']:.2f}")