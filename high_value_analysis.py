#!/usr/bin/env python3
"""
High Value Analysis - Focus on $1400-$1900 range where most unsolved cases cluster
These might follow different business logic - perhaps lookup tables or stepped calculations
"""

import json
import numpy as np
import math
from collections import defaultdict

# Load data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

with open('exact_formulas_found.json', 'r') as f:
    exact_formulas = json.load(f)

# Focus on high-value unsolved cases ($1400-$1900)
exact_case_nums = {f['case_num'] for f in exact_formulas}
high_value_cases = []

for i, case in enumerate(cases):
    if (i + 1) not in exact_case_nums:
        expected = case['expected_output']
        if 1400 <= expected <= 1900:
            inp = case['input']
            high_value_cases.append({
                'case_num': i + 1,
                'days': inp['trip_duration_days'],
                'miles': inp['miles_traveled'],
                'receipts': inp['total_receipts_amount'],
                'expected': expected,
                'mpd': inp['miles_traveled'] / inp['trip_duration_days'],
                'rpd': inp['total_receipts_amount'] / inp['trip_duration_days']
            })

print(f"🎯 HIGH VALUE ANALYSIS - {len(high_value_cases)} cases ($1400-$1900)")
print("=" * 60)

# Look for stepped/bucket patterns
print("\n🪜 STEPPED CALCULATION ANALYSIS:")
print("-" * 40)

# Test if outputs follow stepped patterns
output_values = [c['expected'] for c in high_value_cases]
output_set = sorted(set(output_values))

print(f"Unique output values in range: {len(output_set)}")
print("Sample outputs:", output_set[:10])

# Look for regular intervals
intervals = []
for i in range(1, min(len(output_set), 20)):
    intervals.append(output_set[i] - output_set[i-1])

print(f"Common intervals: {sorted(set([round(x, 2) for x in intervals]))[:10]}")

# Test lookup table hypothesis
print("\n📚 LOOKUP TABLE HYPOTHESIS:")
print("-" * 40)

# Group by exact input combinations that might map to exact outputs
input_patterns = defaultdict(list)

for case in high_value_cases:
    # Try different input combination patterns
    patterns = [
        f"d{case['days']}",
        f"d{case['days']}_m{int(case['miles']/50)*50}",  # Miles in 50-unit buckets
        f"d{case['days']}_r{int(case['receipts']/100)*100}",  # Receipts in $100 buckets
        f"mpd{int(case['mpd']/10)*10}",  # Miles per day in 10-unit buckets
        f"rpd{int(case['rpd']/50)*50}",  # Receipts per day in $50 buckets
    ]
    
    for pattern in patterns:
        input_patterns[pattern].append(case)

# Find patterns with multiple cases having same output
for pattern, pattern_cases in input_patterns.items():
    if len(pattern_cases) >= 3:
        outputs = [c['expected'] for c in pattern_cases]
        if len(set(outputs)) == 1:  # All same output
            print(f"✓ Pattern '{pattern}' → ${outputs[0]:.2f} ({len(pattern_cases)} cases)")

# Test ratio-based formulas specifically for high-value cases
print("\n🔢 RATIO-BASED FORMULA TESTING:")
print("-" * 40)

def test_ratio_formulas(cases):
    """Test ratio-based formulas specifically for high-value cases"""
    
    matches = []
    
    for case in cases[:50]:  # Test subset for speed
        days = case['days']
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        
        # Ratio-based formulas that might apply to high-value cases
        tests = [
            # Daily rate formulas
            ('daily_rate_1', lambda: days * (200 + miles/days*1.5 + receipts/days*0.5)),
            ('daily_rate_2', lambda: days * (150 + (miles/days)**0.8 + (receipts/days)**0.6)),
            
            # Stepped formulas
            ('stepped_days', lambda: 1000 + (days-5)*100 + miles*0.3 + receipts*0.2 if days >= 5 else 0),
            ('stepped_miles', lambda: 1200 + max(0, miles-500)*0.8 + receipts*0.3),
            ('stepped_receipts', lambda: 800 + days*50 + miles*0.4 + max(0, receipts-1000)*0.6),
            
            # Compound formulas  
            ('compound_1', lambda: 500 + days*100*math.log(1+miles/1000) + receipts*0.3),
            ('compound_2', lambda: 1000 + (days*miles)**0.5 + receipts**0.7),
            
            # Legacy "tax bracket" style
            ('bracket_1', lambda: (1400 if receipts > 1500 else 1200) + days*20 + miles*0.2),
            ('bracket_2', lambda: (1500 if days > 7 else 1300) + miles*0.3 + receipts*0.1),
        ]
        
        for name, formula in tests:
            try:
                result = formula()
                if abs(result - expected) < 1.0:
                    matches.append({
                        'case': case['case_num'],
                        'formula': name,
                        'predicted': result,
                        'expected': expected,
                        'error': abs(result - expected)
                    })
                    print(f"✓ Case {case['case_num']}: {name} → {result:.2f} (exp: {expected:.2f}, err: {abs(result-expected):.2f})")
            except:
                pass
    
    return matches

matches = test_ratio_formulas(high_value_cases)

# Test if high-value cases follow a different coefficient pattern
print("\n🎱 HIGH-VALUE COEFFICIENT SEARCH:")
print("-" * 40)

def search_high_value_coefficients(cases):
    """Search for coefficient patterns specific to high-value cases"""
    
    # Focus on larger coefficient ranges since these are high-value outputs
    for a in range(100, 201, 20):  # Days coefficient
        for b in [0.5, 0.7, 0.9, 1.1, 1.3, 1.5]:  # Miles coefficient  
            for c in [0.1, 0.3, 0.5, 0.7, 0.9]:  # Receipts coefficient
                matches = 0
                for case in cases[:30]:  # Test subset
                    predicted = a * case['days'] + b * case['miles'] + c * case['receipts']
                    if abs(predicted - case['expected']) < 5.0:  # Looser tolerance
                        matches += 1
                
                if matches >= 3:
                    print(f"Coefficient pattern {a}*days + {b}*miles + {c}*receipts matches {matches} cases")
                    
                    # Test this pattern on a few specific cases
                    for case in cases[:5]:
                        predicted = a * case['days'] + b * case['miles'] + c * case['receipts']
                        error = abs(predicted - case['expected'])
                        if error < 10:
                            print(f"  Case {case['case_num']}: {predicted:.2f} vs {case['expected']:.2f} (err: {error:.2f})")

search_high_value_coefficients(high_value_cases)

print(f"\n💡 HIGH-VALUE INSIGHTS:")
print("-" * 40)
print("1. High-value cases ($1400-$1900) may use different calculation logic")
print("2. Could be lookup tables based on input buckets/ranges")
print("3. May use stepped calculations or tax-bracket style formulas")
print("4. Ratio-based formulas might apply (daily rates, compound effects)")

# Save high-value cases for focused implementation
with open('high_value_cases.json', 'w') as f:
    json.dump(high_value_cases, f, indent=2)

print(f"\n📝 Saved {len(high_value_cases)} high-value cases for focused implementation")