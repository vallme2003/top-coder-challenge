#!/usr/bin/env python3
import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate travel reimbursement based on reverse-engineered logic.
    """
    days = int(trip_duration_days)
    miles = float(miles_traveled)
    receipts = float(total_receipts_amount)
    
    # Calculate miles per day (efficiency)
    mpd = miles / days if days > 0 else 0
    
    # Base per diem calculation
    # From analysis: decreasing per-day rate as trip length increases
    if days == 1:
        per_diem = 100.0 * days
    elif days == 2:
        per_diem = 98.0 * days
    elif days == 3:
        per_diem = 96.0 * days
    elif days == 4:
        per_diem = 94.0 * days
    elif days == 5:
        per_diem = 100.0 * days  # 5-day bonus mentioned in interviews
    elif days == 6:
        per_diem = 88.0 * days
    elif days == 7:
        per_diem = 85.0 * days
    elif days == 8:
        per_diem = 80.0 * days
    elif days == 9:
        per_diem = 75.0 * days
    elif days == 10:
        per_diem = 70.0 * days
    else:  # >10 days
        per_diem = 65.0 * days
    
    # Mileage calculation - tiered system
    if miles <= 100:
        mileage_reimb = miles * 0.58
    elif miles <= 300:
        mileage_reimb = 100 * 0.58 + (miles - 100) * 0.45
    elif miles <= 600:
        mileage_reimb = 100 * 0.58 + 200 * 0.45 + (miles - 300) * 0.35
    else:
        mileage_reimb = 100 * 0.58 + 200 * 0.45 + 300 * 0.35 + (miles - 600) * 0.25
    
    # Efficiency bonus (miles per day)
    efficiency_bonus = 0
    if 180 <= mpd <= 220:
        efficiency_bonus = 40  # Sweet spot mentioned by Kevin
    elif 150 <= mpd < 180:
        efficiency_bonus = 25
    elif 100 <= mpd < 150:
        efficiency_bonus = 15
    elif mpd > 220:
        efficiency_bonus = 10  # Diminishing returns for very high efficiency
    
    # Receipt handling - complex rules based on amount and trip length
    daily_receipt_avg = receipts / days if days > 0 else receipts
    
    # Penalty for very low receipts
    if receipts < 10:
        receipt_reimb = receipts * 0.3
    # Small receipts get penalized
    elif receipts < 50:
        receipt_reimb = receipts * 0.5
    # Normal range
    elif receipts < 200:
        receipt_reimb = receipts * 0.75
    # Good range for medium trips
    elif receipts < 800:
        if days >= 4 and days <= 6:
            receipt_reimb = receipts * 0.8  # Better rate for optimal trip length
        else:
            receipt_reimb = receipts * 0.7
    # High receipts - strong diminishing returns
    else:
        base_amount = 800 * 0.7
        excess = receipts - 800
        # Very strong penalty for excessive spending
        if daily_receipt_avg > 150:
            receipt_reimb = base_amount + excess * 0.1
        else:
            receipt_reimb = base_amount + excess * 0.3
    
    # Special adjustments
    total = per_diem + mileage_reimb + efficiency_bonus + receipt_reimb
    
    # 5-day trip bonus
    if days == 5:
        total += 30
    
    # Rounding bug for receipts ending in 49/99 cents
    cents = int(round(receipts * 100)) % 100
    if cents == 49 or cents == 99:
        total += 3
    
    # Apply some noise/randomization (mentioned in interviews)
    # Use a pseudo-random factor based on inputs
    pseudo_random = ((days * 7 + int(miles) * 13 + int(receipts * 100)) % 100) / 100.0
    noise = (pseudo_random - 0.5) * 5  # +/- $2.50
    total += noise
    
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