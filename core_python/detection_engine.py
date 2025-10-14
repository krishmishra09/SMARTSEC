# detection_engine.py
import joblib
import pandas as pd

class DetectionEngine:
    def __init__(self, iso_forest_path, rf_path, label_encoder_path):
        print("Loading detection models...")
        self.iso_forest_model = joblib.load(iso_forest_path)
        self.rf_model = joblib.load(rf_path)
        self.label_encoder = joblib.load(label_encoder_path)
        print("Models loaded successfully.")

    def simple_rules(self, metrics):
        """A simple rule-based detection engine that handles the new flat structure."""
        alerts = []
        # NOTE: Host metrics check is removed as the host_agent sends a different structure.
        # This part of the engine now focuses only on network_flow.
        if metrics.get('type') == 'network_flow':
            # MODIFIED: Access 'packet_rate' directly from metrics, not metrics['data']
            if metrics.get('packet_rate', 0) > 1000: # Packets per second
                 alerts.append({
                    "type": "Rule-Based Alert",
                    "severity": "Critical",
                    "description": "High Packet Rate Detected (Potential Flood Attack)",
                    # MODIFIED: Access features directly from metrics
                    "details": f"Packet rate is {metrics.get('packet_rate', 0):.2f} pps for flow {metrics.get('flow_key')}"
                })
        return alerts

    def detect_threats(self, metrics_json):
        """
        Runs the incoming data through all detection mechanisms.
        """
        all_alerts = []
        
        # 1. Run through simple rules (now works with flat data)
        all_alerts.extend(self.simple_rules(metrics_json))
        
        # This function should only process network data for ML models
        if metrics_json.get('type') != 'network_flow':
            return all_alerts

        # MODIFIED: Prepare data directly from the flat metrics_json, not from a nested 'data' key
        df = pd.DataFrame([metrics_json])
        
        # 2. Run through Anomaly Detection (Isolation Forest)
        try:
            iso_forest_features = self.iso_forest_model.feature_names_in_
            
            # Check if all required columns are present
            if all(feature in df.columns for feature in iso_forest_features):
                df_iso = df[iso_forest_features]
                
                anomaly_score = self.iso_forest_model.decision_function(df_iso)
                if anomaly_score[0] < -0.1: # Threshold can be tuned
                    all_alerts.append({
                        "type": "Anomaly-Based Alert",
                        "severity": "Medium",
                        "description": "Anomalous Behavior Detected",
                        # MODIFIED: Fixed the numpy array formatting bug
                        "details": f"Anomaly score of {anomaly_score[0]:.2f}."
                    })
            else:
                # This can happen if a packet is missing some features
                missing_cols = [f for f in iso_forest_features if f not in df.columns]
                # print(f"Warning: Missing columns for anomaly detection: {missing_cols}") # Optional debug message
                pass

        except Exception as e:
            print(f"Error during anomaly detection: {e}")

        # 3. Placeholder for Signature Detection (Random Forest)
        # ...

        return all_alerts

# Example Usage part is removed for clarity as it's not needed for the main application