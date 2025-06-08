#!/usr/bin/env python3
"""
PERFECT ANALYTICAL FUNCTION SEARCH
==================================

Based on our analysis:
1. $10/day appears in 309 cases across all trip lengths
2. Mile coefficients: 0.25, 0.7, 0.75, 0.4, 0.45 are most common
3. Receipt coefficients: 0.7, 0.5, 0.55, 0.65, 0.6 are most common

Hypothesis: The analytical function uses conditional logic based on input characteristics
to select different coefficients, but follows a consistent pattern.
"""

import json
import numpy as np
import math
from itertools import product

def load_data():
    """Load public cases"""
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    return public_cases

def test_input_dependent_coefficients(public_cases):
    """Test if coefficients depend on input values in a predictable way"""
    
    print("=== TESTING INPUT-DEPENDENT COEFFICIENT FUNCTIONS ===")
    
    # Based on our analysis, test functions that predict coefficients from inputs
    candidates = [
        {
            'name': 'Distance-Based Mile Rate',
            'day_rate': 10,
            'mile_func': lambda d, m, r: 0.8 - 0.0005 * m,  # Decreases with distance
            'receipt_func': lambda d, m, r: 0.7,
            'constant': 0
        },
        
        {
            'name': 'Spending-Based Receipt Rate', 
            'day_rate': 10,
            'mile_func': lambda d, m, r: 0.6,
            'receipt_func': lambda d, m, r: 0.9 - 0.0002 * r,  # Decreases with spending
            'constant': 0
        },
        
        {
            'name': 'Trip Length Mile Adjustment',
            'day_rate': 10,
            'mile_func': lambda d, m, r: 0.5 + 0.05 * min(d, 6),  # Increases with trip length
            'receipt_func': lambda d, m, r: 0.7,
            'constant': 0
        },
        
        {
            'name': 'Complex Business Logic',
            'day_rate': 10,
            'mile_func': lambda d, m, r: 0.4 + 0.2 * (1 if m > 500 else 0) + 0.1 * (1 if d > 5 else 0),
            'receipt_func': lambda d, m, r: 0.8 - 0.1 * (1 if r > 1000 else 0) - 0.1 * (1 if r > 2000 else 0),
            'constant': 0
        }
    ]
    
    for candidate in candidates:
        print(f"\nTesting: {candidate['name']}")
        
        exact_matches = 0
        errors = []
        
        for case in public_cases:
            input_data = case['input']
            days = input_data['trip_duration_days']
            miles = input_data['miles_traveled']
            receipts = input_data['total_receipts_amount']
            expected = case['expected_output']
            
            try:
                mile_rate = candidate['mile_func'](days, miles, receipts)
                receipt_rate = candidate['receipt_func'](days, miles, receipts)
                
                predicted = (candidate['day_rate'] * days + 
                           mile_rate * miles + 
                           receipt_rate * receipts + 
                           candidate['constant'])
                
                error = abs(predicted - expected)
                errors.append(error)
                
                if error < 0.01:
                    exact_matches += 1
                    
            except Exception as e:
                errors.append(1000)
        
        avg_error = np.mean(errors)
        score = avg_error * 100 + (1000 - exact_matches) * 0.1
        
        print(f"  Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
        print(f"  Average error: ${avg_error:.2f}")
        print(f"  Score: {score:.2f}")

def test_quantized_coefficient_functions(public_cases):
    """Test if the system uses quantized (discrete) coefficient values"""
    
    print(f"\n=== TESTING QUANTIZED COEFFICIENT SYSTEMS ===")
    
    # Based on coefficient analysis, most common values
    day_rates = [10, 12, 14, 16, 18]
    mile_rates = [0.25, 0.4, 0.45, 0.55, 0.7, 0.75, 0.8, 0.85]
    receipt_rates = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 1.0]
    
    # Test selection rules based on input characteristics
    selection_rules = [
        {
            'name': 'Miles/Day Ratio Rule',
            'day_func': lambda d, m, r: 10,
            'mile_func': lambda d, m, r: 0.4 if m/d < 100 else 0.7 if m/d < 200 else 0.85,
            'receipt_func': lambda d, m, r: 0.7 if r < 1000 else 0.5
        },
        
        {
            'name': 'Trip Category Rule',
            'day_func': lambda d, m, r: 10 if d <= 5 else 12 if d <= 10 else 14,
            'mile_func': lambda d, m, r: 0.8 if m > 500 else 0.55,
            'receipt_func': lambda d, m, r: 0.8 if r < 500 else 0.65 if r < 1500 else 0.5
        },
        
        {
            'name': 'Hash-Based Selection',
            'day_func': lambda d, m, r: day_rates[int((d + m/100 + r/100) % len(day_rates))],
            'mile_func': lambda d, m, r: mile_rates[int((d*7 + m/50) % len(mile_rates))],
            'receipt_func': lambda d, m, r: receipt_rates[int((d*3 + r/200) % len(receipt_rates))]
        }
    ]
    
    for rule in selection_rules:
        print(f"\nTesting: {rule['name']}")
        
        exact_matches = 0
        errors = []
        
        for case in public_cases:
            input_data = case['input']
            days = input_data['trip_duration_days']
            miles = input_data['miles_traveled']
            receipts = input_data['total_receipts_amount']
            expected = case['expected_output']
            
            try:
                day_rate = rule['day_func'](days, miles, receipts)
                mile_rate = rule['mile_func'](days, miles, receipts)
                receipt_rate = rule['receipt_func'](days, miles, receipts)
                
                predicted = day_rate * days + mile_rate * miles + receipt_rate * receipts
                
                error = abs(predicted - expected)
                errors.append(error)
                
                if error < 0.01:
                    exact_matches += 1
                    
            except Exception as e:
                errors.append(1000)
        
        avg_error = np.mean(errors)
        score = avg_error * 100 + (1000 - exact_matches) * 0.1
        
        print(f"  Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
        print(f"  Average error: ${avg_error:.2f}")
        print(f"  Score: {score:.2f}")

def test_legacy_business_formulas(public_cases):
    """Test formulas that might have been used in 1960s business travel"""
    
    print(f"\n=== TESTING LEGACY 1960s BUSINESS FORMULAS ===")
    
    legacy_candidates = [
        {
            'name': '1960s Government Rate',
            'formula': lambda d, m, r: d * 12 + m * 0.10 + r * 0.80,  # Old government rates
            'desc': '$12/day + $0.10/mile + 80% receipts'
        },
        
        {
            'name': 'Per Diem + Mileage + Receipts',
            'formula': lambda d, m, r: d * 15 + m * 0.12 + r * 0.75,
            'desc': '$15/day + $0.12/mile + 75% receipts'  
        },
        
        {
            'name': 'Corporate Rate Structure',
            'formula': lambda d, m, r: d * 10 + m * 0.08 + min(r * 0.85, 100 * d),  # Receipt cap
            'desc': '$10/day + $0.08/mile + 85% receipts (capped at $100/day)'
        },
        
        {
            'name': 'Distance Tiered Rate',
            'formula': lambda d, m, r: d * 11 + (m * 0.15 if m <= 300 else 300 * 0.15 + (m-300) * 0.08) + r * 0.70,
            'desc': '$11/day + tiered mileage (15¢ first 300mi, 8¢ after) + 70% receipts'
        },
        
        {
            'name': 'Complex Legacy Formula',
            'formula': lambda d, m, r: (
                d * (8 + min(d, 7) * 0.5) +  # Progressive daily rate
                m * (0.06 + 0.02 * min(math.floor(m/200), 3)) +  # Distance tiers
                r * (0.9 - 0.05 * min(math.floor(r/500), 3))  # Spending tiers
            ),
            'desc': 'Progressive daily + distance tiers + spending tiers'
        }
    ]
    
    for candidate in legacy_candidates:
        print(f"\nTesting: {candidate['name']}")
        print(f"Formula: {candidate['desc']}")
        
        exact_matches = 0
        errors = []
        
        for case in public_cases:
            input_data = case['input']
            days = input_data['trip_duration_days']
            miles = input_data['miles_traveled']
            receipts = input_data['total_receipts_amount']
            expected = case['expected_output']
            
            try:
                predicted = candidate['formula'](days, miles, receipts)
                error = abs(predicted - expected)
                errors.append(error)
                
                if error < 0.01:
                    exact_matches += 1
                    
            except Exception as e:
                errors.append(1000)
        
        avg_error = np.mean(errors)
        score = avg_error * 100 + (1000 - exact_matches) * 0.1
        
        print(f"  Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
        print(f"  Average error: ${avg_error:.2f}")
        print(f"  Score: {score:.2f}")

def brute_force_optimal_coefficients(public_cases):
    """Brute force search for the optimal coefficient combination"""
    
    print(f"\n=== BRUTE FORCE OPTIMAL COEFFICIENT SEARCH ===")
    
    # Based on our analysis, search around the most promising values
    day_candidates = [8, 9, 10, 11, 12]
    mile_candidates = [0.50, 0.55, 0.60, 0.65, 0.70]
    receipt_candidates = [0.70, 0.75, 0.80, 0.85, 0.90]
    constant_candidates = [0, -50, -100, 50, 100]
    
    best_score = float('inf')
    best_params = None
    best_exact_matches = 0
    
    total_combinations = len(day_candidates) * len(mile_candidates) * len(receipt_candidates) * len(constant_candidates)
    print(f"Testing {total_combinations} coefficient combinations...")
    
    combination_count = 0
    
    for day_rate, mile_rate, receipt_rate, constant in product(day_candidates, mile_candidates, receipt_candidates, constant_candidates):
        combination_count += 1
        
        if combination_count % 25 == 0:
            print(f"  Progress: {combination_count}/{total_combinations} ({100*combination_count/total_combinations:.1f}%)")
        
        exact_matches = 0
        errors = []
        
        for case in public_cases:
            input_data = case['input']
            days = input_data['trip_duration_days']
            miles = input_data['miles_traveled']
            receipts = input_data['total_receipts_amount']
            expected = case['expected_output']
            
            predicted = day_rate * days + mile_rate * miles + receipt_rate * receipts + constant
            error = abs(predicted - expected)
            errors.append(error)
            
            if error < 0.01:
                exact_matches += 1
        
        avg_error = np.mean(errors)
        score = avg_error * 100 + (1000 - exact_matches) * 0.1
        
        if score < best_score or exact_matches > best_exact_matches:
            best_score = score
            best_params = (day_rate, mile_rate, receipt_rate, constant)
            best_exact_matches = exact_matches
    
    print(f"\n=== BEST COEFFICIENT COMBINATION FOUND ===")
    if best_params:
        day_rate, mile_rate, receipt_rate, constant = best_params
        print(f"Formula: {day_rate}*days + {mile_rate}*miles + {receipt_rate}*receipts + {constant}")
        print(f"Exact matches: {best_exact_matches}/1000 ({best_exact_matches/10:.1f}%)")
        print(f"Score: {best_score:.2f}")
    else:
        print("No optimal combination found")

def main():
    """Main perfect function search"""
    print("PERFECT ANALYTICAL FUNCTION SEARCH")
    print("=" * 50)
    
    public_cases = load_data()
    print(f"Loaded {len(public_cases)} public cases")
    
    # Test various approaches to find the perfect analytical function
    test_input_dependent_coefficients(public_cases)
    test_quantized_coefficient_functions(public_cases)
    test_legacy_business_formulas(public_cases)
    brute_force_optimal_coefficients(public_cases)
    
    print(f"\n=== CONCLUSION ===")
    print(f"The true analytical function likely involves:")
    print(f"1. Conditional logic based on input characteristics")
    print(f"2. Quantized coefficient values from a discrete set")
    print(f"3. Legacy business rules from 1960s travel policies")
    print(f"4. Possible non-linear transformations or lookup tables")

if __name__ == "__main__":
    main()