# import psutil
# import time
# import json
# import requests # To send data to the backend API

# class HostAgent:
#     def __init__(self, backend_url, collection_interval=5):
#         """
#         Initializes the Host Agent.
#         :param backend_url: The URL of the backend server's API endpoint.
#         :param collection_interval: The time in seconds between metric collections.
#         """
#         self.backend_url = backend_url
#         self.interval = collection_interval

#     def get_system_metrics(self):
#         """
#         Collects a snapshot of various system metrics.
#         """
#         # Using interval=1 for cpu_percent to get a non-blocking, meaningful reading.
#         cpu_usage = psutil.cpu_percent(interval=1)
#         load_avg = psutil.getloadavg()

#         memory_info = psutil.virtual_memory()
#         mem_percent = memory_info.percent
        
#         disk_io = psutil.disk_io_counters()
#         net_io = psutil.net_io_counters()

#         # Get top 5 processes by CPU usage
#         processes = []
#         for p in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), 
#                         key=lambda p: p.info['cpu_percent'], reverse=True)[:5]:
#             try:
#                 processes.append(p.info)
#             except (psutil.NoSuchProcess, psutil.AccessDenied):
#                 pass

#         metrics = {
#             "timestamp": time.time(),
#             "type": "system_metrics",
#             "data": {
#                 "cpu_usage_percent": cpu_usage,
#                 "cpu_load_avg_1m": load_avg,
#                 "memory_usage_percent": mem_percent,
#                 "disk_read_bytes": disk_io.read_bytes,
#                 "disk_write_bytes": disk_io.write_bytes,
#                 "net_bytes_sent": net_io.bytes_sent,
#                 "net_bytes_recv": net_io.bytes_recv,
#                 "top_processes": processes
#             }
#         }
#         return metrics

#     def send_data(self, data):
#         """
#         Sends collected data to the backend server.
#         For now, we will print it. In the final version, this will be an HTTP POST request.
#         """
#         try:
#             #In the final version, this will be uncommented
#             response = requests.post(self.backend_url, json=data)
#             response.raise_for_status() # Raise an exception for bad status codes
#             print(f"Successfully sent data. Server responded with: {response.status_code}")
            
#             # this line is to show the result on the terminal window
#             # print("--- Collected Host Metrics ---")
#             # print(json.dumps(data, indent=4))
#             # print("----------------------------\n")

#         except requests.exceptions.RequestException as e:
#             print(f"Error sending data to backend: {e}")

#     def run(self):
#         """
#         Runs the agent in a continuous loop.
#         """
#         print("Host Agent started. Press Ctrl+C to stop.")
#         while True:
#             try:
#                 metrics_data = self.get_system_metrics()
#                 self.send_data(metrics_data)
#                 time.sleep(self.interval)
#             except KeyboardInterrupt:
#                 print("Host Agent stopped.")
#                 break
#             except Exception as e:
#                 print(f"An error occurred in the agent loop: {e}")
#                 time.sleep(self.interval)

# if __name__ == '__main__':
#     # The URL will point to our Flask API endpoint later
#     BACKEND_API_URL = "http://127.0.0.1:5000/api/data" 
#     agent = HostAgent(backend_url=BACKEND_API_URL, collection_interval=5)
#     agent.run()

# host_agent.py (Corrected Version)
import psutil
import time
import json
import requests

class HostAgent:
    def __init__(self, backend_url, collection_interval=2): # Shortened interval for faster updates
        self.backend_url = backend_url
        self.interval = collection_interval

    def get_system_metrics(self):
        """
        Collects system metrics in the exact structure expected by the backend.
        """
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        load_avg_1m = psutil.getloadavg()[0]

        # Get top 5 processes by CPU usage
        processes = []
        # The cpu_percent call for processes needs a non-zero interval on the first run
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc.cpu_percent(interval=0.01) 
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by cpu_percent and take the top 15
        top_processes = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:15]

        # Build the payload with the correct type, keys, and structure
        metrics_payload = {
            "type": "system_metrics",          
            "metrics": {                        
                "cpu_usage": cpu_usage,         
                "memory_usage": memory_info.percent, 
                "cpu_load": load_avg_1m,        
                "top_processes": top_processes
            }
        }
        return metrics_payload

    def send_data(self, data):
        """Sends collected data to the backend server."""
        try:
            response = requests.post(self.backend_url, json=data)
            response.raise_for_status()
            # More informative print statement
            print(f"Data sent successfully (Type: {data.get('type')}).")
             # this line is to show the result on the terminal window
            # print("--- Collected Host Metrics ---")
            # print(json.dumps(data, indent=4))
            # print("----------------------------\n")

        except requests.exceptions.RequestException as e:
            print(f"Error sending host data to backend: {e}")

    def run(self):
        """Runs the agent in a continuous loop."""
        print("your Host Agent is started. Press Ctrl+C to stop.")
        while True:
            try:
                metrics_data = self.get_system_metrics()
                self.send_data(metrics_data)
                time.sleep(self.interval)
            except KeyboardInterrupt:
                print("\nStopping Host Agent...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(self.interval)
        print("Host Agent stopped.")

if __name__ == '__main__':
    BACKEND_API_URL = "http://127.0.0.1:5000/api/data"
    agent = HostAgent(backend_url=BACKEND_API_URL, collection_interval=2)
    agent.run()