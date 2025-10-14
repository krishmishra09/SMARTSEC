import scapy.all as scapy
from collections import defaultdict
import time
import csv
import os
import threading

# --- This is the same traffic analyzer from before ---
class TrafficAnalyzer:
    def __init__(self):
        self.flow_stats = defaultdict(lambda: {
            'packet_count': 0, 'byte_count': 0, 'start_time': 0,
            'last_time': 0, 'src_bytes': 0, 'dst_bytes': 0,
            'flags': defaultdict(int)
        })

    def analyze_packet(self, packet):
        if not (packet.haslayer(scapy.IP) and packet.haslayer(scapy.TCP)):
            return None

        ip_layer = packet[scapy.IP]
        tcp_layer = packet[scapy.TCP]

        flow_key_part1 = (ip_layer.src, tcp_layer.sport)
        flow_key_part2 = (ip_layer.dst, tcp_layer.dport)
        flow_key = tuple(sorted((flow_key_part1, flow_key_part2)))
        
        stats = self.flow_stats[flow_key]

        if stats['packet_count'] == 0:
            stats['start_time'] = packet.time
        stats['last_time'] = packet.time
        stats['packet_count'] += 1
        stats['byte_count'] += len(packet)

        if (ip_layer.src, tcp_layer.sport) == flow_key_part1:
            stats['src_bytes'] += len(packet)
        else:
            stats['dst_bytes'] += len(packet)
            
        for flag in tcp_layer.flags.flagrepr():
            stats['flags'][flag] += 1
            
        return self.extract_features(stats)

    def extract_features(self, stats):
        flow_duration = stats['last_time'] - stats['start_time']
        if flow_duration == 0:
            flow_duration = 0.000001

        features = {
            "flow_duration": flow_duration,
            "packet_count": stats['packet_count'],
            "byte_count": stats['byte_count'],
            "packet_rate": stats['packet_count'] / flow_duration,
            "byte_rate": stats['byte_count'] / flow_duration,
            "src_bytes": stats['src_bytes'],
            "dst_bytes": stats['dst_bytes'],
        }
        return features

# --- This new class handles writing the data to a CSV file ---
class DataCollectorAgent:
    def __init__(self, output_file, interface=None):
        self.output_file = output_file
        self.interface = interface
        self.analyzer = TrafficAnalyzer()
        self.stop_sniffing = threading.Event()
        self.written_flows = set() # Keep track of flows we've already written

        # --- NEW: Setup the CSV file and writer ---
        file_exists = os.path.isfile(output_file)
        self.csv_file = open(output_file, 'a', newline='')
        
        # These are the headers for our CSV file
        self.fieldnames = [
            'flow_duration', 'packet_count', 'byte_count', 
            'packet_rate', 'byte_rate', 'src_bytes', 'dst_bytes'
        ]
        
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
        if not file_exists:
            self.writer.writeheader() # Write header only if file is new
        # --- END NEW ---

    def packet_callback(self, packet):
        features = self.analyzer.analyze_packet(packet)
        if features:
            # --- NEW: Write features to the CSV file instead of printing ---
            self.writer.writerow(features)
            # --- END NEW ---
    
    def start(self):
        print(f"Starting data collection on interface {self.interface or 'default'}.")
        print(f"Saving data to '{self.output_file}'. Press Ctrl+C to stop.")
        try:
            scapy.sniff(iface=self.interface, prn=self.packet_callback, store=False, stop_filter=lambda p: self.stop_sniffing.is_set())
        except Exception as e:
            print(f"An error occurred during sniffing: {e}")
        finally:
            self.stop()

    def stop(self):
        if not self.stop_sniffing.is_set():
            print("\nStopping data collection and closing file...")
            self.stop_sniffing.set()
            self.csv_file.close()
            print("File closed. Collection stopped.")

if __name__ == '__main__':
    OUTPUT_CSV_FILE = "normal_network_features.csv"
    agent = DataCollectorAgent(output_file=OUTPUT_CSV_FILE)
    
    agent_thread = threading.Thread(target=agent.start)
    agent_thread.start()

    try:
        while agent_thread.is_alive():
            agent_thread.join(1)
    except KeyboardInterrupt:
        agent.stop()
        agent_thread.join()
