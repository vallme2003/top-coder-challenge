#!/usr/bin/env python3
"""
COEFFICIENT PATTERN ANALYSIS ENGINE
===================================

Analyze our 1,000 discovered exact formulas to find the underlying 
analytical function that achieves perfect score 0.

Strategy: If there's ONE true analytical function, our case-specific 
formulas are likely different expressions of it under different conditions.
"""

import json
import numpy as np
import pandas as pd
from collections import defaultdict
import math

def load_data():
    """Load public cases and discovered formulas"""
    with open('public_cases.json', 'r') as f:
        public_cases = json.load(f)
    
    with open('all_exact_formulas_v4_PERFECT.json', 'r') as f:
        formulas = json.load(f)
    
    return public_cases, formulas

def analyze_coefficient_patterns(public_cases, formulas):
    """Analyze patterns in formula coefficients vs input parameters"""
    
    print("=== COEFFICIENT PATTERN ANALYSIS ===")
    
    # Group formulas by type
    formula_groups = defaultdict(list)
    for formula in formulas:
        formula_type = formula['formula_type']
        formula_groups[formula_type].append(formula)
    
    print(f"\nFormula type distribution:")
    for ftype, flist in formula_groups.items():
        print(f"  {ftype}: {len(flist)} cases")
    
    # Analyze linear formulas (most common pattern)
    linear_formulas = formula_groups.get('linear', []) + formula_groups.get('linear_with_constant', [])
    
    if len(linear_formulas) > 100:
        print(f"\n=== ANALYZING {len(linear_formulas)} LINEAR FORMULAS ===")
        
        # Extract coefficients and inputs
        coeffs_data = []
        for formula in linear_formulas:
            case_num = formula['case_num']
            if case_num <= len(public_cases):
                case = public_cases[case_num - 1]
                input_data = case['input']
                
                days = input_data['trip_duration_days']
                miles = input_data['miles_traveled']
                receipts = input_data['total_receipts_amount']
                expected = case['expected_output']
                
                coeffs = formula.get('coeffs', [])
                if len(coeffs) >= 3:
                    coeffs_data.append({
                        'case_num': case_num,
                        'days': days,
                        'miles': miles,
                        'receipts': receipts,
                        'expected': expected,
                        'coeff_days': coeffs[0],
                        'coeff_miles': coeffs[1],
                        'coeff_receipts': coeffs[2],
                        'coeff_constant': coeffs[3] if len(coeffs) > 3 else 0,
                        'formula_type': formula['formula_type']
                    })
        
        df = pd.DataFrame(coeffs_data)
        print(f"Analyzing {len(df)} linear formulas with coefficients")
        
        # Look for coefficient patterns
        print(f"\n=== COEFFICIENT STATISTICS ===")
        print(f"Days coefficient:     mean={df['coeff_days'].mean():.3f}, std={df['coeff_days'].std():.3f}")
        print(f"Miles coefficient:    mean={df['coeff_miles'].mean():.3f}, std={df['coeff_miles'].std():.3f}")
        print(f"Receipts coefficient: mean={df['coeff_receipts'].mean():.3f}, std={df['coeff_receipts'].std():.3f}")
        print(f"Constant term:        mean={df['coeff_constant'].mean():.3f}, std={df['coeff_constant'].std():.3f}")
        
        # Look for relationships between coefficients and inputs
        print(f"\n=== COEFFICIENT vs INPUT CORRELATIONS ===")
        correlations = [
            ('Days coeff vs Days input', df['coeff_days'].corr(df['days'])),
            ('Days coeff vs Miles input', df['coeff_days'].corr(df['miles'])),
            ('Days coeff vs Receipts input', df['coeff_days'].corr(df['receipts'])),
            ('Miles coeff vs Days input', df['coeff_miles'].corr(df['days'])),
            ('Miles coeff vs Miles input', df['coeff_miles'].corr(df['miles'])),
            ('Miles coeff vs Receipts input', df['coeff_miles'].corr(df['receipts'])),
            ('Receipts coeff vs Days input', df['coeff_receipts'].corr(df['days'])),
            ('Receipts coeff vs Miles input', df['coeff_receipts'].corr(df['miles'])),
            ('Receipts coeff vs Receipts input', df['coeff_receipts'].corr(df['receipts'])),
        ]
        
        for desc, corr in correlations:
            if not pd.isna(corr):
                print(f"  {desc}: {corr:.3f}")
        
        # Look for common coefficient values
        print(f"\n=== MOST COMMON COEFFICIENT VALUES ===")
        
        # Days coefficients
        days_coeffs = df['coeff_days'].round(1).value_counts().head(10)
        print(f"Top days coefficients:")
        for coeff, count in days_coeffs.items():
            print(f"  {coeff}: {count} cases")
        
        # Miles coefficients  
        miles_coeffs = df['coeff_miles'].round(2).value_counts().head(10)
        print(f"Top miles coefficients:")
        for coeff, count in miles_coeffs.items():
            print(f"  {coeff}: {count} cases")
        
        # Receipts coefficients
        receipts_coeffs = df['coeff_receipts'].round(2).value_counts().head(10)
        print(f"Top receipts coefficients:")
        for coeff, count in receipts_coeffs.items():
            print(f"  {coeff}: {count} cases")
            
        return df
    
    return None

