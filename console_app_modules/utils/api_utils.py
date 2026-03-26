import requests
import time
import json
from .logging_utils import LoggingUtils

# API base URL
API_BASE_URL = "http://localhost:8000"

class APIClient(LoggingUtils):
    async def call_api(self, endpoint: str, method: str = "POST", data: dict = None) -> dict:
        """Make API calls to the FastAPI backend with logging"""
        import time
        start_time = time.time()
        
        try:
            url = f"{API_BASE_URL}{endpoint}"
            
            # Log request
            if hasattr(self, 'console'):
                self.console.print(f"\n[dim]-> {method} {url}[/dim]")
                if data:
                    self.console.print(f"[dim]  Request Data: {json.dumps(data, indent=2)}[/dim]")
            
            if method.upper() == "GET":
                response = requests.get(url, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            # Log response
            self.log_http_request(method, url, response.status_code, response_time)
            
            if response.status_code == 200:
                result = response.json()
                if hasattr(self, 'console'):
                    self.console.print(f"[dim]  Response: {json.dumps(result, indent=2)[:200]}...[/dim]")
                return result
            else:
                error_text = response.text
                self.log_http_request(method, url, response.status_code, response_time, error_text)
                return {"error": f"API call failed: {response.status_code}", "details": error_text}
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_http_request(method, url, 0, response_time, str(e))
            return {"error": str(e)}