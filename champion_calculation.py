#!/usr/bin/env python3
"""
Champion calculation script using the best performing RandomForest model.
This model achieved MAE of 73.37 on cross-validation, targeting a score < 8,000.
"""

import sys
import numpy as np
import joblib
import math
import warnings
warnings.filterwarnings('ignore')

# Global model variables - loaded once for efficiency
model = None
feature_cols = None

def load_champion_model():
    """Load the champion model and feature columns"""
    global model, feature_cols
    try:
        model = joblib.load('champion_model.pkl')
        feature_cols = joblib.load('feature_columns.pkl')
        return True
    except:
        return False

def create_features(days, miles, receipts):
    """
    Create the exact same features used in training the champion model.
    This must match the feature engineering in advanced_analysis.py exactly.
    """
    # Convert to float to ensure consistency
    days = float(days)
    miles = float(miles)
    receipts = float(receipts)
    
    features = {}
    
    # Basic inputs
    features['days'] = days
    features['miles'] = miles
    features['receipts'] = receipts
    
    # Basic ratios
    features['mpd'] = miles / days if days > 0 else 0
    features['rpd'] = receipts / days if days > 0 else 0
    
    # Logarithmic transforms
    features['log_days'] = math.log1p(days)
    features['log_miles'] = math.log1p(miles)
    features['log_receipts'] = math.log1p(receipts)
    
    # Inverse relationships (most important feature!)
    features['inv_receipts'] = 1 / (1 + receipts)
    features['inv_miles'] = 1 / (1 + miles)
    
    # Polynomial features
    features['days_sq'] = days ** 2
    features['miles_sq'] = miles ** 2
    features['receipts_sq'] = receipts ** 2
    
    # Interaction terms (very important)
    features['days_miles'] = days * miles
    features['days_receipts'] = days * receipts
    features['miles_receipts'] = miles * receipts
    features['three_way'] = days * miles * receipts
    
    # Categorical features
    features['is_5_days'] = 1 if days == 5 else 0
    features['is_weekend'] = 1 if (int(days) % 7) < 2 else 0
    features['is_week'] = 1 if days == 7 else 0
    
    # Receipt patterns (important for accuracy)
    cents = int(round(receipts * 100)) % 100
    features['cents'] = float(cents)
    features['ends_49'] = 1 if cents == 49 else 0
    features['ends_99'] = 1 if cents == 99 else 0
    
    # Efficiency buckets
    mpd = features['mpd']
    features['low_efficiency'] = 1 if mpd < 50 else 0
    features['med_efficiency'] = 1 if 50 <= mpd < 150 else 0
    features['high_efficiency'] = 1 if mpd >= 150 else 0
    
    # Receipt buckets
    features['low_receipts'] = 1 if receipts < 100 else 0
    features['med_receipts'] = 1 if 100 <= receipts < 500 else 0
    features['high_receipts'] = 1 if receipts >= 500 else 0
    
    return features

def champion_predict(days, miles, receipts):
    """
    Make prediction using the champion RandomForest model.
    
    Args:
        days: Trip duration in days
        miles: Miles traveled
        receipts: Total receipt amount
        
    Returns:
        Predicted reimbursement amount
    """
    global model, feature_cols
    
    if model is None or feature_cols is None:
        raise RuntimeError("Champion model not loaded")
    
    # Create features
    features = create_features(days, miles, receipts)
    
    # Create feature vector in the exact order expected by the model
    feature_vector = []
    for col in feature_cols:
        if col in features:
            feature_vector.append(features[col])
        else:
            feature_vector.append(0.0)  # Default value for missing features
    
    # Make prediction
    X = np.array(feature_vector).reshape(1, -1)
    prediction = model.predict(X)[0]
    
    return round(prediction, 2)

def fallback_calculation(days, miles, receipts):
    """
    Fallback calculation if champion model fails.
    Uses a simplified but still effective approach.
    """
    days = int(days)
    miles = float(miles)
    receipts = float(receipts)
    
    # Key features from analysis
    inv_receipts = 1 / (1 + receipts)
    three_way = days * miles * receipts
    days_receipts = days * receipts
    days_miles = days * miles
    
    # Simplified model based on feature importance
    base = 200 + days * 75  # Base per diem
    
    # Inverse receipts effect (most important)
    inv_effect = inv_receipts * 800
    
    # Three-way interaction effect
    three_way_effect = three_way / 10000 * 50
    
    # Days-receipts interaction
    days_receipts_effect = days_receipts / 1000 * 15
    
    # Days-miles interaction
    days_miles_effect = days_miles / 100 * 8
    
    # Receipt square effect
    receipts_sq_effect = (receipts ** 2) / 1000000 * 30
    
    # Special bonuses
    bonus = 0
    if days == 5:
        bonus += 25
    
    cents = int(round(receipts * 100)) % 100
    if cents == 49:
        bonus += 5
    if cents == 99:
        bonus += 5
    
    total = (base + inv_effect + three_way_effect + 
             days_receipts_effect + days_miles_effect + 
             receipts_sq_effect + bonus)
    
    return round(total, 2)

def calculate_reimbursement(days, miles, receipts):
    """
    Main calculation function - tries champion model, falls back if needed.
    """
    try:
        # Try champion model first
        return champion_predict(days, miles, receipts)
    except Exception as e:
        # Fall back to simplified calculation
        print(f"Champion model failed: {e}, using fallback", file=sys.stderr)
        return fallback_calculation(days, miles, receipts)

def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: champion_calculation.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = sys.argv[1]
        miles = sys.argv[2]
        receipts = sys.argv[3]
        
        # Load champion model
        if not load_champion_model():
            print("Warning: Could not load champion model, using fallback", file=sys.stderr)
        
        result = calculate_reimbursement(days, miles, receipts)
        print(result)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()