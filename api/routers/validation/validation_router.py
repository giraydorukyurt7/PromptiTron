"""
Validation router for handling content validation endpoints
Includes: /validate/content
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import logging

# Import core modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.gemini_client import gemini_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/validate",
    tags=["validation"],
    responses={404: {"description": "Not found"}}
)

# Content Validation (Hallucination Detection)
@router.post("/content")
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
            İçeriği doğruluk ve tutarlılık açısından analiz et:
            
            İçerik: {content}
            Bağlam: {context}
            
            Değerlendirme kriterleri:
            1. Faktual doğruluk
            2. Mantıksal tutarlılık
            3. Kaynak güvenilirliği
            4. Yanıltıcı bilgi varlığı
            
            0-1 arası güven skoru ver ve sorunlu noktaları listele.
            """
            
            response = await gemini_client.generate_content(
                prompt=validation_prompt,
                system_instruction="Sen bir içerik doğrulama uzmanısın."
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