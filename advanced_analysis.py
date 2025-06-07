#!/usr/bin/env python3
"""
Advanced analysis to beat the top leaderboard scores.
Focus on finding the exact mathematical formula through systematic analysis.
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print(f"Analyzing {len(cases)} public cases to beat score of 8,891.41")

# Convert to DataFrame for easier analysis
data = []
for case in cases:
    inp = case['input']
    data.append({
        'days': inp['trip_duration_days'],
        'miles': inp['miles_traveled'],
        'receipts': inp['total_receipts_amount'],
        'output': case['expected_output']
    })

df = pd.DataFrame(data)

print("\nBasic statistics:")
print(df.describe())

# Create comprehensive features
def create_features(df):
    features = df.copy()
    
    # Basic ratios
    features['mpd'] = features['miles'] / features['days']
    features['rpd'] = features['receipts'] / features['days']
    
    # Logarithmic transforms
    features['log_days'] = np.log1p(features['days'])
    features['log_miles'] = np.log1p(features['miles'])
    features['log_receipts'] = np.log1p(features['receipts'])
    
    # Inverse relationships (key insight from earlier analysis)
    features['inv_receipts'] = 1 / (1 + features['receipts'])
    features['inv_miles'] = 1 / (1 + features['miles'])
    
    # Polynomial features
    features['days_sq'] = features['days'] ** 2
    features['miles_sq'] = features['miles'] ** 2
    features['receipts_sq'] = features['receipts'] ** 2
    
    # Interaction terms
    features['days_miles'] = features['days'] * features['miles']
    features['days_receipts'] = features['days'] * features['receipts']
    features['miles_receipts'] = features['miles'] * features['receipts']
    features['three_way'] = features['days'] * features['miles'] * features['receipts']
    
    # Categorical features
    features['is_5_days'] = (features['days'] == 5).astype(int)
    features['is_weekend'] = ((features['days'] % 7) < 2).astype(int)
    features['is_week'] = (features['days'] == 7).astype(int)
    
    # Receipt patterns
    features['cents'] = (features['receipts'] * 100) % 100
    features['ends_49'] = (features['cents'] == 49).astype(int)
    features['ends_99'] = (features['cents'] == 99).astype(int)
    
    # Efficiency buckets
    features['low_efficiency'] = (features['mpd'] < 50).astype(int)
    features['med_efficiency'] = ((features['mpd'] >= 50) & (features['mpd'] < 150)).astype(int)
    features['high_efficiency'] = (features['mpd'] >= 150).astype(int)
    
    # Receipt buckets
    features['low_receipts'] = (features['receipts'] < 100).astype(int)
    features['med_receipts'] = ((features['receipts'] >= 100) & (features['receipts'] < 500)).astype(int)
    features['high_receipts'] = (features['receipts'] >= 500).astype(int)
    
    return features

# Create feature matrix
feature_df = create_features(df)
feature_cols = [col for col in feature_df.columns if col != 'output']
X = feature_df[feature_cols].values
y = feature_df['output'].values

print(f"\nCreated {len(feature_cols)} features")

# Test multiple models
models = {
    'Linear': LinearRegression(),
    'Ridge': Ridge(alpha=1.0),
    'RandomForest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
    'GradientBoosting': GradientBoostingRegressor(n_estimators=300, max_depth=8, learning_rate=0.1, random_state=42),
    'Polynomial': Pipeline([
        ('poly', PolynomialFeatures(degree=2, interaction_only=True)),
        ('ridge', Ridge(alpha=0.1))
    ])
}

best_model = None
best_score = float('inf')
best_name = ""

print("\nTesting models:")
for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
    mae = -scores.mean()
    std = scores.std()
    print(f"{name:15s}: MAE = {mae:7.2f} (+/- {std:5.2f})")
    
    if mae < best_score:
        best_score = mae
        best_model = model
        best_name = name

print(f"\nBest model: {best_name} with MAE: {best_score:.2f}")

# Train best model on full dataset
best_model.fit(X, y)

# Analyze feature importance
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    feature_importance = list(zip(feature_cols, importances))
    feature_importance.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nTop 15 features for {best_name}:")
    for feature, importance in feature_importance[:15]:
        print(f"{feature:20s}: {importance:.4f}")

# Look for patterns in errors
predictions = best_model.predict(X)
errors = np.abs(predictions - y)
df['predicted'] = predictions
df['error'] = errors

print(f"\nError analysis:")
print(f"Mean error: ${np.mean(errors):.2f}")
print(f"Median error: ${np.median(errors):.2f}")
print(f"90th percentile: ${np.percentile(errors, 90):.2f}")
print(f"Max error: ${np.max(errors):.2f}")

# Find worst cases
worst_indices = np.argsort(errors)[-10:]
print(f"\nWorst 10 cases:")
for i in worst_indices:
    row = df.iloc[i]
    print(f"Days={int(row['days']):2d}, Miles={row['miles']:6.1f}, Receipts=${row['receipts']:7.2f}, Expected=${row['output']:7.2f}, Predicted=${row['predicted']:7.2f}, Error=${row['error']:6.2f}")

# Look for systematic patterns in errors
print(f"\nError patterns by trip length:")
for days in range(1, 15):
    subset = df[df['days'] == days]
    if len(subset) > 0:
        mean_error = subset['error'].mean()
        print(f"{days:2d} days: {len(subset):3d} cases, avg error: ${mean_error:6.2f}")

print(f"\nError patterns by receipt ranges:")
receipt_ranges = [(0, 100), (100, 300), (300, 500), (500, 1000), (1000, 2000), (2000, 5000)]
for low, high in receipt_ranges:
    subset = df[(df['receipts'] >= low) & (df['receipts'] < high)]
    if len(subset) > 0:
        mean_error = subset['error'].mean()
        print(f"${low:4d}-${high:4d}: {len(subset):3d} cases, avg error: ${mean_error:6.2f}")

# Save the best model for use in production
import joblib
joblib.dump(best_model, 'champion_model.pkl')
joblib.dump(feature_cols, 'feature_columns.pkl')

print(f"\nSaved best model ({best_name}) to champion_model.pkl")
print(f"Expected score improvement: ~{(13112 - best_score * 100):.0f} points")

# Quick validation on a few cases
print(f"\nQuick validation on first 5 cases:")
for i in range(5):
    row = df.iloc[i]
    print(f"Expected: ${row['output']:7.2f}, Predicted: ${row['predicted']:7.2f}, Error: ${row['error']:6.2f}")