#!/usr/bin/env python3
"""
Deep Pattern Analysis - Opus 4 Enhanced
Goal: Find patterns in the 794 cases we couldn't solve with linear formulas
"""

import json
import numpy as np
from collections import defaultdict
import math

# Load all data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

with open('exact_formulas_found.json', 'r') as f:
    exact_formulas = json.load(f)

# Get cases WITHOUT exact formulas
exact_case_nums = {f['case_num'] for f in exact_formulas}
unsolved_cases = []

for i, case in enumerate(cases):
    if (i + 1) not in exact_case_nums:
        inp = case['input']
        unsolved_cases.append({
            'case_num': i + 1,
            'days': inp['trip_duration_days'],
            'miles': inp['miles_traveled'],
            'receipts': inp['total_receipts_amount'],
            'expected': case['expected_output'],
            'mpd': inp['miles_traveled'] / inp['trip_duration_days'],
            'rpd': inp['total_receipts_amount'] / inp['trip_duration_days'],
            'output_per_day': case['expected_output'] / inp['trip_duration_days']
        })

print(f"🔍 DEEP PATTERN ANALYSIS - {len(unsolved_cases)} unsolved cases")
print("=" * 60)

# Analyze patterns in unsolved cases
def find_complex_patterns(cases):
    """Look for more complex mathematical relationships"""
    
    patterns_found = []
    
    for case in cases[:100]:  # Sample for speed
        days = case['days']
        miles = case['miles']
        receipts = case['receipts']
        expected = case['expected']
        
        # Test complex formulas
        tests = [
            # Polynomial combinations
            ('quadratic_days', lambda: 50 + 20*days + 5*days*days + 0.3*miles + 0.2*receipts),
            ('sqrt_miles', lambda: 100*days + 10*math.sqrt(miles) + 0.3*receipts),
            ('log_all', lambda: 50*days + 20*math.log1p(miles) + 15*math.log1p(receipts)),
            
            # Ratio-based
            ('efficiency_based', lambda: 200 + (miles/days)*2.5 + receipts*0.3 if days > 0 else 0),
            ('spending_ratio', lambda: 150*days + miles*0.4 + (receipts/days)*0.8 if days > 0 else 0),
            
            # Threshold-based
            ('step_function', lambda: (100 if days <= 3 else 200) + miles*0.5 + receipts*0.3),
            
            # Complex interactions
            ('triple_product', lambda: 100 + (days*miles*receipts)**0.33),
            ('inverse_complex', lambda: 500 * (1/(1+days) + 1/(1+miles/100) + 1/(1+receipts/100))),
            
            # Modulo patterns (legacy system quirk?)
            ('modulo_pattern', lambda: 100*days + miles*0.5 + receipts*0.3 + (int(receipts*100) % 7)*5),
            
            # Ceiling/floor effects
            ('ceiling_effect', lambda: math.ceil(days/5)*200 + miles*0.4 + receipts*0.3),
        ]
        
        for name, formula in tests:
            try:
                result = formula()
                if abs(result - expected) < 0.1:
                    patterns_found.append({
                        'case': case['case_num'],
                        'pattern': name,
                        'error': abs(result - expected)
                    })
                    print(f"✓ Case {case['case_num']}: {name} matches!")
            except:
                pass
    
    return patterns_found

# Look for clustering in unsolved cases
print("\n📊 Clustering Analysis of Unsolved Cases:")
print("-" * 40)

# Group by output ranges
output_clusters = defaultdict(list)
for case in unsolved_cases:
    bucket = int(case['expected'] / 100) * 100
    output_clusters[bucket].append(case)

# Analyze largest clusters
for bucket in sorted(output_clusters.keys()):
    cluster = output_clusters[bucket]
    if len(cluster) >= 10:
        print(f"\n${bucket}-${bucket+100} range: {len(cluster)} cases")
        
        # Find commonalities
        days_values = [c['days'] for c in cluster]
        miles_values = [c['miles'] for c in cluster]
        receipts_values = [c['receipts'] for c in cluster]
        
        print(f"  Days: {min(days_values)}-{max(days_values)} (avg: {np.mean(days_values):.1f})")
        print(f"  Miles: {min(miles_values):.0f}-{max(miles_values):.0f} (avg: {np.mean(miles_values):.0f})")
        print(f"  Receipts: ${min(receipts_values):.2f}-${max(receipts_values):.2f} (avg: ${np.mean(receipts_values):.2f})")

# Look for exact output values that repeat
print("\n🎯 Repeated Exact Output Values:")
print("-" * 40)

output_counts = defaultdict(list)
for case in cases:
    output = case['expected_output']
    output_counts[output].append(case)

# Show outputs that appear multiple times
repeated_outputs = [(out, cases) for out, cases in output_counts.items() if len(cases) > 2]
repeated_outputs.sort(key=lambda x: len(x[1]), reverse=True)

for output, cases_list in repeated_outputs[:10]:
    print(f"\n${output:.2f} appears {len(cases_list)} times:")
    # Check if they share common inputs
    for i, case in enumerate(cases_list[:3]):
        inp = case['input']
        print(f"  Case {i+1}: {inp['trip_duration_days']}d, {inp['miles_traveled']:.0f}mi, ${inp['total_receipts_amount']:.2f}")

# Test complex patterns
print("\n🔬 Testing Complex Patterns:")
print("-" * 40)
patterns = find_complex_patterns(unsolved_cases)

# Final insights
print("\n💡 KEY INSIGHTS FOR PERFECT SCORE:")
print("-" * 40)
print("1. Many outputs repeat exactly - suggests lookup tables or discrete calculations")
print("2. Clustering around round numbers ($100 boundaries) - suggests bucketing")
print("3. Need to test non-linear formulas more extensively")
print("4. Consider legacy system quirks (modulo, ceiling, special cases)")

# Save unsolved cases for further analysis
with open('unsolved_cases.json', 'w') as f:
    json.dump(unsolved_cases, f, indent=2)

print(f"\n📝 Saved {len(unsolved_cases)} unsolved cases to 'unsolved_cases.json'")