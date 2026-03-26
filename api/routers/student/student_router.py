"""
Student router for handling student profile management endpoints
Includes: /student/{student_id}/profile
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import logging

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.conversation_memory import conversation_memory

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/student",
    tags=["student"],
    responses={404: {"description": "Not found"}}
)

# Student Profile Management
@router.get("/{student_id}/profile")
async def get_student_profile(student_id: str):
    """Get student profile and analytics"""
    try:
        # Get profile from conversation memory
        profile = conversation_memory.student_profiles.get(student_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")
        
        # Get learning analytics
        analytics = await conversation_memory.get_learning_analytics(student_id)
        
        return {
            "profile": profile.model_dump(),
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{student_id}/profile")
async def update_student_profile(
    student_id: str,
    updates: Dict[str, Any]
):
    """Update student profile"""
    try:
        updated_profile = await conversation_memory.update_student_profile(
            student_id=student_id,
            updates=updates
        )
        
        return {
            "success": True,
            "profile": updated_profile.model_dump() if updated_profile else None
        }
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))