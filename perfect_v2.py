#!/usr/bin/env python3
"""
Perfect Score V2 - Based on systematic pattern analysis
Key insights:
1. Different coefficient sets for different cases
2. Single-day trips cluster around $150 bucket
3. Multiple calculation paths based on trip characteristics
"""

import sys
import math

def perfect_v2_predict(days, miles, receipts):
    """
    Version 2 of perfect score attempt
    Based on systematic analysis of exact formulas found
    """
    days = float(days)
    miles = float(miles)
    receipts = float(receipts)
    
    # Key metrics
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    # From pattern analysis: Different coefficient sets found
    # Case 6: 110*days + 0.6*miles + 0.2*receipts (single day, medium miles)
    # Case 19: 90*days + 0.5*miles + 0.7*receipts (2 days, medium setup)
    
    # Decision tree based on exact patterns found
    
    # Path 1: Single day trips (cluster around $150)
    if days == 1:
        if miles <= 80 and receipts <= 20:
            # Pattern similar to case 6: low receipts, medium miles
            prediction = 110 * days + 0.6 * miles + 0.2 * receipts
        elif miles > 80 and receipts <= 50:
            # Medium single day trip
            prediction = 120 * days + 0.5 * miles + 0.3 * receipts
        else:
            # High mileage or receipts single day
            prediction = 100 * days + 0.4 * miles + 0.4 * receipts
    
    # Path 2: Two day trips 
    elif days == 2:
        if miles <= 200 and receipts <= 50:
            # Pattern similar to case 19: medium setup
            prediction = 90 * days + 0.5 * miles + 0.7 * receipts
        elif receipts_per_day <= 25:
            # Low spending two day trip
            prediction = 95 * days + 0.55 * miles + 0.6 * receipts
        else:
            # Higher spending two day trip
            prediction = 85 * days + 0.45 * miles + 0.5 * receipts
    
    # Path 3: Short trips (3-5 days)
    elif days <= 5:
        if days == 3 and receipts <= 30:
            # 3-day low spending (common pattern)
            prediction = 100 * days + 0.6 * miles + 0.3 * receipts
        elif days == 5:
            # 5-day trip special handling
            prediction = 85 * days + 0.5 * miles + 0.4 * receipts + 25  # bonus
        else:
            # Standard short trip
            prediction = 90 * days + 0.5 * miles + 0.5 * receipts
    
    # Path 4: Medium trips (6-10 days)
    elif days <= 10:
        if receipts_per_day <= 100:
            # Reasonable spending
            prediction = 80 * days + 0.4 * miles + 0.6 * receipts
        else:
            # High spending - penalty
            prediction = 75 * days + 0.35 * miles + 0.4 * receipts
    
    # Path 5: Long trips (11+ days)
    else:
        if receipts_per_day <= 75:
            # Conservative spending long trip
            prediction = 70 * days + 0.35 * miles + 0.7 * receipts
        else:
            # High spending long trip - severe penalty
            prediction = 60 * days + 0.3 * miles + 0.3 * receipts
    
    # Apply universal adjustments based on analysis
    
    # Miles per day efficiency adjustments
    if miles_per_day > 300:
        prediction -= 20  # Excessive daily travel penalty
    elif 150 <= miles_per_day <= 250:
        prediction += 10  # Efficient travel bonus
    
    # Receipt amount adjustments
    if receipts < 10:
        prediction += 15  # Minimal spending bonus
    elif receipts > 1000:
        prediction -= 30  # High spending penalty
    
    # Day-specific adjustments from clustering
    if days == 1 and prediction < 100:
        prediction = prediction * 1.2  # Single day minimum adjustment
    
    # Apply the logarithmic pattern found in analysis
    if receipts > 50:
        log_adj = math.log1p(receipts / 50) * 5
        prediction += log_adj
    
    # Inverse receipts pattern (consistent across models)
    inv_receipts = 100.0 / (1.0 + receipts)
    prediction += inv_receipts
    
    # Ensure reasonable bounds
    if prediction < 50:
        prediction = 50
    elif prediction > 2500:
        prediction = 2500
    
    return round(prediction, 2)

def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: perfect_v2.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = sys.argv[1]
        miles = sys.argv[2]
        receipts = sys.argv[3]
        
        result = perfect_v2_predict(days, miles, receipts)
        print(result)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()