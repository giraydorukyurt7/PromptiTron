"""
Convenience script to run the Promptitron Unified System
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import google.generativeai
        import langchain
        import chromadb
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if not env_path.exists():
        print("[WARNING] .env file not found!")
        print("Please copy .env.example to .env and configure your API keys")
        
        # Ask if user wants to create .env from example
        response = input("Create .env file from .env.example? (y/n): ")
        if response.lower() == 'y':
            example_path = Path(".env.example")
            if example_path.exists():
                import shutil
                shutil.copy(example_path, env_path)
                print("[SUCCESS] Created .env file from .env.example")
                print("Please edit .env file and add your Google API key")
                return False
            else:
                print("[ERROR] .env.example not found")
                return False
        return False
    return True

def run_tests():
    """Run system tests"""
    print("[TEST] Running system tests...")
    result = subprocess.run([sys.executable, "test_system.py"], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_server(host="0.0.0.0", port=8000, reload=True):
    """Run the FastAPI server"""
    print(f"[SERVER] Starting Promptitron API Server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   Docs: http://{host}:{port}/docs")
    print()
    
    # Start the API server
    os.system(f"python api/main_api.py")

def run_console():
    """Run the console application"""
    print(f"[CONSOLE] Starting Promptitron Console Application...")
    print()
    
    # Start the console app
    os.system(f"python main.py")

def main():
    parser = argparse.ArgumentParser(description="Run Promptitron Unified System")
    parser.add_argument("--mode", choices=["server", "console"], default="console", 
                       help="Run mode: server (API) or console (Interactive)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (server mode)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (server mode)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload (server mode)")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    parser.add_argument("--check", action="store_true", help="Check requirements only")
    
    args = parser.parse_args()
    
    print("PROMPTITRON UNIFIED AI SYSTEM")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    if args.check:
        print("[SUCCESS] All requirements satisfied")
        sys.exit(0)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    # Run tests if requested
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Run in selected mode
    try:
        if args.mode == "server":
            run_server(
                host=args.host,
                port=args.port,
                reload=not args.no_reload
            )
        else:  # console mode
            run_console()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down gracefully...")
    except Exception as e:
        print(f"[ERROR] Error starting {args.mode}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()