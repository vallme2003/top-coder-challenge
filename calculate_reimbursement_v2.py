#!/usr/bin/env python3
import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate travel reimbursement based on reverse-engineered logic.
    Key insight: High receipts actually REDUCE total reimbursement!
    """
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Base per diem - varies by trip length
    if days == 1:
        per_diem_rate = 100.0
    elif days == 2:
        per_diem_rate = 100.0
    elif days == 3:
        per_diem_rate = 100.0
    elif days == 4:
        per_diem_rate = 100.0
    elif days == 5:
        per_diem_rate = 105.0  # 5-day bonus
    elif days <= 7:
        per_diem_rate = 100.0
    elif days <= 10:
        per_diem_rate = 95.0
    else:
        per_diem_rate = 90.0
    
    base_per_diem = per_diem_rate * days
    
    # Mileage calculation
    if miles <= 100:
        mileage_reimb = miles * 0.58
    elif miles <= 300:
        mileage_reimb = 100 * 0.58 + (miles - 100) * 0.50
    elif miles <= 600:
        mileage_reimb = 100 * 0.58 + 200 * 0.50 + (miles - 300) * 0.40
    else:
        mileage_reimb = 100 * 0.58 + 200 * 0.50 + 300 * 0.40 + (miles - 600) * 0.30
    
    # Base amount (before receipt adjustment)
    base_amount = base_per_diem + mileage_reimb
    
    # Receipt adjustment - this is the key insight!
    # Receipts don't add to reimbursement, they modify it
    if receipts < 10:
        # Very small receipts - heavy penalty
        adjustment_factor = -0.3
    elif receipts < 50:
        # Small receipts - significant penalty
        adjustment_factor = -0.2
    elif receipts < 100:
        # Medium-small receipts - moderate penalty
        adjustment_factor = -0.1
    elif receipts < 200:
        # Normal receipts - slight penalty
        adjustment_factor = -0.05
    elif receipts < 400:
        # Good range - minimal impact
        adjustment_factor = 0.0
    elif receipts < 800:
        # Higher receipts - small positive
        adjustment_factor = 0.05
    elif receipts < 1200:
        # High receipts - moderate positive
        adjustment_factor = 0.1
    elif receipts < 2000:
        # Very high receipts - but diminishing returns
        adjustment_factor = 0.08
    else:
        # Excessive receipts - reduced benefit
        adjustment_factor = 0.05
    
    # Apply receipt adjustment to base
    receipt_adjustment = base_amount * adjustment_factor
    
    # Add actual receipt reimbursement (but capped)
    if receipts < 50:
        receipt_reimb = receipts * 0.3
    elif receipts < 200:
        receipt_reimb = receipts * 0.5
    elif receipts < 400:
        receipt_reimb = receipts * 0.6
    elif receipts < 800:
        receipt_reimb = receipts * 0.65
    elif receipts < 1200:
        receipt_reimb = 800 * 0.65 + (receipts - 800) * 0.4
    else:
        receipt_reimb = 800 * 0.65 + 400 * 0.4 + (receipts - 1200) * 0.2
    
    # Calculate efficiency bonus
    mpd = miles / days if days > 0 else 0
    efficiency_bonus = 0
    if 180 <= mpd <= 220:
        efficiency_bonus = base_amount * 0.1  # 10% bonus for optimal efficiency
    elif 150 <= mpd < 180:
        efficiency_bonus = base_amount * 0.05
    elif mpd > 250:
        efficiency_bonus = -base_amount * 0.05  # Penalty for excessive driving
    
    # Special adjustments
    total = base_amount + receipt_adjustment + receipt_reimb + efficiency_bonus
    
    # Cap total reimbursement for extreme cases
    if receipts > 1500 and total > base_amount * 1.5:
        total = base_amount * 1.5
    
    # Ensure minimum reimbursement
    min_reimb = base_amount * 0.5
    if total < min_reimb:
        total = min_reimb
    
    return round(total, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement.py <days> <miles> <receipts>")
        sys.exit(1)
    
    days = sys.argv[1]
    miles = sys.argv[2]
    receipts = sys.argv[3]
    
    result = calculate_reimbursement(days, miles, receipts)
    print(result)