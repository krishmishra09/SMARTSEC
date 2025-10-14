#this is just a sampler code to use isolation foresat to detect anaomaly in the network agent 

import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Assume 'normal_traffic_features.csv' is a file containing features 
# extracted from known benign traffic (e.g., from our network agent or CIC-IDS2017).
# The features should match those produced by our agents.
print("Loading normal data for training...")
try:
    # Example using network features. A similar model can be trained for host metrics.
    df = pd.read_csv('normal_network_features.csv')
except FileNotFoundError:
    print("Error: 'normal_network_features.csv' not found. Please create this file from benign traffic captures.")
    exit()

# Select features for the model
features = [
    'flow_duration', 'packet_count', 'byte_count', 
    'packet_rate', 'byte_rate', 'src_bytes', 'dst_bytes'
]
X_train = df[features]

print("Training Isolation Forest model...")
# contamination='auto' is a good starting point. It can be tuned.
# n_estimators is the number of trees in the forest.
model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
model.fit(X_train)

print("Model training complete. Saving model...")
joblib.dump(model, 'isolation_forest_model.joblib')
print("Model saved to 'isolation_forest_model.joblib'")

#To use the model, you would load it and call predict() or decision_function()
loaded_model = joblib.load('isolation_forest_model.joblib')
scores = loaded_model.decision_function(new_data) # Lower scores are more anomalous
predictions = loaded_model.predict(new_data) # -1 for anomalies, 1 for inliers