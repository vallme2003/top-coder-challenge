#!/usr/bin/env python3
"""
Ultra-fast champion implementation based on RandomForest analysis.
Key insights: inv_receipts (37.8%), three_way (19.8%), days_receipts (11.4%), days_miles (10.6%)
Target: Beat current leader's score of 8,891.41
"""

import sys
import math

def fast_predict(days, miles, receipts):
    """
    Fast prediction using key features from RandomForest analysis.
    
    Top features and their importance:
    1. inv_receipts: 37.82% - Inverse receipt relationship
    2. three_way: 19.77% - days * miles * receipts interaction  
    3. days_receipts: 11.42% - Days-receipts interaction
    4. days_miles: 10.56% - Days-miles interaction
    5. receipts_sq: 4.93% - Receipts squared
    """
    # Convert to float
    days = float(days)
    miles = float(miles)
    receipts = float(receipts)
    
    # Calculate key features
    inv_receipts = 1.0 / (1.0 + receipts)
    three_way = days * miles * receipts
    days_receipts = days * receipts
    days_miles = days * miles
    receipts_sq = receipts * receipts
    log_receipts = math.log1p(receipts)
    
    # Multi-path prediction based on key feature ranges
    # This approximates the RandomForest decision paths
    
    # Path 1: High inverse receipts (low receipt amounts)
    if inv_receipts > 0.01:  # receipts < ~100
        base = 150 + days * 40
        inv_effect = inv_receipts * 1200
        interaction_effect = (days_miles / 100) * 8
        if days == 5:
            base += 30
        prediction = base + inv_effect + interaction_effect
    
    # Path 2: Medium receipts with high efficiency
    elif receipts < 500 and (miles / days) > 100:
        base = 200 + days * 60
        efficiency_bonus = ((miles / days) - 100) * 2
        receipt_factor = receipts * 0.4
        three_way_effect = three_way / 50000
        prediction = base + efficiency_bonus + receipt_factor + three_way_effect
    
    # Path 3: Medium to high receipts
    elif receipts < 1500:
        # Base calculation
        base = 100 + days * 80
        
        # Receipt handling with diminishing returns
        if receipts < 300:
            receipt_effect = receipts * 0.6
        elif receipts < 800:
            receipt_effect = 300 * 0.6 + (receipts - 300) * 0.5
        else:
            receipt_effect = 300 * 0.6 + 500 * 0.5 + (receipts - 800) * 0.3
        
        # Interaction effects
        days_miles_effect = days_miles / 50
        log_effect = log_receipts * 40
        
        prediction = base + receipt_effect + days_miles_effect + log_effect
    
    # Path 4: Very high receipts (>$1500)
    else:
        # Different formula for high receipts
        base = 300 + days * 100
        
        # Strong diminishing returns for high receipts
        receipt_effect = 800 + (receipts - 1500) * 0.15
        
        # Three-way interaction becomes more important
        three_way_effect = three_way / 20000
        
        # Days-receipts interaction
        days_receipts_effect = days_receipts / 2000
        
        prediction = base + receipt_effect + three_way_effect + days_receipts_effect
    
    # Apply universal adjustments
    
    # 5-day bonus (observed pattern)
    if days == 5:
        prediction += 25
    
    # Special receipt endings
    cents = int(round(receipts * 100)) % 100
    if cents == 49:
        prediction += 3
    elif cents == 99:
        prediction += 3
    
    # Efficiency adjustments
    mpd = miles / days if days > 0 else 0
    if 180 <= mpd <= 220:  # Optimal efficiency range
        prediction += 20
    elif mpd > 300:  # Too high efficiency penalty
        prediction -= 10
    
    # Trip length adjustments
    if days >= 10:  # Long trip adjustment
        prediction += (days - 10) * 5
    elif days == 1:  # Single day adjustment
        prediction -= 20
    
    # Apply linear correction based on analysis
    # This corrects systematic bias: actual = 0.7326 * predicted + 119.08
    prediction = prediction * 0.732598 + 119.08
    
    # Ensure reasonable bounds
    if prediction < 100:
        prediction = 100
    elif prediction > 3000:
        prediction = 3000
    
    return prediction

def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: fast_champion.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = sys.argv[1]
        miles = sys.argv[2]
        receipts = sys.argv[3]
        
        result = fast_predict(days, miles, receipts)
        print(round(result, 2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()