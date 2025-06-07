#!/bin/bash

# Black Box Challenge - Your Implementation
# This script should take three parameters and output the reimbursement amount
# Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>

# Tree model - proven best competitive performance (9,150 score)
python3 calculate_reimbursement_tree.py "$1" "$2" "$3" 