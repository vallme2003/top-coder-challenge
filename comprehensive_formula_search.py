#!/usr/bin/env python3
"""
Comprehensive Formula Search - Test every case systematically
Goal: Find exact mathematical formulas for as many cases as possible
"""

import json
import numpy as np
from collections import defaultdict
import itertools

# Load ALL public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print(f"🔍 COMPREHENSIVE FORMULA SEARCH - {len(cases)} cases")
print("=" * 60)

exact_formulas = []
formula_patterns = defaultdict(list)

def test_linear_formula(days, miles, receipts, expected):
    """Test all reasonable linear formula combinations"""
    
    # Expanded coefficient ranges based on our discoveries
    days_coeffs = range(20, 151, 5)      # 20 to 150, step 5
    miles_coeffs = [x/100 for x in range(10, 101, 5)]  # 0.1 to 1.0, step 0.05
    receipts_coeffs = [x/100 for x in range(10, 101, 5)]  # 0.1 to 1.0, step 0.05
    
    for a in days_coeffs:
        for b in miles_coeffs:
            for c in receipts_coeffs:
                predicted = a * days + b * miles + c * receipts
                if abs(predicted - expected) < 0.01:
                    return (a, b, c), predicted
    
    return None, None

def test_nonlinear_formulas(days, miles, receipts, expected):
    """Test non-linear formulas"""
    
    # Common non-linear patterns
    formulas_to_test = [
        # With constants
        lambda d, m, r, a, b, c, k: a * d + b * m + c * r + k,
        # With squares
        lambda d, m, r, a, b, c: a * d + b * m + c * r + 0.01 * d * d,
        lambda d, m, r, a, b, c: a * d + b * m + c * r + 0.001 * m * m,
        # With interactions
        lambda d, m, r, a, b, c: a * d + b * m + c * r + 0.01 * d * m,
        lambda d, m, r, a, b, c: a * d + b * m + c * r + 0.01 * d * r,
        # With logarithms
        lambda d, m, r, a, b, c: a * d + b * m + c * r + 10 * np.log1p(r),
        # With inverse
        lambda d, m, r, a, b, c: a * d + b * m + c * r + 100 / (1 + r),
    ]
    
    # Test a smaller range for non-linear to keep it manageable
    days_coeffs = range(50, 121, 10)
    miles_coeffs = [x/10 for x in range(2, 8)]  # 0.2 to 0.7
    receipts_coeffs = [x/10 for x in range(2, 8)]  # 0.2 to 0.7
    
    for formula in formulas_to_test:
        for a in days_coeffs:
            for b in miles_coeffs:
                for c in receipts_coeffs:
                    try:
                        if formula.__code__.co_argcount == 7:  # Has constant k
                            for k in range(-50, 51, 10):
                                predicted = formula(days, miles, receipts, a, b, c, k)
                                if abs(predicted - expected) < 0.01:
                                    return f"{formula.__name__}({a}, {b}, {c}, {k})", predicted
                        else:
                            predicted = formula(days, miles, receipts, a, b, c)
                            if abs(predicted - expected) < 0.01:
                                return f"{formula.__name__}({a}, {b}, {c})", predicted
                    except:
                        continue
    
    return None, None

# Analyze each case systematically
print("Searching for exact formulas...")

for i, case in enumerate(cases):
    if i % 100 == 0:
        print(f"Progress: {i}/{len(cases)} cases analyzed...")
    
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    expected = case['expected_output']
    
    # Try linear formula first
    coeffs, predicted = test_linear_formula(days, miles, receipts, expected)
    
    if coeffs:
        exact_formulas.append({
            'case_num': i + 1,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'formula_type': 'linear',
            'coeffs': coeffs,
            'formula': f"{coeffs[0]}*{days} + {coeffs[1]}*{miles:.1f} + {coeffs[2]}*{receipts:.2f} = {expected:.2f}"
        })
        
        # Group by coefficient pattern
        pattern_key = f"{coeffs[0]}_{coeffs[1]}_{coeffs[2]}"
        formula_patterns[pattern_key].append({
            'case': i + 1,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected
        })
        
        continue
    
    # If linear didn't work, try non-linear
    nonlinear_formula, predicted = test_nonlinear_formulas(days, miles, receipts, expected)
    
    if nonlinear_formula:
        exact_formulas.append({
            'case_num': i + 1,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'formula_type': 'nonlinear',
            'formula': nonlinear_formula
        })

