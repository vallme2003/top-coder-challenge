#!/usr/bin/env python3
import json
import numpy as np
import joblib
from sklearn.tree import DecisionTreeRegressor

# Load data and model
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

model = joblib.load('gradient_boost_model.pkl')

# Generate predictions for analysis
predictions = []
for case in cases:
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    # Extract features (simplified - just key ones)
    mpd = miles / days if days > 0 else 0
    rpd = receipts / days if days > 0 else 0
    
    features = [
        days, miles, receipts, mpd, rpd,
        days ** 2, miles ** 2, receipts ** 2, days ** 3,
        days * miles, days * receipts, miles * receipts,
        days * miles * receipts / 1000,
        np.log1p(days), np.log1p(miles), np.log1p(receipts),
        1 / (1 + receipts), 1 / (1 + miles),
        1 if days == 5 else 0, 1 if days >= 7 else 0,
        1 if receipts < 50 else 0, 1 if receipts > 1000 else 0,
        1 if 180 <= mpd <= 220 else 0,
        1 if 50 <= receipts < 200 else 0,
        1 if 200 <= receipts < 500 else 0,
        1 if 500 <= receipts < 1000 else 0,
        int(receipts * 100) % 100,
        1 if int(receipts * 100) % 100 == 49 else 0,
        1 if int(receipts * 100) % 100 == 99 else 0,
        1 if mpd < 50 else 0, 1 if 50 <= mpd < 100 else 0,
        1 if 100 <= mpd < 150 else 0, 1 if mpd >= 150 else 0
    ]
    
    X = np.array(features).reshape(1, -1)
    pred = model.predict(X)[0]
    
    predictions.append({
        'days': days,
        'miles': miles,
        'receipts': receipts,
        'expected': case['expected_output'],
        'predicted': pred,
        'error': abs(pred - case['expected_output'])
    })

# Analyze patterns
print("Analyzing model predictions...")
print(f"Average error: ${np.mean([p['error'] for p in predictions]):.2f}")

# Try to fit a simpler model that approximates the complex one
print("\nFitting simplified approximation...")

# Create simplified features
X_simple = []
y_target = []

for p in predictions:
    days = p['days']
    miles = p['miles']
    receipts = p['receipts']
    
    # Key features identified by GB model
    features = [
        1 / (1 + receipts),  # Most important
        days * miles * receipts / 1000,  # 3-way interaction
        np.log1p(receipts),
        days * miles,
        receipts ** 2 / 1e6,  # Scaled
        receipts,
        days * receipts,
        miles * receipts / 1000,
        days,
        miles,
        1 if days == 5 else 0,
        1 if int(receipts * 100) % 100 == 49 else 0,
        1 if int(receipts * 100) % 100 == 99 else 0,
    ]
    
    X_simple.append(features)
    y_target.append(p['predicted'])  # Target the GB model's predictions

X_simple = np.array(X_simple)
y_target = np.array(y_target)

# Fit a simpler decision tree
simple_model = DecisionTreeRegressor(max_depth=8, min_samples_leaf=20)
simple_model.fit(X_simple, y_target)

# Evaluate approximation
y_approx = simple_model.predict(X_simple)
approx_error = np.mean(np.abs(y_approx - y_target))
print(f"Approximation error: ${approx_error:.2f}")

# Generate code for the decision tree
print("\nGenerating decision tree code...")

def generate_tree_code(tree, feature_names):
    def recurse(node=0, depth=0):
        indent = "    " * depth
        
        if tree.feature[node] == -2:  # Leaf node
            return f"{indent}return {tree.value[node][0][0]:.2f}"
        else:
            feature = feature_names[tree.feature[node]]
            threshold = tree.threshold[node]
            
            code = f"{indent}if {feature} <= {threshold:.6f}:\n"
            code += recurse(tree.children_left[node], depth + 1) + "\n"
            code += f"{indent}else:\n"
            code += recurse(tree.children_right[node], depth + 1)
            
            return code
    
    return recurse()

feature_names = [
    '1/(1+receipts)', '3way', 'log_receipts', 'days_miles',
    'receipts_sq_scaled', 'receipts', 'days_receipts', 'miles_receipts_scaled',
    'days', 'miles', '5day', 'ends49', 'ends99'
]

tree_code = generate_tree_code(simple_model.tree_, feature_names)

# Save the approximation code
with open('tree_approximation.py', 'w') as f:
    f.write("""def predict_reimbursement(days, miles, receipts):
    # Features
    inv_receipts = 1 / (1 + receipts)
    three_way = days * miles * receipts / 1000
    log_receipts = np.log1p(receipts)
    days_miles = days * miles
    receipts_sq_scaled = receipts ** 2 / 1e6
    days_receipts = days * receipts
    miles_receipts_scaled = miles * receipts / 1000
    five_day = 1 if days == 5 else 0
    ends49 = 1 if int(receipts * 100) % 100 == 49 else 0
    ends99 = 1 if int(receipts * 100) % 100 == 99 else 0
    
    # Decision tree
""")
    f.write(tree_code.replace('1/(1+receipts)', 'inv_receipts')
                     .replace('3way', 'three_way')
                     .replace('log_receipts', 'log_receipts')
                     .replace('days_miles', 'days_miles')
                     .replace('receipts_sq_scaled', 'receipts_sq_scaled')
                     .replace('days_receipts', 'days_receipts')
                     .replace('miles_receipts_scaled', 'miles_receipts_scaled')
                     .replace('5day', 'five_day')
                     .replace('ends49', 'ends49')
                     .replace('ends99', 'ends99'))

print("Tree approximation saved to tree_approximation.py")