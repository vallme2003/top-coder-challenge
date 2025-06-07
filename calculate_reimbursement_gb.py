#!/usr/bin/env python3
import sys
import numpy as np
import joblib

# Load model once at module level for efficiency
model = joblib.load('gradient_boost_model.pkl')

def extract_features(days, miles, receipts):
    """Extract all features used by the model"""
    # Basic features
    mpd = miles / days if days > 0 else 0
    rpd = receipts / days if days > 0 else 0
    
    # Create feature vector
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
    
    return np.array(features).reshape(1, -1)

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """Calculate reimbursement using gradient boosting model"""
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Extract features
    features = extract_features(days, miles, receipts)
    
    # Predict
    prediction = model.predict(features)[0]
    
    return round(prediction, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement_gb.py <days> <miles> <receipts>")
        sys.exit(1)
    
    days = sys.argv[1]
    miles = sys.argv[2]
    receipts = sys.argv[3]
    
    result = calculate_reimbursement(days, miles, receipts)
    print(result)