# import scapy.all as scapy
# from collections import defaultdict
# import time
# import json
# import requests
# import threading

# class TrafficAnalyzer:
#     def __init__(self):
#         self.flow_stats = defaultdict(lambda: {
#             'packet_count': 0,
#             'byte_count': 0,
#             'start_time': 0,
#             'last_time': 0,
#             'src_bytes': 0,
#             'dst_bytes': 0,
#             'flags': defaultdict(int)
#         })

#     def analyze_packet(self, packet):
#         if not (packet.haslayer(scapy.IP) and packet.haslayer(scapy.TCP)):
#             return None

#         ip_layer = packet[scapy.IP]
#         tcp_layer = packet[scapy.TCP]

#         # Define flow key (sorted to handle both directions)
#         flow_key_part1 = (ip_layer.src, tcp_layer.sport)
#         flow_key_part2 = (ip_layer.dst, tcp_layer.dport)
#         flow_key = tuple(sorted((flow_key_part1, flow_key_part2)))

#         stats = self.flow_stats[flow_key]

#         # Update flow statistics
#         if stats['packet_count'] == 0:
#             stats['start_time'] = packet.time
#         stats['last_time'] = packet.time
#         stats['packet_count'] += 1
#         stats['byte_count'] += len(packet)

#         # Directional byte counts
#         if (ip_layer.src, tcp_layer.sport) == flow_key[0]:
#             stats['src_bytes'] += len(packet)
#         else:
#             stats['dst_bytes'] += len(packet)
        
#         # TCP Flags
#         for flag in tcp_layer.flags.flagrepr():
#             stats['flags'][flag] += 1
            
#         return self.extract_features(packet, stats, flow_key)

#     def extract_features(self, packet, stats, flow_key):
#         flow_duration = stats['last_time'] - stats['start_time']
#         if flow_duration == 0:
#             flow_duration = 0.000001 # Avoid division by zero

#         features = {
#             "flow_key": f"{flow_key}:{flow_key}-{flow_key}:{flow_key}",
#             "flow_duration": flow_duration,
#             "packet_count": stats['packet_count'],
#             "byte_count": stats['byte_count'],
#             "packet_rate": stats['packet_count'] / flow_duration,
#             "byte_rate": stats['byte_count'] / flow_duration,
#             "src_bytes": stats['src_bytes'],
#             "dst_bytes": stats['dst_bytes'],
#             "syn_flag_count": stats['flags'].get('S', 0),
#             "fin_flag_count": stats['flags'].get('F', 0),
#             "rst_flag_count": stats['flags'].get('R', 0),
#             "ack_flag_count": stats['flags'].get('A', 0),
#         }
#         return features

# class NetworkAgent:
#     def __init__(self, backend_url, interface=None):
#         self.backend_url = backend_url
#         self.interface = interface
#         self.analyzer = TrafficAnalyzer()
#         self.stop_sniffing = threading.Event()

#     def packet_callback(self, packet):
#         features = self.analyzer.analyze_packet(packet)
#         if features:
#             data_to_send = {
#                 "timestamp": time.time(),
#                 "type": "network_flow",
#                 "data": features
#             }
#             self.send_data(data_to_send)
    
#     def send_data(self, data):
#         try:
#             # In final version, this will be uncommentedclear
#             response = requests.post(self.backend_url, json=data)
#             response.raise_for_status()
#             print(f"Data sent successfully (Type: {data['type']}).")
            
#             # # For development, we print the JSON data
#             # print("--- Extracted Network Features ---")
#             # print(json.dumps(data, indent=4))
#             # print("--------------------------------\n")
#         except requests.exceptions.RequestException as e:
#             print(f"Error sending network data to backend: {e}")

#     def start(self):
#         print(f"Network Agent started sniffing on interface {self.interface or 'default'}. Press Ctrl+C to stop.")
#         try:
#             scapy.sniff(iface=self.interface, prn=self.packet_callback, store=False, stop_filter=lambda p: self.stop_sniffing.is_set())
#         except Exception as e:
#             print(f"An error occurred during sniffing: {e}")

#     def stop(self):
#         print("Stopping Network Agent...")
#         self.stop_sniffing.set()

# if __name__ == '__main__':
#     BACKEND_API_URL = "http://127.0.0.1:5000/api/data"
#     agent = NetworkAgent(backend_url=BACKEND_API_URL)
    
#     # Run sniffing in a separate thread to allow for graceful shutdown
#     sniff_thread = threading.Thread(target=agent.start)
#     sniff_thread.start()

#     try:
#         while sniff_thread.is_alive():
#             sniff_thread.join(1)
#     except KeyboardInterrupt:
#         agent.stop()
#         sniff_thread.join()
#         print("Network Agent stopped.")