print(f"\n🎯 RESULTS: Found {len(exact_formulas)} exact formulas!")
print("=" * 60)

# Show all exact formulas found
for formula in exact_formulas[:20]:  # Show first 20
    print(f"Case {formula['case_num']:3d}: {formula['formula']}")

if len(exact_formulas) > 20:
    print(f"... and {len(exact_formulas) - 20} more!")

# Analyze coefficient patterns
print(f"\n📊 COEFFICIENT PATTERN ANALYSIS:")
print("-" * 40)

# Group formulas by coefficient patterns
pattern_counts = [(pattern, len(cases)) for pattern, cases in formula_patterns.items()]
pattern_counts.sort(key=lambda x: x[1], reverse=True)

print("Most common coefficient patterns:")
for pattern, count in pattern_counts[:10]:
    if count > 1:
        coeffs = pattern.split('_')
        print(f"  {coeffs[0]}*days + {coeffs[1]}*miles + {coeffs[2]}*receipts: {count} cases")
        
        # Show which cases use this pattern
        cases_with_pattern = formula_patterns[pattern]
        print(f"    Cases: {[c['case'] for c in cases_with_pattern[:5]]}")
        
        # Look for commonalities
        days_values = [c['days'] for c in cases_with_pattern]
        if len(set(days_values)) == 1:
            print(f"    → All cases have {days_values[0]} days")
        
        miles_ranges = [c['miles'] for c in cases_with_pattern]
        if max(miles_ranges) - min(miles_ranges) < 50:
            print(f"    → Miles range: {min(miles_ranges):.0f}-{max(miles_ranges):.0f}")
        
        print()

# Generate optimized decision tree
print(f"\n🌳 DECISION TREE GENERATION:")
print("-" * 40)

print("Based on the patterns found, here's the decision logic:")

# Group by days first
days_groups = defaultdict(list)
for formula in exact_formulas:
    days_groups[formula['days']].append(formula)

for days in sorted(days_groups.keys()):
    formulas_for_days = days_groups[days]
    print(f"\nFor {days} day trips ({len(formulas_for_days)} exact formulas):")
    
    # Look for sub-patterns within this day group
    coeffs_in_group = defaultdict(list)
    for f in formulas_for_days:
        if f['formula_type'] == 'linear':
            coeffs_in_group[f['coeffs']].append(f)
    
    for coeffs, cases_list in coeffs_in_group.items():
        if len(cases_list) > 1:
            print(f"  Pattern: {coeffs[0]}*days + {coeffs[1]}*miles + {coeffs[2]}*receipts")
            print(f"    Used by {len(cases_list)} cases")
            
            # Find conditions for this pattern
            miles_range = [c['miles'] for c in cases_list]
            receipts_range = [c['receipts'] for c in cases_list]
            
            print(f"    Miles: {min(miles_range):.0f}-{max(miles_range):.0f}")
            print(f"    Receipts: ${min(receipts_range):.2f}-${max(receipts_range):.2f}")

print(f"\n💡 IMPLEMENTATION STRATEGY:")
print("-" * 40)
print(f"1. Found {len(exact_formulas)} exact formulas out of {len(cases)} cases")
print(f"2. Success rate: {len(exact_formulas)/len(cases)*100:.1f}%")
print(f"3. Need to implement {len(pattern_counts)} different coefficient patterns")
print(f"4. Use decision tree based on days, then miles/receipts ranges")

# Save results for implementation
with open('exact_formulas_found.json', 'w') as f:
    json.dump(exact_formulas, f, indent=2)

print(f"\n✅ Results saved to 'exact_formulas_found.json'")
print(f"Ready to implement comprehensive decision tree!")