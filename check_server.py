import subprocess
import sys
import os
import time
import socket
import webbrowser

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_server_running(port=8001):
    """Check if the server is running on the specified port."""
    return is_port_in_use(port)

def start_server():
    """Start the server using main.py."""
    print("Starting server...")
    
    # Check if we have the required packages installed
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("Required packages not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the server
    print("Starting Radha API server...")
    
    # Use subprocess.Popen to run the server in the background
    if os.name == 'nt':  # Windows
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:  # Unix/Linux/Mac
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    # Wait for the server to start
    max_attempts = 5
    attempts = 0
    while attempts < max_attempts:
        if check_server_running():
            print("Server started successfully!")
            return True
        print("Waiting for server to start...")
        attempts += 1
        time.sleep(2)
    
    print("Server failed to start in the expected time.")
    return False

def open_dashboard():
    """Open the dashboard in the default web browser."""
    url = "http://localhost:8001"
    print(f"Opening dashboard at {url}")
    webbrowser.open(url)

def main():
    """Main function to check and start the server if needed."""
    print("Checking if Radha API server is running...")
    
    if check_server_running():
        print("Server is already running!")
    else:
        print("Server is not running.")
        if start_server():
            print("Server started successfully!")
        else:
            print("Failed to start server. Please check for errors.")
            return
    
    # Open the dashboard
    open_dashboard()

if __name__ == "__main__":
    main()
