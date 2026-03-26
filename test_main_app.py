"""Test script for main application with timeout"""
import subprocess
import sys
import time
import threading

def run_app():
    """Run the main app with input simulation"""
    # Create input for the app (0 to exit)
    proc = subprocess.Popen(
        [r".\.venv\Scripts\python.exe", "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for app to start
    time.sleep(5)
    
    # Send exit command
    proc.stdin.write("0\n")
    proc.stdin.write("y\n")  # Confirm exit
    proc.stdin.flush()
    
    # Wait for completion
    stdout, stderr = proc.communicate(timeout=10)
    
    print("STDOUT:")
    print(stdout)
    
    if stderr:
        print("\nSTDERR:")
        print(stderr)
    
    return proc.returncode

if __name__ == "__main__":
    try:
        exit_code = run_app()
        print(f"\nApp exited with code: {exit_code}")
        
        if exit_code == 0:
            print("✓ Application ran successfully!")
        else:
            print("✗ Application failed!")
            
    except subprocess.TimeoutExpired:
        print("✗ Application timed out")
    except Exception as e:
        print(f"✗ Error: {e}")