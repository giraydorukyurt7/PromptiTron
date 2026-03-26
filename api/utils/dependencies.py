"""API Dependencies"""
from typing import Optional
import uuid

def get_session_id(session_id: Optional[str] = None) -> str:
    """Get or create session ID"""
    return session_id or str(uuid.uuid4())