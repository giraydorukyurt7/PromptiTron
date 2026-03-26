"""Response models for API endpoints"""
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

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
    services: Dict[str, str]

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_found: int
    search_metadata: Dict[str, Any]
    personalized_ranking: Optional[List[int]] = None

class AnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    summary: str
    suggestions: Optional[List[str]] = None
    metadata: Dict[str, Any]

class ValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]

class CrewExecutionResponse(BaseModel):
    result: str
    agents_used: List[str]
    execution_time: float
    metadata: Dict[str, Any]

class MemoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    total_messages: int
    metadata: Dict[str, Any]

class StatsResponse(BaseModel):
    total_requests: int
    total_sessions: int
    active_collections: int
    system_health: str
    uptime: float
    memory_usage: Dict[str, Any]

class DocumentAnalysisResponse(BaseModel):
    summary: str
    key_points: List[str]
    topics: List[str]
    metadata: Dict[str, Any]
    questions: Optional[List[str]] = None
    study_guide: Optional[Dict[str, Any]] = None

class WebAnalysisResponse(BaseModel):
    url: str
    title: str
    summary: str
    main_topics: List[str]
    links: Optional[List[str]] = None
    metadata: Dict[str, Any]

class YouTubeAnalysisResponse(BaseModel):
    video_id: str
    title: str
    duration: str
    summary: str
    key_points: List[str]
    transcript: Optional[str] = None
    educational_value: str
    topics: List[str]
    metadata: Dict[str, Any]

class CurriculumResponse(BaseModel):
    curriculum_data: Dict[str, Any]
    total_subjects: int
    total_topics: int
    metadata: Dict[str, Any]

class QuestionGenerationResponse(BaseModel):
    questions: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    difficulty_distribution: Dict[str, int]

class StudyPlanResponse(BaseModel):
    plan: Dict[str, Any]
    weekly_schedule: List[Dict[str, Any]]
    total_hours: int
    metadata: Dict[str, Any]

class ConceptMapResponse(BaseModel):
    concept_map: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class ExplanationResponse(BaseModel):
    explanation: str
    examples: Optional[List[str]] = None
    diagrams: Optional[List[str]] = None
    related_topics: List[str]
    metadata: Dict[str, Any]

class SocraticResponse(BaseModel):
    response: str
    question: Optional[str] = None
    hints: Optional[List[str]] = None
    session_id: str
    progress: Dict[str, Any]
    metadata: Dict[str, Any]