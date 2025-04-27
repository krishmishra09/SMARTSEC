#system_monitor.py
# system_monitor.py

import psutil
import time
import os

# Make sure 'logs' folder exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Open a log file to write
log_file = open('logs/system_log.txt', 'a')

print("System monitoring started... (Press Ctrl+C to stop)")

try:
    while True:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Format the log entry
        log_entry = (
            f"CPU Usage: {cpu_percent}% | "
            f"Memory Usage: {memory.percent}% | "
            f"Disk Usage: {disk.percent}%\n"
        )
        
        # Print to console
        print(log_entry.strip())

        # Write to log file
        log_file.write(log_entry)
        log_file.flush()

        # Wait 5 seconds before next reading
        time.sleep(5)

except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")
    log_file.close()