def test_universal_functions(public_cases):
    """Test candidate universal analytical functions"""
    
    print(f"\n=== TESTING UNIVERSAL ANALYTICAL FUNCTIONS ===")
    
    # Prepare test data
    test_data = []
    for case in public_cases:
        input_data = case['input']
        days = input_data['trip_duration_days']
        miles = input_data['miles_traveled']
        receipts = input_data['total_receipts_amount']
        expected = case['expected_output']
        test_data.append((days, miles, receipts, expected))
    
    candidates = [
        # Candidate 1: Simple business rates
        {
            'name': 'Business Rates v1',
            'formula': lambda d, m, r: 100 * d + 0.56 * m + 0.8 * r,
            'desc': '100*days + 0.56*miles + 0.8*receipts'
        },
        
        # Candidate 2: Progressive per-day rate
        {
            'name': 'Progressive Daily Rate',
            'formula': lambda d, m, r: (80 + d * 5) * d + 0.6 * m + 0.75 * r,
            'desc': '(80 + 5*days)*days + 0.6*miles + 0.75*receipts'
        },
        
        # Candidate 3: Logarithmic receipt scaling
        {
            'name': 'Log Receipt Scaling',
            'formula': lambda d, m, r: 90 * d + 0.55 * m + 100 * math.log1p(r),
            'desc': '90*days + 0.55*miles + 100*log(receipts+1)'
        },
        
        # Candidate 4: Distance-based rates
        {
            'name': 'Distance-Based Rates',
            'formula': lambda d, m, r: 75 * d + (0.5 + 0.1 * min(d, 10)) * m + 0.7 * r,
            'desc': '75*days + (0.5 + 0.1*min(days,10))*miles + 0.7*receipts'
        },
        
        # Candidate 5: Receipt percentage based on trip length
        {
            'name': 'Trip-Length Receipt %',
            'formula': lambda d, m, r: 85 * d + 0.58 * m + (0.6 + 0.05 * min(d, 8)) * r,
            'desc': '85*days + 0.58*miles + (0.6 + 0.05*min(days,8))*receipts'
        }
    ]
    
    best_score = float('inf')
    best_candidate = None
    
    for candidate in candidates:
        print(f"\nTesting: {candidate['name']}")
        print(f"Formula: {candidate['desc']}")
        
        try:
            errors = []
            exact_matches = 0
            
            for days, miles, receipts, expected in test_data:
                predicted = candidate['formula'](days, miles, receipts)
                error = abs(predicted - expected)
                errors.append(error)
                
                if error < 0.01:
                    exact_matches += 1
            
            avg_error = np.mean(errors)
            max_error = np.max(errors)
            score = avg_error * 100 + (1000 - exact_matches) * 0.1
            
            print(f"  Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
            print(f"  Average error: ${avg_error:.2f}")
            print(f"  Max error: ${max_error:.2f}")
            print(f"  Score: {score:.2f}")
            
            if score < best_score:
                best_score = score
                best_candidate = candidate
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\n=== BEST UNIVERSAL FUNCTION ===")
    if best_candidate:
        print(f"Best: {best_candidate['name']}")
        print(f"Formula: {best_candidate['desc']}")
        print(f"Score: {best_score:.2f}")
    else:
        print("No successful candidates found")

def search_for_perfect_function(public_cases):
    """Use optimization to search for the perfect analytical function"""
    
    print(f"\n=== SEARCHING FOR PERFECT ANALYTICAL FUNCTION ===")
    
    # Test the most promising pattern from our coefficient analysis
    # Many cases seem to use variations of: a*days + b*miles + c*receipts + d
    
    from scipy.optimize import minimize
    
    def test_function(params, test_data):
        """Test a parameterized function"""
        total_error = 0
        for days, miles, receipts, expected in test_data:
            try:
                # Parameterized function: base rate per day + mileage + receipt percentage + adjustments
                a, b, c, d, e, f = params
                
                # Complex function with conditional logic
                predicted = (
                    a * days +  # base per day
                    b * miles +  # mileage rate
                    c * receipts +  # receipt rate
                    d +  # base constant
                    e * (days * miles) / 1000 +  # interaction term
                    f * math.log1p(receipts)  # logarithmic receipt scaling
                )
                
                error = abs(predicted - expected)
                total_error += error
                
            except:
                total_error += 1000  # Heavy penalty for invalid calculations
        
        return total_error
    
    # Prepare test data
    test_data = []
    for case in public_cases:
        input_data = case['input']
        days = input_data['trip_duration_days']
        miles = input_data['miles_traveled']
        receipts = input_data['total_receipts_amount']
        expected = case['expected_output']
        test_data.append((days, miles, receipts, expected))
    
    # Try multiple starting points
    starting_points = [
        [80, 0.6, 0.8, 0, 0, 0],  # Simple linear
        [100, 0.56, 0.75, -50, 0.1, 20],  # With interactions
        [75, 0.5, 1.0, 100, 0, 50],  # High receipt rate
        [90, 0.55, 0.7, 20, 0.05, 30],  # Balanced approach
    ]
    
    best_params = None
    best_error = float('inf')
    
    for i, start_params in enumerate(starting_points):
        print(f"\nOptimizing from starting point {i+1}...")
        
        try:
            result = minimize(
                test_function,
                start_params,
                args=(test_data,),
                method='Nelder-Mead',
                options={'maxiter': 1000}
            )
            
            if result.fun < best_error:
                best_error = result.fun
                best_params = result.x
                
            print(f"  Total error: {result.fun:.2f}")
            print(f"  Parameters: {[f'{p:.3f}' for p in result.x]}")
            
        except Exception as e:
            print(f"  Optimization failed: {e}")
    
    if best_params is not None:
        print(f"\n=== BEST OPTIMIZED FUNCTION ===")
        a, b, c, d, e, f = best_params
        print(f"Formula: {a:.3f}*days + {b:.3f}*miles + {c:.3f}*receipts + {d:.3f} + {e:.3f}*(days*miles)/1000 + {f:.3f}*log(receipts+1)")
        
        # Test the best function
        exact_matches = 0
        errors = []
        for days, miles, receipts, expected in test_data:
            predicted = (
                a * days + b * miles + c * receipts + d +
                e * (days * miles) / 1000 + f * math.log1p(receipts)
            )
            error = abs(predicted - expected)
            errors.append(error)
            if error < 0.01:
                exact_matches += 1
        
        avg_error = np.mean(errors)
        score = avg_error * 100 + (1000 - exact_matches) * 0.1
        
        print(f"Exact matches: {exact_matches}/1000 ({exact_matches/10:.1f}%)")
        print(f"Average error: ${avg_error:.2f}")
        print(f"Score: {score:.2f}")
        
        return best_params
    
    return None

def main():
    """Main analysis pipeline"""
    print("ANALYTICAL FUNCTION SEARCH")
    print("=" * 50)
    
    # Load data
    public_cases, formulas = load_data()
    print(f"Loaded {len(public_cases)} public cases and {len(formulas)} discovered formulas")
    
    # Phase 1: Analyze coefficient patterns
    linear_df = analyze_coefficient_patterns(public_cases, formulas)
    
    # Phase 2: Test universal functions
    test_universal_functions(public_cases)
    
    # Phase 3: Optimization search
    best_params = search_for_perfect_function(public_cases)
    
    print(f"\n=== SUMMARY ===")
    print(f"Current best: 496 exact matches with case-specific formulas")
    print(f"Goal: Find single analytical function with 1000 exact matches")
    print(f"Next: Implement best candidate function and test")

if __name__ == "__main__":
    main()