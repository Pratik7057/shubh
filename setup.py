#!/usr/bin/env python
"""
Radha API Setup Script
This script sets up the Radha API with MongoDB and prepares it for deployment
"""

import os
import sys
import subprocess
import platform
import time
import webbrowser

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60 + "\n")

def run_command(cmd):
    """Run a command and return True if successful"""
    try:
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False

def setup_environment():
    """Set up the Python environment"""
    print_header("Setting Up Python Environment")
    
    # Install requirements
    success = run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    if success:
        print("✅ Dependencies installed successfully")
    else:
        print("❌ Failed to install dependencies")
    
    return success

def check_mongodb():
    """Check MongoDB connection"""
    print_header("Checking MongoDB Connection")
    
    if "MONGODB_URI" not in os.environ:
        print("❌ MONGODB_URI environment variable not set")
        print("\nPlease set the MONGODB_URI environment variable:")
        if platform.system() == "Windows":
            print("$env:MONGODB_URI = 'mongodb+srv://username:password@cluster0.mongodb.net/radhaapi'")
        else:
            print("export MONGODB_URI='mongodb+srv://username:password@cluster0.mongodb.net/radhaapi'")
        return False
    
    # Run setup_mongo.py to test connection
    success = run_command(f"{sys.executable} setup_mongo.py")
    
    if success:
        print("✅ MongoDB connection successful")
    else:
        print("❌ Failed to connect to MongoDB")
        print("  - The application will use in-memory storage instead")
    
    return True  # Continue even if MongoDB fails

def run_server():
    """Run the server"""
    print_header("Starting Radha API Server")
    
    print("Starting server on http://localhost:8002")
    print("Press Ctrl+C to stop the server")
    
    # Open browser
    time.sleep(1)
    webbrowser.open("http://localhost:8002")
    
    # Run the server
    cmd = f"{sys.executable} main.py"
    try:
        subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error running server: {e}")

def main():
    """Main function"""
    print_header("Radha API Setup")
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed")
        return
    
    # Check MongoDB
    check_mongodb()
    
    # Ask to run server
    run_server_input = input("\nDo you want to start the server now? (y/n): ").strip().lower()
    if run_server_input == "y":
        run_server()
    
    print("\n✅ Setup complete")

if __name__ == "__main__":
    main()
