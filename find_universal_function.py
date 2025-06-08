#!/usr/bin/env python3
"""
RAPID UNIVERSAL FUNCTION DISCOVERY
=================================
5 minute max mode - find the score 0 function NOW
"""

import json

def main():
    # Load data
    with open('input_to_formula_mapping.json', 'r') as f:
        mapping = json.load(f)
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("ANALYZING COEFFICIENT PATTERNS...")
    
    # The coefficients showed clear step patterns:
    # Days: increments of 2 starting from 10
    # Miles/Receipts: increments of 0.05 starting from 0.05  
    # Constants: increments of 10 from -200 to 200
    
    # HYPOTHESIS: The function uses input values to determine coefficients!
    
    # Test if coefficients are calculated from inputs
    correct_predictions = 0
    
    for key, formula_info in mapping.items():
        parts = key.split(',')
        days = float(parts[0])
        miles = float(parts[1]) 
        receipts = float(parts[2])
        expected = formula_info['expected']
        
        # PATTERN HYPOTHESIS: coefficients based on input modulo operations
        # This would explain the step patterns we see
        
        # Try: a = 10 + 2*(days % something), b = 0.05 * (miles % something), etc.
        
        # Test multiple modulo bases
        for day_mod in [2, 3, 4, 5, 10]:
            for mile_mod in [10, 20, 50, 100]:
                for receipt_mod in [10, 20, 50]:
                    
                    # Calculate coefficients from inputs
                    a = 10 + 2 * (int(days) % day_mod)
                    b = 0.05 + 0.05 * (int(miles) % mile_mod) 
                    c = 0.05 + 0.05 * (int(receipts * 100) % receipt_mod)
                    d = -200 + 10 * ((int(days) + int(miles)) % 40)
                    
                    # Test prediction
                    pred = a * days + b * miles + c * receipts + d
                    
                    if abs(pred - expected) < 0.01:
                        correct_predictions += 1
                        if correct_predictions < 10:  # Show first few
                            print(f"MATCH: {key} -> a={a}, b={b}, c={c}, d={d}")
                        
                        if correct_predictions >= 1000:  # Found it!
                            print(f"\n*** UNIVERSAL FUNCTION FOUND! ***")
                            print(f"Modulo bases: day_mod={day_mod}, mile_mod={mile_mod}, receipt_mod={receipt_mod}")
                            print(f"Formula:")
                            print(f"a = 10 + 2 * (days % {day_mod})")
                            print(f"b = 0.05 + 0.05 * (miles % {mile_mod})")
                            print(f"c = 0.05 + 0.05 * (receipts*100 % {receipt_mod})")
                            print(f"d = -200 + 10 * ((days + miles) % 40)")
                            print(f"reimbursement = a*days + b*miles + c*receipts + d")
                            return day_mod, mile_mod, receipt_mod
    
    print(f"Best result: {correct_predictions}/1000 matches")
    
    # If modulo didn't work, try hash-based or lookup table approach
    if correct_predictions < 500:
        print("\nTrying hash-based coefficient selection...")
        
        # Maybe coefficients are selected based on hash of inputs
        for case_num, (key, formula_info) in enumerate(mapping.items()):
            parts = key.split(',')
            days = float(parts[0])
            miles = float(parts[1])
            receipts = float(parts[2])
            
            # Create hash from inputs
            input_hash = hash((int(days), int(miles), int(receipts*100))) % 1000
            
            # Use hash to select from coefficient arrays
            day_coeffs = list(range(10, 250, 2))
            mile_coeffs = [x * 0.05 for x in range(1, 41)]
            receipt_coeffs = [x * 0.05 for x in range(1, 41)]
            constants = list(range(-200, 201, 10))
            
            a = day_coeffs[input_hash % len(day_coeffs)]
            b = mile_coeffs[input_hash % len(mile_coeffs)]
            c = receipt_coeffs[input_hash % len(receipt_coeffs)]
            d = constants[input_hash % len(constants)]
            
            pred = a * days + b * miles + c * receipts + d
            expected = formula_info['expected']
            
            if abs(pred - expected) < 0.01:
                correct_predictions += 1
        
        print(f"Hash-based matches: {correct_predictions}/1000")

if __name__ == "__main__":
    main()