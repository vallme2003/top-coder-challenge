#!/usr/bin/env python3
"""
Linear champion model based on the best linear regression analysis.
From earlier analysis: Linear model achieved MAE 96.54, which translates to score ~9,654.
This should put us in the top 3 on the leaderboard.
"""

import sys
import math

def linear_predict(days, miles, receipts):
    """
    Linear prediction based on coefficients from linear regression analysis.
    From advanced_analysis.py: Linear model had MAE 96.54 with good generalization.
    """
    days = float(days)
    miles = float(miles)
    receipts = float(receipts)
    
    # Core linear formula (from regression analysis)
    # Approximate coefficients from earlier analysis
    prediction = (
        50.05 * days +           # Days coefficient 
        0.45 * miles +           # Miles coefficient
        0.38 * receipts          # Receipts coefficient
    )
    
    # Add key non-linear adjustments that improve accuracy
    
    # Logarithmic receipt effect (important pattern)
    log_receipts = math.log1p(receipts)
    prediction += log_receipts * 15
    
    # Inverse receipts (critical insight from RF analysis)
    inv_receipts = 1.0 / (1.0 + receipts)
    prediction += inv_receipts * 120
    
    # Interaction effects (keep minimal for stability)
    days_miles = days * miles
    prediction += days_miles * 0.002
    
    # Efficiency bonus (conservative)
    mpd = miles / days if days > 0 else 0
    if 150 <= mpd <= 250:
        prediction += 25
    elif 100 <= mpd < 150:
        prediction += 10
    
    # Day-specific adjustments (from residual analysis)
    day_adjustments = {
        1: -95,
        2: -25,
        3: -42,
        4: -2,
        5: 65,    # Strong 5-day bonus
        6: 115,
        7: 128,
        8: 20,
        9: 4,
        10: -31,
        11: -32,
        12: -50,
        13: -6,
        14: -54
    }
    
    if days in day_adjustments:
        prediction += day_adjustments[days]
    
    # Receipt range adjustments (from residual analysis)
    if receipts < 50:
        prediction -= 103
    elif receipts < 200:
        prediction -= 106
    elif receipts < 500:
        prediction -= 160
    elif receipts < 1000:
        prediction += 37
    else:
        prediction += 45
    
    # Special receipt endings
    cents = int(round(receipts * 100)) % 100
    if cents == 49 or cents == 99:
        prediction += 3
    
    # Ensure reasonable bounds
    if prediction < 100:
        prediction = 100
    elif prediction > 2500:
        prediction = 2500
    
    return round(prediction, 2)

def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: linear_champion.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = sys.argv[1]
        miles = sys.argv[2]
        receipts = sys.argv[3]
        
        result = linear_predict(days, miles, receipts)
        print(result)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()