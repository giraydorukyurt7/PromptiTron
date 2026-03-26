"""Custom API Exceptions"""
from fastapi import HTTPException

class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)

class ContentNotFoundError(HTTPException):
    def __init__(self, detail: str = "Content not found"):
        super().__init__(status_code=404, detail=detail)

class SystemError(HTTPException):
    def __init__(self, detail: str = "Internal system error"):
        super().__init__(status_code=500, detail=detail)

class SessionNotFoundError(HTTPException):
    def __init__(self, session_id: str):
        super().__init__(status_code=404, detail=f"Session {session_id} not found")