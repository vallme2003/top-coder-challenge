#!/usr/bin/env python3
import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate travel reimbursement based on patterns discovered through ML analysis.
    Key insights:
    - days*miles is the most important feature
    - receipts and log(receipts) heavily influence the outcome
    - Receipt amounts don't simply add to reimbursement
    """
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Key derived features
    days_miles = days * miles
    mpd = miles / days if days > 0 else 0
    rpd = receipts / days if days > 0 else 0
    log_receipts = math.log1p(receipts)
    
    # Base calculation heavily influenced by days*miles interaction
    if days_miles < 500:
        base = 100 + days_miles * 0.8
    elif days_miles < 2000:
        base = 100 + 500 * 0.8 + (days_miles - 500) * 0.5
    elif days_miles < 5000:
        base = 100 + 500 * 0.8 + 1500 * 0.5 + (days_miles - 2000) * 0.3
    else:
        base = 100 + 500 * 0.8 + 1500 * 0.5 + 3000 * 0.3 + (days_miles - 5000) * 0.15
    
    # Per diem component (smaller influence)
    per_diem = days * 50  # Reduced from 100 since days*miles dominates
    
    # Receipt influence is complex and non-linear
    # Based on analysis, receipts can reduce OR increase reimbursement
    if receipts < 50:
        # Small receipts reduce reimbursement
        receipt_factor = -50 + receipts * 0.5
    elif receipts < 200:
        # Moderate receipts have neutral to slight positive effect
        receipt_factor = receipts * 0.3
    elif receipts < 800:
        # Good range
        receipt_factor = 60 + receipts * 0.4
    elif receipts < 1500:
        # Diminishing returns
        receipt_factor = 380 + (receipts - 800) * 0.2
    else:
        # High receipts can reduce total reimbursement
        receipt_factor = 520 - (receipts - 1500) * 0.15
    
    # Log transformation of receipts (important from ML analysis)
    log_bonus = log_receipts * 20
    
    # Efficiency adjustments
    if 180 <= mpd <= 220:
        efficiency_bonus = 50
    elif 100 <= mpd < 180:
        efficiency_bonus = 20
    else:
        efficiency_bonus = 0
    
    # 5-day bonus
    if days == 5:
        day_bonus = 30
    else:
        day_bonus = 0
    
    # Special receipt endings
    cents = int(round(receipts * 100)) % 100
    if cents == 49 or cents == 99:
        rounding_bonus = 5
    else:
        rounding_bonus = 0
    
    # Combine all factors
    total = base + per_diem + receipt_factor + log_bonus + efficiency_bonus + day_bonus + rounding_bonus
    
    # Apply caps for extreme cases
    # Very high receipt cases seem to be capped
    if receipts > 2000 and total > 2000:
        total = 1900 + (total - 2000) * 0.1
    
    # Minimum reimbursement
    if total < 100:
        total = 100
    
    return round(total, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement_final.py <days> <miles> <receipts>")
        sys.exit(1)
    
    days = sys.argv[1]
    miles = sys.argv[2]
    receipts = sys.argv[3]
    
    result = calculate_reimbursement(days, miles, receipts)
    print(result)