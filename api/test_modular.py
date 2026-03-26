"""Test modular API structure without initializing systems"""
import sys
import os

# Set up paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test model imports
    from models.request_models import ChatRequest
    print("OK: Request models import successful")
    
    from models.response_models import ChatResponse  
    print("OK: Response models import successful")
    
    # Test utils imports
    from utils.dependencies import get_session_id
    print("OK: Utils import successful")
    
    # Test middleware
    from middleware.logging import log_requests
    print("OK: Middleware import successful")
    
    # Test basic FastAPI structure without core systems
    from fastapi import FastAPI
    app = FastAPI(title="Test API")
    print("OK: FastAPI app creation successful")
    
    print("\nAll modular components import successfully!")
    print("The modular API structure is working correctly.")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()