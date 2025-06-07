#!/usr/bin/env python3
import json
import statistics
import math

# Load the public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

print(f"Total cases: {len(cases)}")

# Basic statistics
days = [c['input']['trip_duration_days'] for c in cases]
miles = [c['input']['miles_traveled'] for c in cases]
receipts = [c['input']['total_receipts_amount'] for c in cases]
outputs = [c['expected_output'] for c in cases]

print(f"\nTrip duration range: {min(days)} - {max(days)} days")
print(f"Miles range: {min(miles)} - {max(miles)} miles")
print(f"Receipts range: ${min(receipts):.2f} - ${max(receipts):.2f}")
print(f"Output range: ${min(outputs):.2f} - ${max(outputs):.2f}")

# Analyze 5-day trips specifically (mentioned as special in interviews)
five_day_trips = [(c['input'], c['expected_output']) for c in cases if c['input']['trip_duration_days'] == 5]
print(f"\n5-day trips: {len(five_day_trips)}")

# Calculate per-day rates for different trip lengths
for d in range(1, 11):
    trips_d = [(c['input'], c['expected_output']) for c in cases if c['input']['trip_duration_days'] == d]
    if trips_d:
        avg_output = statistics.mean([t[1] for t in trips_d])
        per_day = avg_output / d
        print(f"{d}-day trips: {len(trips_d)} cases, avg output: ${avg_output:.2f}, per day: ${per_day:.2f}")

# Look for efficiency bonuses
print("\nEfficiency analysis (miles per day):")
for c in cases[:20]:  # Sample
    inp = c['input']
    out = c['expected_output']
    mpd = inp['miles_traveled'] / inp['trip_duration_days']
    base_per_diem = inp['trip_duration_days'] * 100  # $100/day base
    mileage = inp['miles_traveled'] * 0.58  # $0.58/mile base
    receipt_portion = inp['total_receipts_amount'] * 0.8  # 80% of receipts
    basic_calc = base_per_diem + mileage + receipt_portion
    diff = out - basic_calc
    print(f"Days: {inp['trip_duration_days']}, Miles: {inp['miles_traveled']}, MPD: {mpd:.1f}, Receipts: ${inp['total_receipts_amount']:.2f}, Output: ${out:.2f}, Basic calc: ${basic_calc:.2f}, Diff: ${diff:.2f}")

# Check for receipts ending in 49/99 cents
special_receipts = []
for c in cases:
    cents = int(round(c['input']['total_receipts_amount'] * 100)) % 100
    if cents == 49 or cents == 99:
        special_receipts.append(c)

print(f"\nReceipts ending in 49/99 cents: {len(special_receipts)}")

# Look for small receipt penalties
small_receipt_cases = [(c['input'], c['expected_output']) for c in cases if c['input']['total_receipts_amount'] < 50]
print(f"\nSmall receipt cases (<$50): {len(small_receipt_cases)}")
for inp, out in small_receipt_cases[:10]:
    base_calc = inp['trip_duration_days'] * 100 + inp['miles_traveled'] * 0.58
    print(f"Days: {inp['trip_duration_days']}, Miles: {inp['miles_traveled']}, Receipts: ${inp['total_receipts_amount']:.2f}, Output: ${out:.2f}, Base w/o receipts: ${base_calc:.2f}")