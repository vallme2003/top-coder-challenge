import json
import sys

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculate expense reimbursement based on trip parameters.
    
    This function implements the reverse-engineered formula from the legacy system.
    Based on extensive analysis of 1000 public cases and employee interviews.
    """
    
    # Optimized linear formula based on least squares analysis
    # This gives the best overall fit to the 1000 test cases
    
    days_coefficient = 62.839410
    receipts_coefficient = 0.436038
    miles_coefficient = 0.579790
    
    # The core formula
    reimbursement = (
        days_coefficient * trip_duration_days +
        receipts_coefficient * total_receipts_amount +
        miles_coefficient * miles_traveled
    )
    
    return reimbursement

def main():
    # Read input from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    results = []
    
    for case in input_data:
        trip_duration_days = case['trip_duration_days']
        miles_traveled = case['miles_traveled']
        total_receipts_amount = case['total_receipts_amount']
        
        reimbursement = calculate_reimbursement(
            trip_duration_days, 
            miles_traveled, 
            total_receipts_amount
        )
        
        results.append(reimbursement)
    
    # Output results
    json.dump(results, sys.stdout)

if __name__ == "__main__":
    main()