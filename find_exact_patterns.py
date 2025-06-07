#!/usr/bin/env python3
"""
Systematic search for exact mathematical patterns to achieve score 0
"""

import json
import numpy as np
from collections import defaultdict
import itertools

# Load public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print("🔍 Systematic Pattern Analysis for Perfect Score")
print("=" * 60)

# Extract data
data = []
for case in cases[:100]:  # Use first 100 for speed
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    expected = case['expected_output']
    
    data.append({
        'days': days,
        'miles': miles,
        'receipts': receipts,
        'expected': expected,
        'mpd': miles / days,
        'rpd': receipts / days,
        'per_day': expected / days
    })

print(f"Analyzing {len(data)} cases for exact patterns...")

# Look for exact mathematical relationships
def test_formula(formula_func, description):
    """Test a mathematical formula against all cases"""
    exact_matches = 0
    close_matches = 0
    errors = []
    
    for d in data:
        try:
            predicted = formula_func(d)
            error = abs(predicted - d['expected'])
            errors.append(error)
            
            if error < 0.01:
                exact_matches += 1
            elif error < 1.0:
                close_matches += 1
                
        except:
            errors.append(999999)
    
    avg_error = np.mean(errors)
    return {
        'description': description,
        'exact_matches': exact_matches,
        'close_matches': close_matches,
        'avg_error': avg_error,
        'score': avg_error * 100
    }

# Test various formula patterns
print("\n📊 Testing Mathematical Formulas:")
print("-" * 40)

# Simple linear combinations
formulas = [
    (lambda d: d['days'] * 50 + d['miles'] * 0.5 + d['receipts'] * 0.3, 
     "50*days + 0.5*miles + 0.3*receipts"),
    
    (lambda d: d['days'] * 60 + d['miles'] * 0.6 + d['receipts'] * 0.4, 
     "60*days + 0.6*miles + 0.4*receipts"),
    
    (lambda d: d['days'] * 70 + d['miles'] * 0.4 + d['receipts'] * 0.5,
     "70*days + 0.4*miles + 0.5*receipts"),
    
    (lambda d: d['days'] * 80 + d['miles'] * 0.3 + d['receipts'] * 0.6,
     "80*days + 0.3*miles + 0.6*receipts"),
     
    # Non-linear patterns
    (lambda d: d['days'] * 60 + d['miles'] * 0.5 + d['receipts'] * 0.4 + (d['days'] * d['miles']) / 100,
     "60*days + 0.5*miles + 0.4*receipts + (days*miles)/100"),
     
    (lambda d: d['days'] * 70 + d['miles'] * 0.4 + d['receipts'] * 0.3 + np.log1p(d['receipts']) * 20,
     "70*days + 0.4*miles + 0.3*receipts + 20*log(1+receipts)"),
     
    (lambda d: d['days'] * 75 + d['miles'] * 0.45 + d['receipts'] * 0.35 + 100 / (1 + d['receipts']),
     "75*days + 0.45*miles + 0.35*receipts + 100/(1+receipts)"),
]

results = []
for formula, desc in formulas:
    result = test_formula(formula, desc)
    results.append(result)
    print(f"{desc:50} | Exact: {result['exact_matches']:2d} | Close: {result['close_matches']:2d} | Score: {result['score']:8.1f}")

print(f"\n🏆 Best Formula: {min(results, key=lambda x: x['score'])['description']}")
print(f"Best Score: {min(results, key=lambda x: x['score'])['score']:.1f}")

# Look for case-by-case patterns
print("\n🔍 Looking for Exact Case Matches:")
print("-" * 40)

exact_formulas_found = []
for i, d in enumerate(data[:20]):  # Check first 20 cases
    days, miles, receipts, expected = d['days'], d['miles'], d['receipts'], d['expected']
    
    # Try to find exact formula for this specific case
    found_exact = False
    
    # Try different coefficient combinations
    for a in range(20, 121, 10):  # days coefficient
        for b in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:  # miles coefficient
            for c in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:  # receipts coefficient
                predicted = a * days + b * miles + c * receipts
                if abs(predicted - expected) < 0.01:
                    exact_formulas_found.append({
                        'case': i+1,
                        'formula': f"{a}*{days} + {b}*{miles:.1f} + {c}*{receipts:.2f} = {expected:.2f}",
                        'coeffs': (a, b, c)
                    })
                    found_exact = True
                    print(f"Case {i+1}: {a}*days + {b}*miles + {c}*receipts = {expected:.2f} ✅")
                    break
            if found_exact:
                break
        if found_exact:
            break
    
    if not found_exact:
        print(f"Case {i+1}: No exact linear formula found ❌")

# Analyze coefficient patterns
if exact_formulas_found:
    print(f"\n📈 Coefficient Analysis ({len(exact_formulas_found)} exact matches):")
    days_coeffs = [f['coeffs'][0] for f in exact_formulas_found]
    miles_coeffs = [f['coeffs'][1] for f in exact_formulas_found]
    receipts_coeffs = [f['coeffs'][2] for f in exact_formulas_found]
    
    print(f"Days coefficients: {set(days_coeffs)}")
    print(f"Miles coefficients: {set(miles_coeffs)}")
    print(f"Receipts coefficients: {set(receipts_coeffs)}")

# Look for clustering patterns
print("\n🎯 Output Value Clustering:")
print("-" * 40)

# Group outputs by value ranges
output_clusters = defaultdict(list)
for d in data:
    bucket = round(d['expected'] / 50) * 50  # Group by $50 buckets
    output_clusters[bucket].append(d)

# Show largest clusters
sorted_clusters = sorted(output_clusters.items(), key=lambda x: len(x[1]), reverse=True)
for bucket, cases in sorted_clusters[:10]:
    if len(cases) > 1:
        print(f"${bucket} bucket: {len(cases)} cases")
        # Check if these cases share common patterns
        days_set = set(c['days'] for c in cases)
        if len(days_set) == 1:
            print(f"  → All have {list(days_set)[0]} days")

print("\n💡 Key Insights:")
print("- Multiple exact formulas exist for individual cases")
print("- No single formula works for all cases")
print("- The system likely uses different calculation paths")
print("- Decision tree approach is probably correct")
print("- Need to identify the branching conditions")