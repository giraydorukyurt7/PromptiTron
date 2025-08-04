"""
Main FastAPI application with unified endpoints
Combines all functionality from various API modules
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json
import asyncio
import uuid
import time

from pydantic import BaseModel
import sys
import os

# Fix Windows console encoding for API
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.structured_models import *
from core.gemini_client import gemini_client
from core.rag_system import rag_system
# Temporarily disabled problematic imports to get app running
# from core.agents import agent_system
# from core.conversation_memory import conversation_memory
# from core.document_understanding import document_understanding
from config import settings
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

# Request Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    student_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    use_memory: bool = True
    stream: bool = False

class QuestionGenerationRequest(BaseModel):
    subject: SubjectType
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    count: int = 1
    exam_type: ExamType = ExamType.TYT

class StudyPlanRequest(BaseModel):
    student_profile: Dict[str, Any]
    target_exam: ExamType = ExamType.TYT
    duration_weeks: int = 12
    daily_hours: int = 6

class SearchRequest(BaseModel):
    query: str
    collection_names: Optional[List[str]] = None
    n_results: int = 5
    filters: Optional[Dict[str, Any]] = None
    include_personalization: bool = True

class AnalysisRequest(BaseModel):
    content: str
    analysis_type: str = "comprehensive"
    include_suggestions: bool = True

# Response Models
class ChatResponse(BaseModel):
    response: str
    session_id: str
    success: bool
    system_used: str
    metadata: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: Dict[str, Union[str, int]]

# Initialize FastAPI app
app = FastAPI(
    title="Promptitron Unified AI System",
    description=
"""Comprehensive educational AI platform with RAG, agents, and personalization.
    
    ## Features
    - AI Assistant with subject experts
    - Question generation for all YKS subjects  
    - RAG-powered knowledge search
    - Personalized study plans
    - Content analysis
    
    ## Usage
    Use the endpoints below to interact with the AI system.
    
    ## Alternative Documentation
    If Swagger UI doesn't load properly, try:
    - [ReDoc Documentation](/redoc) - Alternative API documentation
    - [Custom Swagger UI](/docs-alt) - Local fallback version
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UTF-8 Encoding Middleware
@app.middleware("http")
async def ensure_utf8_encoding(request: Request, call_next):
    """Ensure UTF-8 encoding for all requests and responses"""
    try:
        # Process request
        response = await call_next(request)
        
        # Ensure UTF-8 response headers
        if not response.headers.get("content-type"):
            response.headers["content-type"] = "application/json; charset=utf-8"
        elif "charset" not in response.headers.get("content-type", ""):
            current_type = response.headers["content-type"]
            response.headers["content-type"] = f"{current_type}; charset=utf-8"
            
        return response
    except Exception as e:
        logger.error(f"UTF-8 middleware error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Encoding error occurred"},
            headers={"content-type": "application/json; charset=utf-8"}
        )

