#!/usr/bin/env python3
"""
Perfect Score Attempt - Aiming for score of 0
Based on detailed analysis of exact business logic patterns
"""

import sys
import math

def perfect_predict(days, miles, receipts):
    """
    Attempt to reverse-engineer the EXACT business logic for perfect accuracy.
    
    Key insights from analysis:
    1. Multiple calculation paths based on trip characteristics
    2. Different base rates for different trip durations
    3. Tiered mileage rates with diminishing returns
    4. Severe receipt penalties for high spending
    5. Legacy quirks and accumulated patches over 60 years
    """
    days = float(days)
    miles = float(miles)
    receipts = float(receipts)
    
    # Calculate key metrics
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    # Decision tree based on trip characteristics
    # Path 1: Single day trips (special handling)
    if days == 1:
        if miles < 100:
            # Short single day trip
            base = 120
            mile_rate = 0.65
            receipt_rate = 0.9 if receipts < 75 else 0.7
        elif miles < 300:
            # Medium single day trip
            base = 115
            mile_rate = 0.58
            receipt_rate = 0.85 if receipts < 100 else 0.6
        else:
            # Long single day trip
            base = 100
            mile_rate = 0.45
            receipt_rate = 0.75 if receipts < 150 else 0.5
    
    # Path 2: Short trips (2-3 days)
    elif days <= 3:
        base_per_day = 115 if days == 2 else 110
        
        if miles_per_day < 150:
            mile_rate = 0.58
        elif miles_per_day < 250:
            mile_rate = 0.52
        else:
            mile_rate = 0.45
            
        # Receipt penalties for short trips
        if receipts_per_day < 75:
            receipt_rate = 0.85
        elif receipts_per_day < 125:
            receipt_rate = 0.75
        elif receipts_per_day < 200:
            receipt_rate = 0.55
        else:
            receipt_rate = 0.25  # Severe penalty
            
        base = base_per_day * days
    
    # Path 3: Medium trips (4-7 days) 
    elif days <= 7:
        # Special 5-day bonus
        if days == 5:
            base_per_day = 110
            bonus = 25
        else:
            base_per_day = 105 if days <= 5 else 100
            bonus = 0
            
        # Efficiency-based mile rates
        if 180 <= miles_per_day <= 220:
            mile_rate = 0.55  # Optimal efficiency bonus
        elif miles_per_day < 150:
            mile_rate = 0.52
        elif miles_per_day < 300:
            mile_rate = 0.48
        else:
            mile_rate = 0.42
            
        # Progressive receipt penalties
        if receipts_per_day < 100:
            receipt_rate = 0.8
        elif receipts_per_day < 150:
            receipt_rate = 0.7
        elif receipts_per_day < 250:
            receipt_rate = 0.5
        else:
            receipt_rate = 0.2  # High spending penalty
            
        base = (base_per_day * days) + bonus
    
    # Path 4: Long trips (8+ days) - "Vacation penalty"
    else:
        base_per_day = 95 if days <= 10 else 90
        
        # Lower mile rates for long trips
        if miles_per_day > 250:
            mile_rate = 0.38  # Very long daily travel penalty
        elif miles_per_day > 150:
            mile_rate = 0.42
        else:
            mile_rate = 0.48
            
        # Severe receipt penalties for long trips (vacation penalty)
        if receipts_per_day < 75:
            receipt_rate = 0.75
        elif receipts_per_day < 120:
            receipt_rate = 0.6
        elif receipts_per_day < 200:
            receipt_rate = 0.35
        else:
            receipt_rate = 0.15  # Extreme vacation penalty
            
        base = base_per_day * days
        
        # Additional long trip penalty
        if days > 10:
            base -= (days - 10) * 5
    
    # Calculate core prediction
    mile_component = miles * mile_rate
    receipt_component = receipts * receipt_rate
    prediction = base + mile_component + receipt_component
    
    # Apply universal adjustments and legacy quirks
    
    # Receipt ending patterns (legacy system quirk)
    cents = int(round(receipts * 100)) % 100
    if cents == 49:
        prediction += 2.5
    elif cents == 99:
        prediction += 3.2
    elif cents == 0:  # Even dollar amounts
        prediction -= 1.5
    
    # Efficiency sweet spots (from interviews)
    efficiency = miles_per_day
    if 190 <= efficiency <= 210:
        prediction += 15  # Optimal efficiency bonus
    elif efficiency > 300:
        prediction -= 20  # Excessive travel penalty
    
    # Special day patterns (accumulated over 60 years)
    if days == 5:
        prediction += 18  # Additional 5-day bonus
    elif days == 7:
        prediction += 8   # Weekly trip bonus
    elif days == 14:
        prediction -= 25  # Two-week trip penalty
    
    # Mileage threshold bonuses/penalties
    if miles < 50:
        prediction += 10  # Local trip bonus
    elif miles > 1000:
        prediction -= 30  # Long distance penalty
    
    # Receipt amount thresholds (legacy brackets)
    if receipts < 25:
        prediction += 15  # Minimal spending bonus
    elif receipts > 2000:
        prediction -= 50  # Excessive spending penalty
    
    # Apply logarithmic adjustments for extreme values
    if receipts > 500:
        log_penalty = math.log(receipts / 500) * 20
        prediction -= log_penalty
    
    # Three-way interaction (complex legacy formula)
    three_way = (days * miles * receipts) / 100000
    if three_way > 10:
        prediction += math.sqrt(three_way) * 2
    elif three_way < 1:
        prediction += three_way * 5
    
    # Final legacy adjustments (accumulated patches)
    
    # Miles squared effect for medium trips
    if 4 <= days <= 8 and 200 <= miles <= 600:
        miles_sq_effect = (miles * miles) / 100000
        prediction += miles_sq_effect
    
    # Receipts inverse relationship (key insight)
    inv_receipts = 1.0 / (1.0 + receipts)
    prediction += inv_receipts * 150
    
    # Final bounds and rounding
    if prediction < 50:
        prediction = 50
    elif prediction > 3000:
        prediction = 3000
    
    # Legacy rounding (system may round to specific increments)
    # Try different rounding strategies
    prediction = round(prediction, 2)
    
    return prediction

def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: perfect_score_attempt.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = sys.argv[1]
        miles = sys.argv[2]
        receipts = sys.argv[3]
        
        result = perfect_predict(days, miles, receipts)
        print(result)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()