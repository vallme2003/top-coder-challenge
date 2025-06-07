#!/usr/bin/env python3
import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate travel reimbursement based on regression analysis insights.
    Base formula: output ≈ 50*days + 0.45*miles + 0.38*receipts + adjustments
    """
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Base calculation from linear regression
    base = 50.05 * days + 0.45 * miles + 0.38 * receipts
    
    # Day-specific adjustments based on residual analysis
    day_adjustments = {
        1: -95.83,
        2: -24.47,
        3: -42.39,
        4: -1.60,
        5: 64.90,   # Strong 5-day bonus!
        6: 115.57,
        7: 127.93,
        8: 19.65,
        9: 3.79,
        10: -31.48,
        11: -31.74,
        12: -49.61,
        13: -6.41,
        14: -53.56
    }
    
    day_adj = day_adjustments.get(days, 0)
    
    # Receipt range adjustments based on residual analysis
    if receipts < 50:
        receipt_adj = -102.76
    elif receipts < 200:
        receipt_adj = -105.65
    elif receipts < 500:
        receipt_adj = -159.52
    elif receipts < 1000:
        receipt_adj = 37.46
    else:
        receipt_adj = 45.15
    
    # Polynomial features - add interaction and quadratic terms
    # These help reduce error significantly
    interaction_adj = 0.001 * days * miles  # days*miles interaction
    quadratic_adj = -0.00001 * receipts * receipts  # receipts squared (negative to cap high receipts)
    
    # Efficiency bonus
    mpd = miles / days if days > 0 else 0
    if 180 <= mpd <= 220:
        efficiency_adj = 30
    elif 100 <= mpd < 180:
        efficiency_adj = 15
    else:
        efficiency_adj = 0
    
    # Special endings
    cents = int(round(receipts * 100)) % 100
    if cents == 49 or cents == 99:
        rounding_adj = 3
    else:
        rounding_adj = 0
    
    # Combine all adjustments
    total = base + day_adj + receipt_adj + interaction_adj + quadratic_adj + efficiency_adj + rounding_adj
    
    # Ensure reasonable bounds
    if total < 100:
        total = 100
    elif total > 3000:
        total = 3000
    
    return round(total, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement_v3.py <days> <miles> <receipts>")
        sys.exit(1)
    
    days = sys.argv[1]
    miles = sys.argv[2]
    receipts = sys.argv[3]
    
    result = calculate_reimbursement(days, miles, receipts)
    print(result)