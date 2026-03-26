"""
Request logging middleware
"""

from fastapi import Request
import time
import json
import logging
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

async def log_requests(request: Request, call_next):
    """Log all HTTP requests to console"""
    start_time = time.time()
    
    # Log request
    console.print(f"\n[dim]-> {request.method} {request.url.path}[/dim]")
    
    # Log request body for POST/PUT
    if request.method in ["POST", "PUT"]:
        try:
            body = await request.body()
            if body:
                try:
                    json_body = json.loads(body)
                    console.print(f"[dim]  Request Body: {json.dumps(json_body, indent=2)[:200]}...[/dim]")
                except:
                    console.print(f"[dim]  Request Body: {body[:200]}...[/dim]")
                # Reset body for processing
                request._body = body
        except:
            pass
    
    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        status_code = response.status_code
        if 200 <= status_code < 300:
            console.print(f"[green][OK] {request.method} {request.url.path} - {status_code} ({process_time:.2f}s)[/green]")
        elif 400 <= status_code < 500:
            console.print(f"[yellow][!] {request.method} {request.url.path} - {status_code} ({process_time:.2f}s)[/yellow]")
        else:
            console.print(f"[red][ERR] {request.method} {request.url.path} - {status_code} ({process_time:.2f}s)[/red]")
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        console.print(f"[red][X] {request.method} {request.url.path} - ERROR: {str(e)} ({process_time:.2f}s)[/red]")
        raise