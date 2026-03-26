"""Helper functions for API operations"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def create_response_metadata(
    execution_time: Optional[float] = None,
    system_used: Optional[str] = None,
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized response metadata"""
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }
    
    if execution_time is not None:
        metadata["execution_time"] = execution_time
    
    if system_used:
        metadata["system_used"] = system_used
    
    if additional_info:
        metadata.update(additional_info)
    
    return metadata

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format"""
    if not session_id or len(session_id) < 10:
        return False
    return True

def sanitize_content(content: str, max_length: int = 10000) -> str:
    """Sanitize and limit content length"""
    if not content:
        return ""
    
    # Remove any potentially harmful content
    sanitized = content.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized

def log_api_call(endpoint: str, params: Dict[str, Any], execution_time: float):
    """Log API call for monitoring"""
    logger.info(f"API call: {endpoint} - {execution_time:.2f}s - Params: {len(str(params))} chars")