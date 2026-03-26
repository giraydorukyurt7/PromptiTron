"""
Content router for handling content analysis and upload endpoints
Includes: /analyze/content, /upload/document, /document/analyze, /web/analyze, /youtube/analyze
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional, Union
import logging
import time
import tempfile
from pathlib import Path
from datetime import datetime
import json

# Import models
from pydantic import BaseModel

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.gemini_client import gemini_client
from core.document_understanding import document_understanding
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

router = APIRouter(
    prefix="",
    tags=["content"],
    responses={404: {"description": "Not found"}}
)

# Request Models
class AnalysisRequest(BaseModel):
    content: str
    analysis_type: str = "comprehensive"
    include_suggestions: bool = True

class DocumentAnalysisRequest(BaseModel):
    file_path: str
    analysis_type: str = "general"
    custom_prompt: Optional[str] = None
    extract_questions: bool = False
    summarize: bool = False
    expand_topics: bool = False

class WebAnalysisRequest(BaseModel):
    url: str
    analysis_type: str = "comprehensive"
    custom_prompt: Optional[str] = None

class YouTubeAnalysisRequest(BaseModel):
    url: str
    analysis_type: str = "comprehensive"
    custom_prompt: Optional[str] = None

# Content Analysis
@router.post("/analyze/content")
async def analyze_content(request: AnalysisRequest):
    """Analyze content for educational insights"""
    try:
        # Use Gemini to analyze content
        analysis_prompt = f"""
        Aşağıdaki eğitim içeriğini analiz et:
        
        İçerik: {request.content}
        
        Analiz türü: {request.analysis_type}
        
        Şunları değerlendir:
        1. Zorluk seviyesi
        2. Ana kavramlar
        3. Öğrenme hedefleri
        4. Eksik noktalar
        5. İyileştirme önerileri
        """
        
        response = await gemini_client.generate_content(
            prompt=analysis_prompt,
            system_instruction="Sen eğitim içeriği analiz uzmanısın."
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
@router.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    description: str = Form(""),
    analysis_type: str = Form("general")
):
    """Upload and process educational documents with AI understanding"""
    try:
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

# Document Analysis Endpoint
@router.post("/document/analyze")
async def analyze_document(request: Union[DocumentAnalysisRequest, WebAnalysisRequest]):
    """Analyze document or web URL with AI understanding and advanced features"""
    try:
        if isinstance(request, WebAnalysisRequest):
            # Process web URL
            start_time = time.time()
            from core.web_analyzer import web_analyzer
            
            result = await web_analyzer.analyze_website(
                url=request.url,
                analysis_type=request.analysis_type,
                custom_prompt=request.custom_prompt
            )
            
            processing_time = time.time() - start_time
            
            if result.get("error"):
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": result["error"],
                        "suggestion": result.get("suggestion", ""),
                        "processing_time": processing_time
                    }
                )
            
            return JSONResponse(content={
                **result,
                "processing_time": processing_time
            })
        
        # Basic document processing (existing functionality)
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
        
        # Save full results as JSON file
        if enhanced_result.get("success"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"document_analysis_{timestamp}.json"
            
            try:
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(enhanced_result, f, ensure_ascii=False, indent=2)
                enhanced_result["json_file"] = json_filename
                logger.info(f"Analysis results saved to {json_filename}")
            except Exception as e:
                logger.error(f"Failed to save JSON: {e}")
        
        return enhanced_result
        
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add dedicated web analysis endpoint  
@router.post("/web/analyze")
async def analyze_website(request: WebAnalysisRequest):
    """Analyze website content for educational value and YKS curriculum compliance"""
    try:
        start_time = time.time()
        from core.web_analyzer import web_analyzer
        
        console.print(f"[cyan]API: Analyzing website - {request.url}[/cyan]")
        
        result = await web_analyzer.analyze_website(
            url=request.url,
            analysis_type=request.analysis_type,
            custom_prompt=request.custom_prompt
        )
        
        processing_time = time.time() - start_time
        
        if result.get("error"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": result["error"],
                    "suggestion": result.get("suggestion", ""),
                    "processing_time": processing_time
                }
            )
        
        console.print(f"[green]API: Website analysis completed in {processing_time:.2f}s[/green]")
        
        return JSONResponse(content={
            **result,
            "processing_time": processing_time
        })
        
    except Exception as e:
        logger.error(f"Web analysis API error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Web sitesi analizi sırasında hata oluştu: {str(e)}"
            }
        )

# Add YouTube video analysis endpoint  
@router.post("/youtube/analyze")
async def analyze_youtube_video(request: YouTubeAnalysisRequest):
    """Analyze YouTube video content for educational value and YKS curriculum compliance"""
    try:
        start_time = time.time()
        from core.youtube_analyzer import youtube_analyzer
        
        console.print(f"[cyan]API: Analyzing YouTube video - {request.url}[/cyan]")
        
        result = await youtube_analyzer.analyze_youtube_video(
            url=request.url,
            analysis_type=request.analysis_type,
            custom_prompt=request.custom_prompt
        )
        
        processing_time = time.time() - start_time
        
        if result.get("error"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": result["error"],
                    "suggestion": result.get("suggestion", ""),
                    "processing_time": processing_time
                }
            )
        
        console.print(f"[green]API: YouTube video analysis completed in {processing_time:.2f}s[/green]")
        
        return JSONResponse(content={
            **result,
            "processing_time": processing_time
        })
        
    except Exception as e:
        logger.error(f"YouTube analysis API error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"YouTube video analizi sırasında hata oluştu: {str(e)}"
            }
        )

# Helper functions for enhanced document analysis
async def _extract_questions_from_document(content: str) -> List[Dict[str, Any]]:
    """Extract questions from document content"""
    try:
        prompt = f"""
        Bu dokümandan soru çıkar ve YKS formatında düzenle:
        
        {content[:2000]}...
        
        Her soru için:
        1. Soru metni
        2. A-E arası çoktan seçmeli seçenekler
        3. Doğru cevap
        4. Açıklama
        
        JSON formatında en fazla 5 soru çıkar.
        """
        
        response = await gemini_client.generate_content(
            prompt=prompt,
            system_instruction="Sen YKS soru hazırlama uzmanısın. JSON formatında yanıt ver."
        )
        
        # Try to parse JSON
        try:
            questions = json.loads(response.get("text", "[]"))
            return questions if isinstance(questions, list) else []
        except:
            return [{"question": response.get("text", "Soru çıkarılamadı")}]
            
    except Exception as e:
        logger.error(f"Question extraction error: {e}")
        return [{"error": "Soru çıkarma başarısız"}]

async def _summarize_document(content: str) -> str:
    """Summarize document content"""
    try:
        prompt = f"""
        Bu dokümanı özetle:
        
        {content[:3000]}...
        
        Özet:
        1. Ana konu ve içerik
        2. Önemli kavramlar
        3. Anahtar noktalar
        4. Çalışma önerileri
        
        Özet YKS öğrencisi için uygun olsun.
        """
        
        response = await gemini_client.generate_content(
            prompt=prompt,
            system_instruction="Sen eğitim uzmanısın. Anlaşılır özetler hazırlarsın."
        )
        
        return response.get("text", "Özet oluşturulamadı")
        
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return "Özet oluşturma başarısız"

async def _expand_topics_yks(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """Expand topics according to YKS standards"""
    try:
        subject = structured_data.get("subject", "Genel")
        topics = structured_data.get("topics", [])
        
        if not topics:
            return {"error": "Genişletilecek konu bulunamadı"}
        
        main_topic = topics[0] if topics else "Genel Konu"
        
        prompt = f"""
        YKS {subject} dersi '{main_topic}' konusunu genişlet:
        
        1. Konu tanımı ve kapsamı
        2. YKS'de hangi soru türleri çıkar
        3. Önkoşul bilgiler
        4. Detaylı açıklamalar
        5. Örnek sorular
        6. Çalışma stratejileri
        7. Sık yapılan hatalar
        8. İlgili diğer konular
        
        YKS müfredatına uygun detaylı açıklama yap.
        """
        
        response = await gemini_client.generate_content(
            prompt=prompt,
            system_instruction=f"Sen {subject} dersi YKS uzmanısın. Detaylı konu anlatımları yaparsın."
        )
        
        return {
            "subject": subject,
            "main_topic": main_topic,
            "expanded_content": response.get("text", "Konu genişletme başarısız"),
            "yks_relevance": "High"
        }
        
    except Exception as e:
        logger.error(f"Topic expansion error: {e}")
        return {"error": "Konu genişletme başarısız"}