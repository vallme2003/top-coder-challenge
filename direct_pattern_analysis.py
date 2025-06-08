#!/usr/bin/env python3
"""
DIRECT PATTERN ANALYSIS - EMERGENCY MODE
========================================
Find the pattern by looking at actual coefficient relationships
"""

import json
from collections import defaultdict

def main():
    with open('input_to_formula_mapping.json', 'r') as f:
        mapping = json.load(f)
    
    # Focus on linear_with_constant (641 cases) - most common
    linear_cases = []
    for key, formula_info in mapping.items():
        if formula_info['formula_type'] == 'linear_with_constant':
            parts = key.split(',')
            days = int(float(parts[0]))
            miles = int(float(parts[1]))
            receipts = float(parts[2])
            coeffs = formula_info['coeffs']
            
            linear_cases.append({
                'days': days,
                'miles': miles, 
                'receipts': receipts,
                'a': coeffs[0],  # days coeff
                'b': coeffs[1],  # miles coeff  
                'c': coeffs[2],  # receipts coeff
                'd': coeffs[3],  # constant
                'expected': formula_info['expected']
            })
    
    print(f"Analyzing {len(linear_cases)} linear_with_constant cases...")
    
    # Group by coefficient combinations to find patterns
    coeff_groups = defaultdict(list)
    for case in linear_cases:
        coeff_key = (case['a'], case['b'], case['c'], case['d'])
        coeff_groups[coeff_key].append(case)
    
    print(f"Found {len(coeff_groups)} unique coefficient combinations")
    
    # Look for input patterns within each coefficient group
    for i, (coeffs, cases) in enumerate(coeff_groups.items()):
        if i < 5:  # Show first 5 groups
            print(f"\nGroup {i+1}: coeffs={coeffs}, {len(cases)} cases")
            for case in cases[:3]:  # Show first 3 cases in group
                print(f"  days={case['days']}, miles={case['miles']}, receipts={case['receipts']:.2f}")
    
    # NEW APPROACH: Look for the simplest possible pattern
    # Maybe it's just based on input ranges or simple arithmetic
    
    print("\n=== TESTING SIMPLE ARITHMETIC PATTERNS ===")
    
    # Test if coefficients are simple functions of inputs
    patterns_found = 0
    
    for case in linear_cases[:50]:  # Test first 50
        days, miles, receipts = case['days'], case['miles'], case['receipts']
        a, b, c, d = case['a'], case['b'], case['c'], case['d']
        
        # Test various simple relationships
        tests = [
            ("a = 10 + days", a == 10 + days),
            ("a = 10 + 2*days", a == 10 + 2*days),
            ("b = miles/100", abs(b - miles/100) < 0.001),
            ("b = miles*0.01", abs(b - miles*0.01) < 0.001),
            ("c = receipts*0.1", abs(c - receipts*0.1) < 0.001),
            ("d = days*10", d == days*10),
            ("d = (days+miles)*2", d == (days+miles)*2),
        ]
        
        for desc, result in tests:
            if result:
                print(f"Pattern found: {desc} for case days={days}, miles={miles}")
                patterns_found += 1
    
    print(f"\nSimple patterns found: {patterns_found}")
    
    # FINAL ATTEMPT: Just try to reverse engineer from a few examples
    print("\n=== REVERSE ENGINEERING FROM EXAMPLES ===")
    
    # Take first few cases and manually figure out the pattern
    for i in range(min(10, len(linear_cases))):
        case = linear_cases[i]
        days, miles, receipts = case['days'], case['miles'], case['receipts']
        expected = case['expected']
        
        # Try the most obvious business logic
        # Daily allowance + mileage + receipt reimbursement
        
        # Standard government rates from 1960s might be:
        daily_rates = [75, 80, 85, 90, 95, 100]
        mileage_rates = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
        receipt_rates = [0.80, 0.85, 0.90, 0.95, 1.00]  # High because receipts are actual expenses
        
        for daily in daily_rates:
            for mileage in mileage_rates:
                for receipt in receipt_rates:
                    pred = daily * days + mileage * miles + receipt * receipts
                    if abs(pred - expected) < 0.01:
                        print(f"EXACT MATCH: {daily}*{days} + {mileage}*{miles} + {receipt}*{receipts:.2f} = {expected}")
                        
                        # Test this on ALL cases
                        total_matches = 0
                        for test_case in linear_cases:
                            test_pred = daily * test_case['days'] + mileage * test_case['miles'] + receipt * test_case['receipts']
                            if abs(test_pred - test_case['expected']) < 0.01:
                                total_matches += 1
                        
                        if total_matches > 500:
                            print(f"*** POTENTIAL UNIVERSAL FORMULA: {daily}*days + {mileage}*miles + {receipt}*receipts ***")
                            print(f"Matches: {total_matches}/{len(linear_cases)} linear cases")
                            return daily, mileage, receipt

if __name__ == "__main__":
    main()