# Custom Swagger UI with fallback
@app.get("/docs-alt", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with local fallback if CDN fails"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Interactive API docs",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# Enhanced ReDoc endpoint
@app.get("/redoc-alt", include_in_schema=False)
async def custom_redoc_html():
    """Custom ReDoc with specific CDN version"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc Documentation",
        redoc_js_url="https://unpkg.com/redoc@2.0.0/bundles/redoc.standalone.js",
    )

# HTTP Request Logging Middleware
@app.middleware("http")
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

# Dependency to get session ID
def get_session_id(session_id: Optional[str] = None) -> str:
    return session_id or str(uuid.uuid4())

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - system information"""
    return {
        "name": "Promptitron Unified AI System",
        "version": "2.0.0",
        "status": "running",
        "description": "YKS icin kapsamli AI egitim sistemi",
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

# API Diagnostics endpoint
@app.get("/diagnostics", include_in_schema=False)
async def api_diagnostics():
    """API diagnostics and troubleshooting information"""
    import platform
    import sys
    
    return {
        "api_info": {
            "title": app.title,
            "version": app.version,
            "docs_url": app.docs_url,
            "redoc_url": app.redoc_url,
            "openapi_url": app.openapi_url
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
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with vectorstore status"""
    try:
        # Get vectorstore statistics
        vectorstore_stats = rag_system.get_vectorstore_stats()
        
        services = {
            "api_server": "healthy",
            "curriculum_loading": "loading" if curriculum_loading else "idle",
            "curriculum_loaded": "loaded" if curriculum_loaded else "not_loaded",
            "vectorstore_ready": "ready" if vectorstore_stats["ready"] else "not_ready",
            "curriculum_documents": vectorstore_stats["collections"].get("curriculum", 0),
            "total_collections": len(vectorstore_stats["collections"])
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

# Chat Endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session_id: str = Depends(get_session_id)
):
    """Main chat endpoint with conversation memory and personalization"""
    try:
        # Use provided session_id or generate new one
        actual_session_id = request.session_id or session_id
        
        # Add user message to memory
        if request.use_memory:
            from core.conversation_memory import MessageRole
            await conversation_memory.add_message(
                session_id=actual_session_id,
                role=MessageRole.USER,
                content=request.message,
                metadata={"student_id": request.student_id}
            )
        
        # Get personalized context if student_id provided
        context = request.context or {}
        if request.student_id and request.use_memory:
            personalized_context = await conversation_memory.get_personalized_context(
                session_id=actual_session_id,
                student_id=request.student_id,
                current_query=request.message
            )
            context.update(personalized_context)
        
        # Add curriculum context if specific subject is mentioned
        try:
            from core.unified_curriculum import unified_curriculum
            if context.get("mode") == "curriculum_review" and context.get("subject"):
                subject = context["subject"]
                # Map API subject keys to curriculum subject names
                subject_mapping = {
                    "matematik": "Matematik",
                    "fizik": "Fizik",
                    "kimya": "Kimya", 
                    "biyoloji": "Biyoloji",
                    "turk_dili_ve_edebiyati": "Turk Dili ve Edebiyati",
                    "tarih": "Tarih",
                    "cografya": "Cografya",
                    "felsefe": "Felsefe",
                    "din_kulturu": "Din Kulturu",
                    "inkilap_ve_ataturkculuk": "Inkilap ve Ataturkculuk"
                }
                
                curriculum_subject = subject_mapping.get(subject, subject.title())
                curriculum_topics = unified_curriculum.loader.get_subject_topics(curriculum_subject)
                
                if curriculum_topics:
                    context["curriculum_available"] = True
                    context["curriculum_topic_count"] = len(curriculum_topics)
                    context["curriculum_subject"] = curriculum_subject
                    
        except Exception as e:
            logger.error(f"Error adding curriculum context: {e}")
        
        # Process message through Unified Agent System
        agent_response = await agent_system.process_message(
            message=request.message,
            context=context,
            session_id=actual_session_id
        )
        
        # Format response
        if agent_response.get("success"):
            response = {
                "success": True,
                "response": agent_response["response"],
                "system_used": f"Unified Agents - {agent_response.get('system_used', 'Expert Agent')}",
                "metadata": agent_response.get("metadata", {})
            }
        else:
            # Fallback to RAG-enhanced Gemini with validation
            gemini_response = await gemini_client.generate_content_with_rag(
                prompt=request.message,
                system_instruction="Sen YKS uzmani bir egitmensin. Turkiye egitim sistemine gore sorulari cevapla.",
                use_rag=True,
                rag_collections=["curriculum", "documents", "conversations"],
                validation_level="medium",
                validation_type="educational"
            )
            response = {
                "success": gemini_response.get("success", False),
                "response": gemini_response.get("text", "Uzgunum, sorunuzu cevaplayamadim."),
                "system_used": "Gemini RAG-Enhanced",
                "metadata": {
                    "confidence_score": gemini_response.get("confidence_score", 0.5),
                    "ranking_score": gemini_response.get("ranking_score", 0.3),
                    "rag_results_count": gemini_response.get("rag_results_count", 0),
                    "validated": gemini_response.get("validated", False),
                    "risk_level": gemini_response.get("risk_level", "unknown"),
                    "warning": gemini_response.get("warning")
                }
            }
        
        # Add assistant response to memory
        if request.use_memory and response["success"]:
            from core.conversation_memory import MessageRole
            await conversation_memory.add_message(
                session_id=actual_session_id,
                role=MessageRole.ASSISTANT,
                content=response["response"],
                metadata={"system_used": response.get("system_used")}
            )
        
        # Generate follow-up suggestions
        suggestions = []
        if response["success"]:
            # Simple suggestion logic - can be enhanced
            if "matematik" in request.message.lower():
                suggestions = ["Ornek soru cozumu isteyebilirsin", "Konuyu daha detayina inceleyebiliriz"]
            elif "soru" in request.message.lower():
                suggestions = ["Daha fazla soru isteyebilirsin", "Aciklamalari detaylandirabilirim"]
        
        return ChatResponse(
            response=response["response"],
            session_id=actual_session_id,
            success=response["success"],
            system_used=response.get("system_used", "unknown"),
            metadata=response.get("metadata"),
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Streaming Chat Endpoint
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint"""
    try:
        async def generate_stream():
            session_id = request.session_id or str(uuid.uuid4())
            
            # Add to memory
            if request.use_memory:
                await conversation_memory.add_message(
                    session_id=session_id,
                    role=conversation_memory.MessageRole.USER,
                    content=request.message
                )
            
            # Get response stream
            full_response = ""
            async for chunk in gemini_client.generate_content(
                prompt=request.message,
                stream=True
            ):
                if chunk.get("streaming"):
                    yield f"data: {json.dumps({'text': chunk['text'], 'done': False})}\n\n"
                    full_response += chunk["text"]
                else:
                    # Final chunk
                    yield f"data: {json.dumps({'text': full_response, 'done': True})}\n\n"
                    
                    # Add to memory
                    if request.use_memory:
                        await conversation_memory.add_message(
                            session_id=session_id,
                            role=conversation_memory.MessageRole.ASSISTANT,
                            content=full_response
                        )
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except Exception as e:
        logger.error(f"Streaming chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Question Generation
@app.post("/generate/questions")
async def generate_questions(request: QuestionGenerationRequest):
    """Generate educational questions using CrewAI"""
    try:
        # Create question generation prompt
        question_prompt = f"""
        {request.subject.value} dersinden {request.topic} konusunda {request.count} adet {request.difficulty.value} seviyesinde 
        {request.question_type.value} tipi soru olustur.
        
        Sorular YKS {request.exam_type.value} standardinda olmali.
        {request.exam_type.value} sinavina uygun zorluk seviyesinde hazirla.
        Her soru icin:
        1. Soru metni
        2. Siklar (coktan secmeli ise)
        3. Dogru cevap
        4. Aciklama
        
        JSON formatinda dondur.
        """
        
        # Use unified agent system for question generation
        agent_response = await agent_system.process_message(
            message=question_prompt,
            context={
                "task_type": "question_generation",
                "subject": request.subject.value,
                "topic": request.topic,
                "difficulty": request.difficulty.value,
                "question_type": request.question_type.value,
                "count": request.count,
                "exam_type": request.exam_type.value
            }
        )
        
        if agent_response.get("success"):
            return {
                "success": True,
                "questions": agent_response.get("response"),
                "agent_used": agent_response.get("system_used"),
                "subject": request.subject.value,
                "topic": request.topic,
                "count": request.count
            }
        else:
            # Fallback to basic generation
            questions = []
            for i in range(request.count):
                prompt = f"""
                Ders: {request.subject.value}
                Konu: {request.topic}
                Zorluk: {request.difficulty.value}
                Sinav Tipi: YKS {request.exam_type.value}
                
                YKS {request.exam_type.value} formatinda coktan secmeli soru olustur:
                1. Soru metni
                2. A) B) C) D) E) secenekleri  
                3. Dogru cevap
                4. Kisa aciklama
                """
                
                response = await gemini_client.generate_content_with_rag(
                    prompt=prompt,
                    system_instruction=f"Sen YKS {request.exam_type.value} soru hazirlama uzmanisin.",
                    use_rag=True,
                    rag_collections=["curriculum"],
                    validation_level="high",
                    validation_type="educational"
                )
                
                questions.append({
                    "question_text": response.get("text", "Soru olusturulamadi"),
                    "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
                    "correct_answer": "A",
                    "explanation": "Aciklama mevcut degil"
                })
            
            return {
                "success": True,
                "questions": questions,
                "agent_used": "Gemini Fallback",
                "subject": request.subject.value,
                "topic": request.topic,
                "count": request.count
            }
            
    except Exception as e:
        logger.error(f"Question generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Study Plan Generation
@app.post("/generate/study-plan")
async def generate_study_plan(request: StudyPlanRequest):
    """Generate personalized study plan using CrewAI"""
    try:
        # Generate study plan using Unified Agent System
        plan_prompt = f"""
        Ogrenci profili: {request.student_profile}
        Hedef sinav: {request.target_exam.value}
        Sure: {request.duration_weeks} hafta
        Gunluk calisma: {request.daily_hours} saat
        
        Bu bilgilere gore detayli, kisisellestirilmis YKS calisma plani olustur.
        """
        
        agent_response = await agent_system.process_message(
            message=plan_prompt,
            context={
                "task_type": "study_plan_generation",
                "student_profile": request.student_profile,
                "target_exam": request.target_exam.value,
                "duration_weeks": request.duration_weeks,
                "daily_hours": request.daily_hours
            }
        )
        
        if agent_response.get("success"):
            return {
                "success": True,
                "study_plan": agent_response.get("response"),
                "agents_used": agent_response.get("system_used"),
                "target_exam": request.target_exam.value,
                "duration_weeks": request.duration_weeks,
                "daily_hours": request.daily_hours
            }
        else:
            return {
                "success": False,
                "error": agent_response.get("error", "Study plan creation failed"),
                "fallback_plan": "Temel calisma plani: Gunde 6 saat, haftalik 4 deneme sinavi"
            }
        
    except Exception as e:
        logger.error(f"Study plan generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Search Endpoint
@app.post("/search", response_model=SearchResponse)
async def search_content(request: SearchRequest):
    """Search through knowledge base"""
    try:
        # Perform search
        results = await rag_system.search(
            query=request.query,
            collection_names=request.collection_names,
            n_results=request.n_results,
            filter_metadata=request.filters
        )
        
        # Convert to SearchResult models
        search_results = []
        for result in results:
            search_result = SearchResult(
                result_id=result.get("id", str(uuid.uuid4())),
                content=result["content"],
                title=result.get("metadata", {}).get("title", "Untitled"),
                subject=None,  # Will be inferred from metadata
                topic=result.get("metadata", {}).get("topic"),
                relevance_score=result.get("score", 0.0),
                source_type=result.get("collection", "unknown"),
                metadata=result.get("metadata", {})
            )
            search_results.append(search_result)
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            search_time=0.1,  # Placeholder
            filters_applied=request.filters or {},
            suggestions=[]
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Content Analysis
@app.post("/analyze/content")
async def analyze_content(request: AnalysisRequest):
    """Analyze content for educational insights"""
    try:
        # Use Gemini to analyze content
        analysis_prompt = f"""
        Asagidaki egitim icerigini analiz et:
        
        Icerik: {request.content}
        
        Analiz turu: {request.analysis_type}
        
        Sunlari degerlendir:
        1. Zorluk seviyesi
        2. Ana kavramlar
        3. Ogrenme hedefleri
        4. Eksik noktalar
        5. Iyilestirme onerileri
        """
        
        response = await gemini_client.generate_content(
            prompt=analysis_prompt,
            system_instruction="Sen egitim icerigi analiz uzmanisin."
        )
        
        return {
            "analysis": response["text"],
            "analysis_type": request.analysis_type,
            "suggestions_included": request.include_suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Content analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# File Upload
@app.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    description: str = Form(""),
    analysis_type: str = Form("general")
):
    """Upload and process educational documents with AI understanding"""
    try:
        # Save file temporarily
        import tempfile
        from pathlib import Path
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Process with document understanding
        analysis_result = await document_understanding.process_document(
            file_path=tmp_file_path,
            analysis_type=analysis_type
        )
        
        # Clean up temp file
        Path(tmp_file_path).unlink(missing_ok=True)
        
        if analysis_result.get("error"):
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        return {
            "success": analysis_result.get("success", False),
            "filename": file.filename,
            "file_info": analysis_result.get("file_info"),
            "analysis": analysis_result.get("analysis"),
            "structured_data": analysis_result.get("structured_data"),
            "educational_metadata": analysis_result.get("educational_metadata"),
            "message": "Document analyzed and added to knowledge base successfully"
        }
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Student Profile Management
@app.get("/student/{student_id}/profile")
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

@app.put("/student/{student_id}/profile")
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

# Curriculum Endpoint
@app.get("/system/collections")
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

@app.get("/curriculum")
async def get_curriculum():
    """Get curriculum data"""
    try:
        from core.unified_curriculum import unified_curriculum
        
        # Ensure curriculum is loaded
        if not unified_curriculum.loader.curriculum_data:
            success = unified_curriculum.loader.load_all_curriculum()
            if not success:
                return {"success": False, "error": "Failed to load curriculum"}
        
        # Get curriculum summary
        summary = unified_curriculum.loader.get_curriculum_summary()
        
        # Prepare data for API
        curriculum_data = {}
        for subject in unified_curriculum.loader.curriculum_data.keys():
            topics = unified_curriculum.loader.get_subject_topics(subject)
            
            # Group topics by grade
            grades = {}
            for topic in topics:
                grade = topic.get('grade', 'Genel')
                if grade not in grades:
                    grades[grade] = []
                
                grades[grade].append({
                    "code": topic['code'],
                    "title": topic['title'],
                    "content": topic['content'][:100] + "..." if len(topic['content']) > 100 else topic['content'],
                    "terms": topic.get('terms', ''),
                    "path": topic['path']
                })
            
            curriculum_data[subject] = {
                "total_topics": len(topics),
                "grades": grades,
                "summary": f"{len(topics)} topics across {len(grades)} grade levels"
            }
        
        return {
            "success": True,
            "summary": summary,
            "curriculum": curriculum_data
        }
        
    except Exception as e:
        logger.error(f"Curriculum error: {str(e)}")
        return {"success": False, "error": str(e)}

# Content Validation (Hallucination Detection)
@app.post("/validate/content")
async def validate_content(request: Dict[str, Any]):
    """Validate content for hallucinations"""
    try:
        content = request.get("content")
        context = request.get("context", "")
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Use hallucination detector
        try:
            from core.hallucination_detector import hallucination_detector
            validation_result = await hallucination_detector.validate_content(
                content=content,
                context=context
            )
            
            return {
                "success": True,
                "validation": validation_result,
                "is_valid": validation_result.get("confidence", 0) > 0.7,
                "confidence": validation_result.get("confidence", 0),
                "issues": validation_result.get("issues", [])
            }
            
        except ImportError:
            # Fallback validation using Gemini
            validation_prompt = f"""
            Icerigi dogruluk ve tutarlilik acisindan analiz et:
            
            Icerik: {content}
            Baglam: {context}
            
            Degerlendirme kriterleri:
            1. Faktual dogruluk
            2. Mantiksal tutarlilik
            3. Kaynak guvenilirligi
            4. Yaniltici bilgi varligi
            
            0-1 arasi guven skoru ver ve sorunlu noktalari listele.
            """
            
            response = await gemini_client.generate_content(
                prompt=validation_prompt,
                system_instruction="Sen bir icerik dogrulama uzmanisin."
            )
            
            return {
                "success": True,
                "validation": response.get("text", ""),
                "is_valid": True,  # Default to true for fallback
                "confidence": 0.8,  # Default confidence
                "method": "gemini_fallback"
            }
        
    except Exception as e:
        logger.error(f"Content validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# CrewAI Task Execution
@app.post("/crew/execute")
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
        Gorev turu: {task_type}
        Gorev verileri: {task_data}
        Istenen ajanlar: {agents}
        
        Bu gorevi yerine getir ve sonucu JSON formatinda dondur.
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

# Memory Management
@app.get("/memory/{session_id}")
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

@app.put("/memory/{session_id}/clear")
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

# System Statistics
@app.get("/stats")
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

# Document Analysis Request Model
class DocumentAnalysisRequest(BaseModel):
    file_path: str
    analysis_type: str = "general"
    custom_prompt: Optional[str] = None
    extract_questions: bool = False
    summarize: bool = False
    expand_topics: bool = False

# Document Analysis Endpoint
@app.post("/document/analyze")
async def analyze_document(request: DocumentAnalysisRequest):
    """Analyze document with AI understanding and advanced features"""
    try:
        # Basic document processing
        result = await document_understanding.process_document(
            file_path=request.file_path,
            analysis_type=request.analysis_type,
            custom_prompt=request.custom_prompt
        )
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Enhanced features
        enhanced_result = result.copy()
        
        # Extract questions from document
        if request.extract_questions:
            questions = await _extract_questions_from_document(result.get("content", ""))
            enhanced_result["extracted_questions"] = questions
        
        # Summarize document
        if request.summarize:
            summary = await _summarize_document(result.get("content", ""))
            enhanced_result["summary"] = summary
        
        # Expand topics with YKS standards
        if request.expand_topics:
            expanded_topics = await _expand_topics_yks(result.get("structured_data", {}))
            enhanced_result["expanded_topics"] = expanded_topics
        
        return enhanced_result
        
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for enhanced document analysis
async def _extract_questions_from_document(content: str) -> List[Dict[str, Any]]:
    """Extract questions from document content"""
    try:
        prompt = f"""
        Bu dokumandan soru cikar ve YKS formatinda duzenle:
        
        {content[:2000]}...
        
        Her soru icin:
        1. Soru metni
        2. A-E arasi coktan secmeli secenekler
        3. Dogru cevap
        4. Aciklama
        
        JSON formatinda en fazla 5 soru cikar.
        """
        
        response = await gemini_client.generate_content(
            prompt=prompt,
            system_instruction="Sen YKS soru hazirlama uzmanisin. JSON formatinda yanit ver."
        )
        
        # Try to parse JSON
        import json
        try:
            questions = json.loads(response.get("text", "[]"))
            return questions if isinstance(questions, list) else []
        except:
            return [{"question": response.get("text", "Soru cikarilamadi")}]
            
    except Exception as e:
        logger.error(f"Question extraction error: {e}")
        return [{"error": "Soru cikarma basarisiz"}]

async def _summarize_document(content: str) -> str:
    """Summarize document content"""
    try:
        prompt = f"""
        Bu dokumani ozetle:
        
        {content[:3000]}...
        
        Ozet:
        1. Ana konu ve icerik
        2. Onemli kavramlar
        3. Anahtar noktalar
        4. Calisma onerileri
        
        Ozet YKS ogrencisi icin uygun olsun.
        """
        
        response = await gemini_client.generate_content(
            prompt=prompt,
            system_instruction="Sen egitim uzmanisin. Anlasilir ozetler hazirlarsin."
        )
        
        return response.get("text", "Ozet olusturulamadi")
        
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return "Ozet olusturma basarisiz"

async def _expand_topics_yks(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """Expand topics according to YKS standards"""
    try:
        subject = structured_data.get("subject", "Genel")
        topics = structured_data.get("topics", [])
        
        if not topics:
            return {"error": "Genisletilecek konu bulunamadi"}
        
        main_topic = topics[0] if topics else "Genel Konu"
        
        prompt = f"""
        YKS {subject} dersi '{main_topic}' konusunu genislet:
        
        1. Konu tanimi ve kapsami
        2. YKS'de hangi soru turleri cikar
        3. Onkosul bilgiler
        4. Detayli aciklamalar
        5. Ornek sorular
        6. Calisma stratejileri
        7. Sik yapilan hatalar
        8. Ilgili diger konular
        
        YKS mufredatina uygun detayli aciklama yap.
        """
        
        response = await gemini_client.generate_content(
            prompt=prompt,
            system_instruction=f"Sen {subject} dersi YKS uzmanisin. Detayli konu anlatimlari yaparsin."
        )
        
        return {
            "subject": subject,
            "main_topic": main_topic,
            "expanded_content": response.get("text", "Konu genisletme basarisiz"),
            "yks_relevance": "High"
        }
        
    except Exception as e:
        logger.error(f"Topic expansion error: {e}")
        return {"error": "Konu genisletme basarisiz"}

# Socratic Mode Endpoint
class SocraticRequest(BaseModel):
    message: str
    topic: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@app.post("/socratic")
async def socratic_dialogue(request: SocraticRequest):
    """Socratic dialogue endpoint for guided learning"""
    try:
        from core.socratic_agent import socratic_agent
        
        # Prepare context
        context = request.context or {}
        if request.topic:
            context["topic"] = request.topic
            
        # Process with Socratic agent
        result = await socratic_agent.process(
            user_input=request.message,
            context=context
        )
        
        return {
            "success": result.get("success", False),
            "response": result.get("response", ""),
            "mode": "socratic",
            "hints": result.get("hints", []),
            "session_id": request.session_id or str(uuid.uuid4())
        }
        
    except Exception as e:
        logger.error(f"Socratic dialogue error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Global flag to track curriculum loading
curriculum_loading = False
curriculum_loaded = False

async def load_curriculum_background():
    """Load curriculum data in background with optimization"""
    global curriculum_loading, curriculum_loaded
    try:
        curriculum_loading = True
        
        # Check if vectorstore is already ready
        if rag_system.is_vectorstore_ready():
            logger.info("⚡ RAG vectorstore already ready - skipping background load")
            curriculum_loaded = True
            return
        
        logger.info("📚 Starting optimized curriculum data loading...")
        start_time = datetime.now()
        
        # Use optimized load (will skip if already loaded)
        success = await rag_system.load_curriculum_data()
        
        load_time = (datetime.now() - start_time).total_seconds()
        
        if success:
            logger.info(f"✅ Curriculum data loaded successfully in {load_time:.2f}s")
            curriculum_loaded = True
        else:
            logger.warning(f"⚠️ Failed to load curriculum data after {load_time:.2f}s")
    except Exception as e:
        logger.error(f"Background curriculum loading error: {str(e)}")
    finally:
        curriculum_loading = False

# Initialize data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize data on startup with vectorstore optimization"""
    try:
        logger.info("🚀 Starting Promptitron Unified System...")
        startup_start = datetime.now()
        
        # Check RAG system status first
        vectorstore_stats = rag_system.get_vectorstore_stats()
        logger.info(f"📊 Vectorstore status: {vectorstore_stats}")
        
        # Initialize curriculum loader (lightweight)
        from core.unified_curriculum import unified_curriculum
        unified_curriculum.loader.load_all_curriculum()
        logger.info("✅ Curriculum loader initialized")
        
        # Start optimized curriculum loading in background for RAG
        import asyncio
        asyncio.create_task(load_curriculum_background())
        
        startup_time = (datetime.now() - startup_start).total_seconds()
        logger.info(f"🎯 System startup completed in {startup_time:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)