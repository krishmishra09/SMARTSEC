# app.py
import eventlet
eventlet.monkey_patch()
# Enable eventlet for async handling

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from detection_engine import DetectionEngine  # Import our detection engine

import time
from threading import Lock


# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key'   
socketio = SocketIO(app, async_mode='eventlet')

# Global variables to track network traffic rate
last_check_time = time.time()
bytes_sent_since_last = 0
bytes_received_since_last = 0 # Placeholder for received traffic
data_lock = Lock()

# Initialize detection engine (ML models)
try:
    detection_engine = DetectionEngine(
        iso_forest_path='isolation_forest_model.joblib',
        rf_path='random_forest_model.joblib',
        label_encoder_path='label_encoder.joblib'
    )
except FileNotFoundError:
    print("CRITICAL: Model files not found. Detection engine disabled.")
    detection_engine = None


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')


@app.route('/api/data', methods=['POST'])   
def receive_data():
    """API endpoint for agents to post their data."""
    # Use global variables for rate calculation
    global last_check_time, bytes_sent_since_last, bytes_received_since_last
    
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    data_type = data.get('type')

    # Handle system metrics and top processes
    if data_type == 'system_metrics':
        # Emit system data on a specific channel
        socketio.emit('system_metrics_update', data.get('metrics', {}))

    # Handle network data for alerts AND traffic rate calculation
    elif data_type == 'network_flow':
        # 1. Accumulate bytes for rate calculation
        with data_lock:
            # Assuming your network_agent sends packet length in a 'len' field
            packet_size = data.get('len', 0)
            bytes_sent_since_last += packet_size

        # 2. Check if it's time to calculate and emit the rate (e.g., every 1 second)
        current_time = time.time()
        if current_time - last_check_time >= 1.0:
            with data_lock:
                elapsed_time = current_time - last_check_time
                # Calculate rate in Bytes/sec
                sent_rate = bytes_sent_since_last / elapsed_time
                received_rate = 0 # You would implement received logic similarly

                # Emit the calculated rate on a new, specific channel for the graph
                socketio.emit('network_traffic_update', {
                    'sent': sent_rate,
                    'received': received_rate 
                })

                # Reset counters for the next interval
                bytes_sent_since_last = 0
                last_check_time = current_time

        # 3. Run threat detection on the packet data
        if detection_engine:
            # print(f"Running network data through detection engine...") # Optional debug
            alerts = detection_engine.detect_threats(data)
            if alerts:
                for alert in alerts:
                    socketio.emit('new_alert', alert)

    return jsonify({"status": "success"}), 200


# Handle client connections
@socketio.on('connect')
def handle_connect():
    print('✅ Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')


if __name__ == '__main__':
    print("🚀 Starting server at http://127.0.0.1:5000")
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
