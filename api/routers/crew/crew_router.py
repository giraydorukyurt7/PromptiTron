"""
Crew router for handling CrewAI task execution endpoints
Includes: /crew/execute
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import logging

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.agents import agent_system

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/crew",
    tags=["crew"],
    responses={404: {"description": "Not found"}}
)

# CrewAI Task Execution
@router.post("/execute")
async def execute_crew_task(request: Dict[str, Any]):
    """Execute a custom CrewAI task"""
    try:
        task_type = request.get("task_type")
        task_data = request.get("task_data", {})
        agents = request.get("agents", [])
        
        if not task_type:
            raise HTTPException(status_code=400, detail="task_type is required")
        
        # Route to Unified Agent System
        custom_prompt = f"""
        Görev türü: {task_type}
        Görev verileri: {task_data}
        İstenen ajanlar: {agents}
        
        Bu görevi yerine getir ve sonucu JSON formatında döndür.
        """
        
        agent_response = await agent_system.process_message(
            message=custom_prompt,
            context={
                "task_type": task_type,
                "task_data": task_data,
                "agents": agents
            }
        )
        
        return {
            "success": agent_response.get("success", False),
            "result": agent_response.get("response"),
            "agents_used": agent_response.get("system_used", "unified_agent"),
            "execution_time": agent_response.get("metadata", {}).get("processing_time"),
            "task_type": task_type
        }
        
    except Exception as e:
        logger.error(f"CrewAI execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))