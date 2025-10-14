# core_python/process_monitor.py

# process_monitor.py

import psutil
import time
import os

# Make sure 'logs' folder exists
if not os.path.exists('logs'):
    os.makedirs('logs')


# Open log file
log_file = open('logs/process_log.txt', 'a')

print("Process monitoring started... (Press Ctrl+C to stop)")

try:
    while True:
        # Get all running processes
        processes = psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent'])

        log_file.write("---- Process Snapshot (one process monitor is complete again it shows after 10 sec----\n")

        for proc in processes:
            try:
                info = proc.info
                log_entry = (
                    f"PID: {info['pid']} | "
                    f"Name: {info['name']} | "
                    f"User: {info['username']} | "
                    f"CPU: {info['cpu_percent']}% | "
                    f"Memory: {info['memory_percent']:.2f}%\n"
                )

                # Print to console
                print(log_entry.strip())

                # Write to file
                log_file.write(log_entry)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Some processes may terminate or deny access during monitoring
                continue

        log_file.flush()#ensures that all data is written imediately

        # Wait for 10 seconds before next snapshot
        time.sleep(10)

except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")
    log_file.close()
