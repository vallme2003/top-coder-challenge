#!/usr/bin/env python3
import sys
import numpy as np
import joblib

def extract_features(days, miles, receipts):
    """Extract features for ML model"""
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
    return np.array(features).reshape(1, -1)

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """Calculate reimbursement using ML model"""
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Load model
    model = joblib.load('reimbursement_model.pkl')
    
    # Extract features
    features = extract_features(days, miles, receipts)
    
    # Predict
    prediction = model.predict(features)[0]
    
    return round(prediction, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement_ml.py <days> <miles> <receipts>")
        sys.exit(1)
    
    days = sys.argv[1]
    miles = sys.argv[2]
    receipts = sys.argv[3]
    
    result = calculate_reimbursement(days, miles, receipts)
    print(result)