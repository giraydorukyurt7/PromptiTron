"""
Chat router for handling chat-related endpoints
Includes: /chat, /chat/stream, /socratic
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any, Optional
import logging
import json
import uuid
import asyncio

# Import models - use absolute imports within api package
import sys
import os
api_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if api_path not in sys.path:
    sys.path.insert(0, api_path)

from models.request_models import ChatRequest, SocraticRequest
from models.response_models import ChatResponse
from utils.dependencies import get_session_id

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.gemini_client import gemini_client
from core.agents import agent_system
from core.conversation_memory import conversation_memory, MessageRole

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}}
)

# Chat Endpoint
@router.post("/", response_model=ChatResponse)
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
                    "turk_dili_ve_edebiyati": "Türk Dili ve Edebiyatı",
                    "tarih": "Tarih",
                    "cografya": "Coğrafya",
                    "felsefe": "Felsefe",
                    "din_kulturu": "Din Kültürü",
                    "inkilap_ve_ataturkculuk": "İnkılap ve Atatürkçülük"
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
                system_instruction="Sen YKS uzmanı bir eğitmensin. Türkiye eğitim sistemine göre soruları cevapla.",
                use_rag=True,
                rag_collections=["curriculum", "documents", "conversations"],
                validation_level="medium",
                validation_type="educational"
            )
            response = {
                "success": gemini_response.get("success", False),
                "response": gemini_response.get("text", "Üzgünüm, sorunuzu cevaplayamadım."),
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
                suggestions = ["Örnek soru çözümü isteyebilirsin", "Konuyu daha detayına inceleyebiliriz"]
            elif "soru" in request.message.lower():
                suggestions = ["Daha fazla soru isteyebilirsin", "Açıklamaları detaylandırabilirim"]
        
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
@router.post("/stream")
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

# Standard Socratic Mode (backward compatibility)
@router.post("/socratic")
async def socratic_dialogue(request: SocraticRequest):
    """Standard Socratic dialogue endpoint for guided learning"""
    try:
        # Prepare enhanced context
        context = {"mode": "socratic"}
        
        if hasattr(request, 'topic') and request.topic:
            context["topic"] = request.topic
            
        # Create Socratic prompt
        socratic_prompt = f"""
        Öğrenci sorusu/yanıtı: {request.user_input}
        
        Sokratik yöntemle rehberlik et:
        1. Öğrenciyi düşündürücü sorularla yönlendir
        2. Doğrudan cevap verme, keşfetmesine yardım et
        3. Küçük ipuçları ve rehberlik sağla
        4. Öğrencinin yanıtlarını analiz et ve devam et
        5. Kritik düşünmeyi teşvik et
        
        Müfredat konularından hareketle derin öğrenmeyi destekle.
        """
        
        # Use agent system with Socratic approach
        agent_response = await agent_system.process_message(
            message=socratic_prompt,
            context=context
        )
        
        if agent_response.get("success"):
            # Extract hints and guidance from response
            response_text = agent_response.get("response", "")
            hints = []
            
            # Simple hint extraction (can be enhanced)
            if "ipucu" in response_text.lower():
                hints.append("Bu konuda daha derin düşünmeye devam et")
            if "soru" in response_text.lower() and "?" in response_text:
                hints.append("Soru sorma becerinizi geliştiriyorsunuz")
                
            return {
                "success": True,
                "response": response_text,
                "mode": "socratic",
                "hints": hints,
                "session_id": request.session_id or str(uuid.uuid4()),
                "agent_used": agent_response.get("system_used", "Socratic Agent")
            }
        else:
            # Fallback Socratic approach
            fallback_response = await gemini_client.generate_content(
                prompt=socratic_prompt,
                system_instruction="Sen Sokratik öğretim uzmanısın. Öğrencileri soru sorarak öğrenmeye yönlendirirsin."
            )
            
            return {
                "success": True,
                "response": fallback_response.get("text", "Sokratik diyalog devam edemiyor."),
                "mode": "socratic",
                "hints": ["Düşünmeye devam et", "Sorular sormaya çalış"],
                "session_id": request.session_id or str(uuid.uuid4()),
                "agent_used": "Gemini Socratic Fallback"
            }
        
    except Exception as e:
        logger.error(f"Socratic dialogue error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))