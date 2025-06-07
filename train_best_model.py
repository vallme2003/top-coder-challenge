#!/usr/bin/env python3
import json
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
import joblib

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Prepare comprehensive features
X = []
y = []

for case in cases:
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    # Basic features
    mpd = miles / days if days > 0 else 0
    rpd = receipts / days if days > 0 else 0
    
    # Create extensive feature set
    features = [
        # Basic inputs
        days,
        miles,
        receipts,
        
        # Ratios
        mpd,
        rpd,
        
        # Polynomial features
        days ** 2,
        miles ** 2,
        receipts ** 2,
        days ** 3,
        
        # Interactions
        days * miles,
        days * receipts,
        miles * receipts,
        days * miles * receipts / 1000,  # Three-way interaction
        
        # Log transforms
        np.log1p(days),
        np.log1p(miles),
        np.log1p(receipts),
        
        # Inverse features (for capturing diminishing returns)
        1 / (1 + receipts),
        1 / (1 + miles),
        
        # Categorical indicators
        1 if days == 5 else 0,  # 5-day bonus
        1 if days >= 7 else 0,  # Long trip
        1 if receipts < 50 else 0,  # Small receipts
        1 if receipts > 1000 else 0,  # High receipts
        1 if 180 <= mpd <= 220 else 0,  # Optimal efficiency
        
        # Receipt buckets
        1 if 50 <= receipts < 200 else 0,
        1 if 200 <= receipts < 500 else 0,
        1 if 500 <= receipts < 1000 else 0,
        
        # Special features
        int(receipts * 100) % 100,  # Cents
        1 if int(receipts * 100) % 100 == 49 else 0,
        1 if int(receipts * 100) % 100 == 99 else 0,
        
        # Efficiency categories
        1 if mpd < 50 else 0,
        1 if 50 <= mpd < 100 else 0,
        1 if 100 <= mpd < 150 else 0,
        1 if mpd >= 150 else 0,
    ]
    
    X.append(features)
    y.append(case['expected_output'])

X = np.array(X)
y = np.array(y)

print(f"Training on {len(X)} samples with {X.shape[1]} features")

# Train gradient boosting model
model = GradientBoostingRegressor(
    n_estimators=500,
    learning_rate=0.01,
    max_depth=6,
    min_samples_split=10,
    min_samples_leaf=5,
    subsample=0.8,
    random_state=42
)

# Cross-validation
scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
print(f"Cross-validation MAE: ${-scores.mean():.2f} (+/- ${scores.std():.2f})")

# Train on full dataset
model.fit(X, y)

# Evaluate on training set
y_pred = model.predict(X)
mae = np.mean(np.abs(y_pred - y))
print(f"Training MAE: ${mae:.2f}")

# Feature importance
feature_names = [
    'days', 'miles', 'receipts', 'mpd', 'rpd',
    'days^2', 'miles^2', 'receipts^2', 'days^3',
    'days*miles', 'days*receipts', 'miles*receipts', '3way',
    'log_days', 'log_miles', 'log_receipts',
    '1/(1+receipts)', '1/(1+miles)',
    '5day', 'long_trip', 'small_receipts', 'high_receipts', 'optimal_eff',
    'receipts_50_200', 'receipts_200_500', 'receipts_500_1000',
    'cents', 'ends_49', 'ends_99',
    'mpd_<50', 'mpd_50_100', 'mpd_100_150', 'mpd_150+'
]

print("\nTop 15 most important features:")
importances = model.feature_importances_
for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:15]:
    print(f"  {name}: {imp:.4f}")

# Save model
joblib.dump(model, 'gradient_boost_model.pkl')
print("\nModel saved to gradient_boost_model.pkl")

# Generate code that doesn't need sklearn
print("\nGenerating hardcoded prediction function...")
print("This might take a moment for 500 trees...")