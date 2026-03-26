#!/usr/bin/env python3
"""
Promptitron Unified System - Console-Based Main Entry Point
Konsol tabanlı AI Assistant uygulaması
"""

import sys
import asyncio
import logging
from pathlib import Path
import threading
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import system modules
try:
    import uvicorn
    from console_app import ConsoleManager
    from api.main import app as fastapi_app
    from config import settings
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.panel import Panel
except ImportError as e:
    print(f"Critical import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging with Windows console fix
import os
import sys

# Fix Windows console encoding
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

console = Console(force_terminal=True, width=120, color_system="truecolor" if not sys.platform.startswith('win') else "windows")
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

def run_api_server():
    """Run the FastAPI server in a separate thread"""
    try:
        console.print("[blue]Starting API server on port 8000...[/blue]")
        
        # Custom uvicorn logging config
        log_config = uvicorn.config.LOGGING_CONFIG
        log_config["formatters"]["default"]["fmt"] = "%(levelprefix)s %(message)s"
        log_config["formatters"]["access"]["fmt"] = '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
        
        uvicorn.run(
            fastapi_app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            access_log=False,  # We handle logging in middleware
            log_config=log_config
        )
    except Exception as e:
        console.print(f"[red]API server error: {e}[/red]")
        logger.error(f"API server error: {e}")

def wait_for_api_server(max_retries=60, delay=2):
    """Wait for API server to be ready"""
    import requests
    
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                return True
        except Exception as e:
            if i % 10 == 0:  # Print progress every 20 seconds
                console.print(f"[yellow]Still waiting for server... (attempt {i+1}/{max_retries})[/yellow]")
        
        if i < max_retries - 1:
            time.sleep(delay)
    
    return False

def main():
    """Main entry point"""
    try:
        # Print banner
        console.print(Panel.fit(
            "[bold cyan]PROMPTITRON UNIFIED SYSTEM[/bold cyan]\n"
            "Console-Based AI Educational Assistant\n"
            f"Version: {settings.APP_VERSION}",
            border_style="cyan"
        ))
        
        # Start API server in background thread
        api_thread = threading.Thread(target=run_api_server, daemon=True)
        api_thread.start()
        
        # Wait for API server to start
        console.print("\n[yellow]Waiting for API server to start...[/yellow]")
        
        if wait_for_api_server():
            console.print("[green]✓ API server is ready![/green]")
            console.print("[green]✓ All systems initialized successfully![/green]\n")
            
            # Start console interface
            manager = ConsoleManager(console)
            asyncio.run(manager.run())
        else:
            console.print("[red]✗ API server failed to start[/red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        logger.exception("Unhandled exception")


if __name__ == "__main__":
    # Set event loop policy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    main()