#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt

with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Group by receipt ranges and analyze reimbursement patterns
receipt_ranges = [
    (0, 50, "0-50"),
    (50, 100, "50-100"),
    (100, 200, "100-200"),
    (200, 400, "200-400"),
    (400, 800, "400-800"),
    (800, 1200, "800-1200"),
    (1200, 2000, "1200-2000"),
    (2000, 3000, "2000+")
]

for min_r, max_r, label in receipt_ranges:
    filtered = []
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        if min_r <= receipts < max_r:
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            output = case['expected_output']
            
            # Calculate base components
            base_per_diem = days * 100
            base_mileage = miles * 0.58
            base_without_receipts = base_per_diem + base_mileage
            
            # How much of the output is beyond base?
            excess = output - base_without_receipts
            receipt_contribution = excess / receipts if receipts > 0 else 0
            
            filtered.append({
                'receipts': receipts,
                'output': output,
                'days': days,
                'miles': miles,
                'base_without_receipts': base_without_receipts,
                'excess': excess,
                'receipt_contribution': receipt_contribution
            })
    
    if filtered:
        avg_contribution = sum(f['receipt_contribution'] for f in filtered) / len(filtered)
        print(f"\nReceipt range ${label}:")
        print(f"  Cases: {len(filtered)}")
        print(f"  Avg receipt contribution: {avg_contribution:.3f}")
        print(f"  Sample cases:")
        for f in sorted(filtered, key=lambda x: x['receipt_contribution'])[:5]:
            print(f"    Receipts=${f['receipts']:.2f}, Days={f['days']}, Output=${f['output']:.2f}, Base=${f['base_without_receipts']:.2f}, Excess=${f['excess']:.2f}, Contribution={f['receipt_contribution']:.3f}")

# Look specifically at high receipt cases
print("\n\nHigh receipt cases analysis:")
high_receipt_cases = [c for c in cases if c['input']['total_receipts_amount'] > 1000]
print(f"Total high receipt cases (>$1000): {len(high_receipt_cases)}")

for case in sorted(high_receipt_cases, key=lambda x: x['expected_output'])[:10]:
    inp = case['input']
    out = case['expected_output']
    base = inp['trip_duration_days'] * 100 + inp['miles_traveled'] * 0.58
    print(f"Days={inp['trip_duration_days']}, Miles={inp['miles_traveled']}, Receipts=${inp['total_receipts_amount']:.2f}")
    print(f"  Output=${out:.2f}, Base w/o receipts=${base:.2f}, Implied receipt portion=${out - base:.2f}")
    print(f"  Receipt reimbursement rate: {(out - base) / inp['total_receipts_amount']:.3f}")
    print()