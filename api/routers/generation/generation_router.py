"""
Generation router for handling question and study plan generation endpoints
Includes: /generate/questions, /generate/study-plan
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import logging

# Import models
from ...models.request_models import QuestionGenerationRequest, StudyPlanRequest

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.gemini_client import gemini_client
from core.agents import agent_system

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/generate",
    tags=["generation"],
    responses={404: {"description": "Not found"}}
)

# Question Generation
@router.post("/questions")
async def generate_questions(request: QuestionGenerationRequest):
    """Generate educational questions using CrewAI"""
    try:
        # Create question generation prompt
        question_prompt = f"""
        {request.subject.value} dersinden {request.topic} konusunda {request.count} adet {request.difficulty.value} seviyesinde 
        {request.question_type.value} tipi soru oluştur.
        
        Sorular YKS {request.exam_type.value} standardında olmalı.
        {request.exam_type.value} sınavına uygun zorluk seviyesinde hazırla.
        Her soru için:
        1. Soru metni
        2. Şıklar (çoktan seçmeli ise)
        3. Doğru cevap
        4. Açıklama
        
        JSON formatında döndür.
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
                Sınav Tipi: YKS {request.exam_type.value}
                
                YKS {request.exam_type.value} formatında çoktan seçmeli soru oluştur:
                1. Soru metni
                2. A) B) C) D) E) seçenekleri  
                3. Doğru cevap
                4. Kısa açıklama
                """
                
                response = await gemini_client.generate_content_with_rag(
                    prompt=prompt,
                    system_instruction=f"Sen YKS {request.exam_type.value} soru hazırlama uzmanısın.",
                    use_rag=True,
                    rag_collections=["curriculum"],
                    validation_level="high",
                    validation_type="educational"
                )
                
                questions.append({
                    "question_text": response.get("text", "Soru oluşturulamadı"),
                    "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
                    "correct_answer": "A",
                    "explanation": "Açıklama mevcut değil"
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
@router.post("/study-plan")
async def generate_study_plan(request: StudyPlanRequest):
    """Generate personalized study plan using CrewAI"""
    try:
        # Generate study plan using Unified Agent System
        plan_prompt = f"""
        Öğrenci profili: {request.student_profile}
        Hedef sınav: {request.target_exam.value}
        Süre: {request.duration_weeks} hafta
        Günlük çalışma: {request.daily_hours} saat
        
        Bu bilgilere göre detaylı, kişiselleştirilmiş YKS çalışma planı oluştur.
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
                "fallback_plan": "Temel çalışma planı: Günde 6 saat, haftalık 4 deneme sınavı"
            }
        
    except Exception as e:
        logger.error(f"Study plan generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))