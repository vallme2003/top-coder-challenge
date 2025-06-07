#!/usr/bin/env python3
import joblib
import json

# Load the trained model
model = joblib.load('gradient_boost_model.pkl')

# Export model parameters
model_data = {
    'n_estimators': model.n_estimators,
    'learning_rate': model.learning_rate,
    'init_prediction': float(model.init_.constant_[0]),
    'trees': []
}

# Export each tree
for i, tree in enumerate(model.estimators_[:, 0]):
    tree_data = {
        'children_left': tree.tree_.children_left.tolist(),
        'children_right': tree.tree_.children_right.tolist(),
        'feature': tree.tree_.feature.tolist(),
        'threshold': tree.tree_.threshold.tolist(),
        'value': tree.tree_.value.tolist()
    }
    model_data['trees'].append(tree_data)
    
    if i % 50 == 0:
        print(f"Exported {i+1}/{model.n_estimators} trees")

# Save to JSON
with open('model_params.json', 'w') as f:
    json.dump(model_data, f)

print(f"\nModel exported to model_params.json")
print(f"File size: {len(json.dumps(model_data)) / 1024 / 1024:.2f} MB")