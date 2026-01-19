
import os
import subprocess
import time

def kill_process(name):
    print(f"Finding and killing {name}...")
    try:
        # Use pgrep to find PID
        pids = subprocess.check_output(["pgrep", "-f", name]).decode().strip().split('\n')
        for pid in pids:
            if pid:
                print(f"Killing {pid} ({name})")
                subprocess.run(["kill", "-9", pid])
    except subprocess.CalledProcessError:
        print(f"No running process found for {name}")

def main():
    print("Stopping application...")
    kill_process("uvicorn")
    kill_process("next")
    kill_process("start_app.sh")
    
    print("Waiting for ports to clear...")
    time.sleep(3)
    
    print("Starting application...")
    # Run start_app.sh in background
    subprocess.Popen(["bash", "start_app.sh"])
    print("Application started!")

if __name__ == "__main__":
    main()
