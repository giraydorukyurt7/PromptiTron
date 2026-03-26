"""Request models for API endpoints"""
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
# Import from local enums instead of root models
from .enums import SubjectType, DifficultyLevel, QuestionType, ExamType

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

class ContentValidationRequest(BaseModel):
    content: str
    content_type: str
    context: Optional[Dict[str, Any]] = None

class CrewExecutionRequest(BaseModel):
    task: str
    agents: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None

class DocumentAnalysisRequest(BaseModel):
    file_path: Optional[str] = None
    content: Optional[str] = None
    analysis_type: str = "comprehensive"

class WebAnalysisRequest(BaseModel):
    url: str
    analysis_type: str = "comprehensive"
    custom_prompt: Optional[str] = None

class YouTubeAnalysisRequest(BaseModel):
    url: str
    analysis_type: str = "comprehensive"
    custom_prompt: Optional[str] = None

class CurriculumQuestionRequest(BaseModel):
    subject: str
    grade_level: str
    topic: Optional[str] = None
    count: int = 5
    difficulty: str = "medium"
    question_type: str = "multiple_choice"

class CurriculumSummarizeRequest(BaseModel):
    subject: str
    grade_level: str
    topic: Optional[str] = None
    detail_level: str = "comprehensive"

class ConceptMapRequest(BaseModel):
    subject: str
    topic: str
    depth: int = 2
    include_relationships: bool = True

class ExplainRequest(BaseModel):
    topic: str
    subject: str
    grade_level: str
    learning_style: str = "visual"
    include_examples: bool = True

class SocraticRequest(BaseModel):
    topic: str
    subject: str
    user_input: str
    session_id: Optional[str] = None
    difficulty_level: str = "medium"