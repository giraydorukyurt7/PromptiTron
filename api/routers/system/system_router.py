"""
System router for handling system-related endpoints
Includes: /health, /, /diagnostics, /system/collections, /stats, /memory/{session_id}
"""

from fastapi import APIRouter, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import platform
import sys
import os

# Import models
from ...models.response_models import HealthResponse

# Import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.conversation_memory import conversation_memory
from core.rag_system import rag_system
from config import settings

logger = logging.getLogger(__name__)

# Global flags for curriculum loading status
curriculum_loading = False
curriculum_loaded = False

router = APIRouter(
    tags=["system"],
    responses={404: {"description": "Not found"}}
)

# Root endpoint
@router.get("/")
async def root():
    """Root endpoint - system information"""
    return {
        "name": "Promptitron Unified AI System",
        "version": "2.0.0",
        "status": "running",
        "description": "YKS için kapsamlı AI eğitim sistemi",
        "documentation": {
            "swagger_ui": "/docs",
            "swagger_alt": "/docs-alt", 
            "redoc": "/redoc",
            "redoc_alt": "/redoc-alt",
            "openapi_spec": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "search": "/search",
            "generate_questions": "/generate/questions",
            "study_plan": "/generate/study-plan",
            "upload_document": "/upload/document",
            "analyze_document": "/document/analyze"
        }
    }

# Custom Swagger UI with fallback
@router.get("/docs-alt", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with local fallback if CDN fails"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Promptitron Unified AI System - Interactive API docs",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# Enhanced ReDoc endpoint
@router.get("/redoc-alt", include_in_schema=False)
async def custom_redoc_html():
    """Custom ReDoc with specific CDN version"""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Promptitron Unified AI System - ReDoc Documentation",
        redoc_js_url="https://unpkg.com/redoc@2.0.0/bundles/redoc.standalone.js",
    )

# API Diagnostics endpoint
@router.get("/diagnostics", include_in_schema=False)
async def api_diagnostics():
    """API diagnostics and troubleshooting information"""
    return {
        "api_info": {
            "title": "Promptitron Unified AI System",
            "version": "2.0.0",
            "docs_url": "/docs",
            "redoc_url": "/redoc",  
            "openapi_url": "/openapi.json"
        },
        "system_info": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "fastapi_version": "0.115.6"  # Current version
        },
        "documentation_urls": {
            "primary_swagger": "/docs",
            "alternative_swagger": "/docs-alt",  
            "primary_redoc": "/redoc",
            "alternative_redoc": "/redoc-alt",
            "openapi_spec": "/openapi.json"
        },
        "troubleshooting": {
            "swagger_not_loading": "Try /docs-alt for alternative CDN",
            "javascript_errors": "Check browser console and network tab",
            "cdn_blocked": "Use /redoc as fallback documentation",
            "cors_issues": "API allows all origins for development"
        }
    }

# Health Check
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Simple health check - just return server status
        services = {
            "api_server": "healthy",
            "curriculum_loading": "loading" if curriculum_loading else "idle",
            "curriculum_loaded": "loaded" if curriculum_loaded else "not_loaded"
        }
        
        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            timestamp=datetime.now().isoformat(),
            services=services
        )
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# System Collections Info
@router.get("/system/collections")
async def get_collections_info():
    """Get RAG collections information and sync status"""
    try:
        collections_info = {}
        
        # Get collection counts by manually checking
        collection_names = ["curriculum", "conversations", "documents", "questions"]
        
        for coll_name in collection_names:
            try:
                collection = rag_system._get_or_create_collection(coll_name)
                count = collection.count()
                collections_info[coll_name] = count
            except Exception as e:
                collections_info[coll_name] = f"Error: {e}"
        
        # Get curriculum loader info for comparison
        from core.unified_curriculum import unified_curriculum
        if not unified_curriculum.loader.curriculum_data:
            unified_curriculum.loader.load_all_curriculum()
            
        curriculum_topics = len(unified_curriculum.loader.flat_topics)
        
        return {
            "success": True,
            "collections": collections_info,
            "curriculum_loader_topics": curriculum_topics,
            "sync_status": {
                "rag_curriculum_docs": collections_info.get("curriculum", 0),
                "curriculum_loader_topics": curriculum_topics,
                "difference": curriculum_topics - collections_info.get("curriculum", 0),
                "synced": curriculum_topics == collections_info.get("curriculum", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting collections info: {str(e)}")
        return {"success": False, "error": str(e)}

# System Statistics
@router.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        stats = {
            "total_conversations": len(conversation_memory.conversations),
            "total_students": len(conversation_memory.student_profiles),
            "total_summaries": sum(len(summaries) for summaries in conversation_memory.summaries.values()),
            "system_health": "healthy",
            "uptime": "running",
            "version": settings.APP_VERSION
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Memory Management
@router.get("/memory/{session_id}")
async def get_conversation_memory(session_id: str):
    """Get conversation memory for a session"""
    try:
        memory_data = await conversation_memory.get_conversation_history(
            session_id=session_id,
            limit=50
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": memory_data,
            "message_count": len(memory_data)
        }
        
    except Exception as e:
        logger.error(f"Memory retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/memory/{session_id}/clear")
async def clear_conversation_memory(session_id: str):
    """Clear conversation memory for a session"""
    try:
        await conversation_memory.clear_conversation(session_id)
        
        return {
            "success": True,
            "message": f"Conversation memory cleared for session {session_id}"
        }
        
    except Exception as e:
        logger.error(f"Memory clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))