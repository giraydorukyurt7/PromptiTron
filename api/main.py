"""
Main FastAPI application with modular structure
This is the refactored version of main_api.py following SOLID principles
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse
import logging
import sys
import os
import asyncio
from pathlib import Path

# Fix Windows console encoding
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import routers with relative imports
from .routers.chat import chat_router
from .routers.curriculum import curriculum_router
from .routers.content import content_router
from .routers.generation import generation_router
from .routers.student import student_router
from .routers.system import system_router
from .routers.search import search_router
from .routers.validation import validation_router
from .routers.crew import crew_router

# Import middleware
from .middleware.logging import log_requests

# Import core modules for initialization
from core.rag_system import rag_system
from core.curriculum_loader import CurriculumLoader

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Promptitron Unified AI System",
    description="""
    Comprehensive educational AI platform with RAG, agents, and personalization.
    
    ## Features
    - 🤖 Multi-agent AI system with specialized experts
    - 📚 Complete curriculum integration (TYT/AYT)
    - 🧠 RAG-powered knowledge retrieval
    - 💬 Conversational memory and context
    - 📊 Content analysis and generation
    - 🎯 Personalized study planning
    """,
    version="2.0.0",
    docs_url=None,
    redoc_url=None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.middleware("http")(log_requests)

# Mount static files if needed
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Docs",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@2.0.0/bundles/redoc.standalone.js",
    )

# Alternative documentation endpoints
@app.get("/docs-alt", include_in_schema=False)
async def custom_swagger_ui_html_alt():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Alternative Docs",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc-alt", include_in_schema=False)
async def redoc_html_alt():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Alternative ReDoc",
        redoc_js_url="https://unpkg.com/redoc@2.0.0/bundles/redoc.standalone.js",
    )

# Include all routers
app.include_router(chat_router.router, tags=["Chat"])
app.include_router(curriculum_router.router, tags=["Curriculum"])
app.include_router(content_router.router, tags=["Content Analysis"])
app.include_router(generation_router.router, tags=["Generation"])
app.include_router(student_router.router, tags=["Student"])
app.include_router(system_router.router, tags=["System"])
app.include_router(search_router.router, tags=["Search"])
app.include_router(validation_router.router, tags=["Validation"])
app.include_router(crew_router.router, tags=["Crew"])

# Background task for curriculum loading
async def load_curriculum_data():
    """Background task to load curriculum data into RAG system"""
    logger.info("Starting curriculum data loading in background...")
    try:
        await rag_system.load_curriculum_data(force_reload=True)
        logger.info("Unified curriculum data loaded successfully to RAG")
    except Exception as e:
        logger.error(f"Failed to load curriculum data: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize systems on startup"""
    logger.info("Starting Promptitron Unified System...")
    
    # Initialize curriculum loader
    global curriculum_loader
    curriculum_loader = CurriculumLoader()
    logger.info("Curriculum loader initialized")
    
    # Load curriculum data in background
    asyncio.create_task(load_curriculum_data())
    
    logger.info("System startup completed")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Promptitron Unified System...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )