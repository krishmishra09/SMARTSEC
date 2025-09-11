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

#simple_rule function called from detect_threats to check incoming metrics for basic rule-based alerts.
#The function is a rule-based detection engine.
#It checks system or network metrics and generates alerts if certain thresholds are exceeded.
    def simple_rules(self, metrics):
        """A simple rule-based detection engine."""
        alerts = []
        if metrics.get('type') == 'host_metrics':
            if metrics['data']['cpu_usage_percent'] > 95.0:
                alerts.append({
                    "type": "Rule-Based Alert",
                    "severity": "High",
                    "description": "High CPU Utilization Detected",
                    "details": f"CPU usage is at {metrics['data']['cpu_usage_percent']}%"
                })
        elif metrics.get('type') == 'network_flow':
            if metrics['data']['packet_rate'] > 1000: # Packets per second
                 alerts.append({
                    "type": "Rule-Based Alert",
                    "severity": "Critical",
                    "description": "High Packet Rate Detected (Potential Flood Attack)",
                    "details": f"Packet rate is {metrics['data']['packet_rate']:.2f} pps for flow {metrics['data']['flow_key']}"
                })
        return alerts

    def detect_threats(self, metrics_json):
        """
        Runs the incoming data through all detection mechanisms.
        :param metrics_json: The JSON object from a host or network agent.
        :return: A list of detected alerts.
        """
        all_alerts = []
        
        # 1. Run through simple rules
        all_alerts.extend(self.simple_rules(metrics_json))
        
        # Prepare data for ML models
        data = metrics_json['data']
        df = pd.DataFrame([data])
        #since data is dictonary so pd.dataframe([data]) convert dictonary key:value pair to the rows and column
        
        # 2. Run through Anomaly Detection (Isolation Forest)
        # Ensure columns match the training data
        iso_forest_features = self.iso_forest_model.feature_names_in_
        df_iso = df[iso_forest_features]
        
        anomaly_score = self.iso_forest_model.decision_function(df_iso)
        if anomaly_score < -0.1: # Threshold can be tuned
            all_alerts.append({
                "type": "Anomaly-Based Alert",
                "severity": "Medium",
                "description": "Anomalous Behavior Detected",
                "details": f"Anomaly score of {anomaly_score[0]:.2f}. Data: {data}"
            })
            
        # 3. Run through Signature Detection (Random Forest) - only for network data
        if metrics_json.get('type') == 'network_flow':
            # This requires more complex feature mapping to match CIC-IDS2017
            # For this example, we'll simulate it. A real implementation needs a
            # function to map our extracted features to the 40+ features used by the RF model.
            # prediction = self.rf_model.predict(df_rf)
            # predicted_label = self.label_encoder.inverse_transform(prediction)
            # if predicted_label!= 'BENIGN':
            #     all_alerts.append({... "description": f"Signature Detected: {predicted_label}"... })
            # pass # Placeholder for signature detection logic

         return all_alerts

if __name__ == '__main__':
    # Example Usage
    engine = DetectionEngine(
        iso_forest_path='isolation_forest_model.joblib',
        rf_path='random_forest_model.joblib',
        label_encoder_path='label_encoder.joblib'
    )
    
    # Example host metric data
    high_cpu_data = {
        "timestamp": time.time(), "type": "host_metrics",
        "data": {"cpu_usage_percent": 98.0}
    }
    
    # Example network metric data
    high_rate_data = {
        "timestamp": time.time(), "type": "network_flow",
        "data": {
            "flow_key": "1.2.3.4:1234-5.6.7.8:80", "flow_duration": 2.0, "packet_count": 3000, 
            "byte_count": 180000, "packet_rate": 1500.0, "byte_rate": 90000.0,
            "src_bytes": 180000, "dst_bytes": 0, "syn_flag_count": 3000,
            "fin_flag_count": 0, "rst_flag_count": 0, "ack_flag_count": 0
        }
    }
    
    alerts1 = engine.detect_threats(high_cpu_data)
    print("\nAlerts for High CPU Data:", json.dumps(alerts1, indent=2))
    alerts2 = engine.detect_threats(high_rate_data)
    print("\nAlerts for High Packet Rate Data:", json.dumps(alerts2, indent=2))