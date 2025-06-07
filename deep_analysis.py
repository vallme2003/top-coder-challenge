#!/usr/bin/env python3
import json
import statistics
import math

with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Function to attempt various calculations
def analyze_case(inp, expected):
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    # Calculate efficiency
    mpd = miles / days if days > 0 else 0
    
    # Try different base calculations
    results = {}
    
    # Base per diem approach
    per_diem = 100 * days
    
    # Mileage calculations - try different approaches
    if miles <= 100:
        mileage1 = miles * 0.58
    else:
        mileage1 = 100 * 0.58 + (miles - 100) * 0.40  # Tiered
    
    # Efficiency bonus?
    efficiency_bonus = 0
    if 180 <= mpd <= 220:
        efficiency_bonus = 50  # Flat bonus?
    elif mpd > 100:
        efficiency_bonus = 20
    
    # 5-day bonus?
    day_bonus = 0
    if days == 5:
        day_bonus = 50  # Mentioned in interviews
    
    # Receipt handling - various approaches
    if receipts < 50:
        receipt_reimbursement = receipts * 0.5  # Penalty for small receipts
    elif receipts < 200:
        receipt_reimbursement = receipts * 0.8
    elif receipts < 800:
        receipt_reimbursement = receipts * 0.85  # Better rate for medium
    else:
        receipt_reimbursement = 800 * 0.85 + (receipts - 800) * 0.5  # Diminishing returns
    
    # Total calculation
    total = per_diem + mileage1 + receipt_reimbursement + efficiency_bonus + day_bonus
    
    # Check for rounding patterns
    if int(receipts * 100) % 100 in [49, 99]:
        total += 5  # Rounding bonus?
    
    return {
        'expected': expected,
        'calculated': round(total, 2),
        'diff': round(expected - total, 2),
        'per_diem': per_diem,
        'mileage': round(mileage1, 2),
        'receipts': round(receipt_reimbursement, 2),
        'efficiency_bonus': efficiency_bonus,
        'day_bonus': day_bonus,
        'mpd': round(mpd, 2)
    }

# Test on sample cases
print("Testing calculation approach on sample cases:")
print("-" * 80)

for i, case in enumerate(cases[:20]):
    inp = case['input']
    expected = case['expected_output']
    result = analyze_case(inp, expected)
    
    print(f"Case {i+1}: Days={inp['trip_duration_days']}, Miles={inp['miles_traveled']}, Receipts=${inp['total_receipts_amount']:.2f}")
    print(f"  Expected: ${expected:.2f}, Calculated: ${result['calculated']:.2f}, Diff: ${result['diff']:.2f}")
    print(f"  Components: Per diem=${result['per_diem']}, Mileage=${result['mileage']}, Receipts=${result['receipts']}")
    print(f"  Bonuses: Efficiency=${result['efficiency_bonus']}, Day=${result['day_bonus']}, MPD={result['mpd']}")
    print()

# Look for patterns in errors
errors = []
for case in cases:
    result = analyze_case(case['input'], case['expected_output'])
    errors.append(abs(result['diff']))

print(f"Average absolute error: ${statistics.mean(errors):.2f}")
print(f"Median absolute error: ${statistics.median(errors):.2f}")
print(f"Max error: ${max(errors):.2f}")

# Find cases with large errors to understand what we're missing
large_errors = []
for case in cases:
    result = analyze_case(case['input'], case['expected_output'])
    if abs(result['diff']) > 100:
        large_errors.append((case, result))

print(f"\nCases with large errors (>${100}):")
for case, result in sorted(large_errors, key=lambda x: abs(x[1]['diff']), reverse=True)[:10]:
    inp = case['input']
    print(f"Days={inp['trip_duration_days']}, Miles={inp['miles_traveled']}, Receipts=${inp['total_receipts_amount']:.2f}")
    print(f"  Expected: ${case['expected_output']:.2f}, Calculated: ${result['calculated']:.2f}, Diff: ${result['diff']:.2f}")
    print(f"  MPD: {result['mpd']}")