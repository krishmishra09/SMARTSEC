# network_monitor.py
#this file tracks total bandwidth usage not the  indivisual active connections and monitors 
# total file sent or recieved and packets sent or recieved 

# it detects the sudden spikes or drops in usage

import psutil
import time
import os

# Make sure 'logs' folder exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Open a log file to write
log_file = open('logs/network_log.txt', 'a')

print("Network monitoring started... (Press Ctrl+C to stop)")

try:
    while True:
        # Get network IO statistics
        net_io = psutil.net_io_counters()

        # Format the log entry
        log_entry = (
            f"Bytes Sent: {net_io.bytes_sent} | "
            f"Bytes Received: {net_io.bytes_recv} | "
            f"Packets Sent: {net_io.packets_sent} | "
            f"Packets Received: {net_io.packets_recv}\n"
        )

        # Print to console
        #network load over time
        print(log_entry.strip())

        # Write to log file
        log_file.write(log_entry)
        log_file.flush()

        # Wait for 5 seconds before next snapshot
        time.sleep(5)

except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")
    log_file.close()
