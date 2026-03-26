#!/usr/bin/env python3
"""
Promptitron System Monitor
Provides health checks and system monitoring for all services
"""

import asyncio
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

import uvicorn
import requests
import psutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from rich.console import Console

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Promptitron System Monitor",
    description="Health monitoring and system status for Promptitron services",
    version="1.0.0"
)

class SystemMonitor:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "http://localhost:8000")
        self.chroma_url = os.getenv("CHROMA_URL", "http://localhost:8001")
        self.start_time = datetime.now()
        
    def get_system_stats(self):
        """Get system resource statistics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def check_api_health(self):
        """Check main API health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None
            }
    
    async def check_chroma_health(self):
        """Check ChromaDB health"""
        try:
            response = requests.get(f"{self.chroma_url}/api/v1/heartbeat", timeout=10)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "response_time_ms": None
            }

monitor = SystemMonitor()

@app.get("/health")
async def health_check():
    """Overall system health check"""
    try:
        api_health = await monitor.check_api_health()
        chroma_health = await monitor.check_chroma_health()
        system_stats = monitor.get_system_stats()
        
        overall_status = "healthy"
        if api_health["status"] != "healthy" or chroma_health["status"] != "healthy":
            overall_status = "degraded"
        
        if system_stats["cpu_percent"] > 90 or system_stats["memory_percent"] > 90:
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": api_health,
                "chroma": chroma_health
            },
            "system": system_stats
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/services/api/health")
async def api_health():
    """API service health"""
    return await monitor.check_api_health()

@app.get("/services/chroma/health") 
async def chroma_health():
    """ChromaDB service health"""
    return await monitor.check_chroma_health()

@app.get("/system/stats")
async def system_stats():
    """System resource statistics"""
    return monitor.get_system_stats()

@app.get("/system/logs")
async def get_recent_logs():
    """Get recent log entries"""
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {"logs": [], "message": "No logs directory found"}
        
        log_files = list(logs_dir.glob("*.log"))
        if not log_files:
            return {"logs": [], "message": "No log files found"}
        
        # Get most recent log file
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        
        # Read last 50 lines
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-50:] if len(lines) > 50 else lines
        
        return {
            "logs": [line.strip() for line in recent_lines],
            "log_file": latest_log.name,
            "total_lines": len(lines)
        }
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return {"error": str(e), "logs": []}

@app.get("/")
async def root():
    """Monitor service info"""
    return {
        "service": "Promptitron System Monitor",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_health": "/services/api/health", 
            "chroma_health": "/services/chroma/health",
            "system_stats": "/system/stats",
            "logs": "/system/logs"
        }
    }

async def main():
    """Start the monitor service"""
    console.print("[cyan]🔍 Starting Promptitron System Monitor[/cyan]")
    
    port = int(os.getenv("MONITOR_PORT", 8002))
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    console.print(f"[green]✅ Monitor service running on port {port}[/green]")
    console.print(f"[dim]📊 Health check: http://localhost:{port}/health[/dim]")
    
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())