import scapy.all as scapy
from collections import defaultdict
import time
import json
import requests
import threading

class TrafficAnalyzer:
    def __init__(self):
        self.flow_stats = defaultdict(lambda: {
            'packet_count': 0,
            'byte_count': 0,
            'start_time': 0,
            'last_time': 0,
            'src_bytes': 0,
            'dst_bytes': 0,
            'flags': defaultdict(int)
        })

    def analyze_packet(self, packet):
        if not (packet.haslayer(scapy.IP) and packet.haslayer(scapy.TCP)):
            return None

        ip_layer = packet[scapy.IP]
        # CHANGE 1: Correctly extract the TCP layer
        tcp_layer = packet[scapy.TCP]

        # Define flow key (sorted to handle both directions)
        flow_key_part1 = (ip_layer.src, tcp_layer.sport)
        flow_key_part2 = (ip_layer.dst, tcp_layer.dport)
        flow_key = tuple(sorted((flow_key_part1, flow_key_part2)))

        stats = self.flow_stats[flow_key]

        # Update flow statistics
        if stats['packet_count'] == 0:
            stats['start_time'] = packet.time
        stats['last_time'] = packet.time
        stats['packet_count'] += 1
        stats['byte_count'] += len(packet)

        # CHANGE 2: Correct the logic for directional byte counts
        if (ip_layer.src, tcp_layer.sport) == flow_key[0]:
            stats['src_bytes'] += len(packet)
        else:
            stats['dst_bytes'] += len(packet)
        
        # TCP Flags
        for flag in tcp_layer.flags.flagrepr():
            stats['flags'][flag] += 1
            
        return self.extract_features(packet, stats, flow_key)

    def extract_features(self, packet, stats, flow_key):
        flow_duration = stats['last_time'] - stats['start_time']
        if flow_duration == 0:
            flow_duration = 1e-6 # Avoid division by zero

        features = {
            # CHANGE 3: Make the flow_key readable
            "flow_key": f"{flow_key[0][0]}:{flow_key[0][1]}-{flow_key[1][0]}:{flow_key[1][1]}",
            
            # CHANGE 4: Add the packet length ('len') for the server to use
            "len": len(packet),
            
            "flow_duration": flow_duration,
            "packet_count": stats['packet_count'],
            "byte_count": stats['byte_count'],
            "packet_rate": stats['packet_count'] / flow_duration,
            "byte_rate": stats['byte_count'] / flow_duration,
            "src_bytes": stats['src_bytes'],
            "dst_bytes": stats['dst_bytes'],
            "syn_flag_count": stats['flags'].get('S', 0),
            "fin_flag_count": stats['flags'].get('F', 0),
            "rst_flag_count": stats['flags'].get('R', 0),
            "ack_flag_count": stats['flags'].get('A', 0),
        }
        return features

class NetworkAgent:
    def __init__(self, backend_url, interface=None):
        self.backend_url = backend_url
        self.interface = interface
        self.analyzer = TrafficAnalyzer()
        self.stop_sniffing = threading.Event()

    def packet_callback(self, packet):
        features = self.analyzer.analyze_packet(packet)
        if features:
            # CHANGE 5: Send the data in the correct flat format that app.py expects
            data_to_send = {
                "timestamp": time.time(),
                "type": "network_flow",
                **features
            }
            self.send_data(data_to_send)
    
    def send_data(self, data):
        try:
            response = requests.post(self.backend_url, json=data)
            response.raise_for_status()
            print(f"Data sent successfully (Type: {data['type']}).")
            # # For development, we print the JSON data
            # print("--- Extracted Network Features ---")
            # print(json.dumps(data, indent=4))
#           # print("--------------------------------\n")
        except requests.exceptions.RequestException as e:
            print(f"Error sending network data to backend: {e}")

    def start(self):
        print(f"Network Agent started sniffing on interface {self.interface or 'default'}. Press Ctrl+C to stop.")
        try:
            scapy.sniff(iface=self.interface, prn=self.packet_callback, store=False, stop_filter=lambda p: self.stop_sniffing.is_set())
        except Exception as e:
            print(f"An error occurred during sniffing: {e}")

    def stop(self):
        print("\nStopping Network Agent...")
        self.stop_sniffing.set()

if __name__ == '__main__':
    BACKEND_API_URL = "http://127.0.0.1:5000/api/data"
    agent = NetworkAgent(backend_url=BACKEND_API_URL)
    
    # Run sniffing in a separate thread to allow for graceful shutdown
    sniff_thread = threading.Thread(target=agent.start)
    sniff_thread.start()

    try:
        while sniff_thread.is_alive():
            sniff_thread.join(1)
    except KeyboardInterrupt:
        agent.stop()
        sniff_thread.join()
        print("Network Agent stopped.")
