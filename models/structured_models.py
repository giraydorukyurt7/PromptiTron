"""
Structured output models for Gemini API integration
Provides type-safe responses and validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class SubjectType(str, Enum):
    MATEMATIK = "matematik"
    FIZIK = "fizik"
    KIMYA = "kimya"
    BIYOLOJI = "biyoloji"
    COGRAFYA = "cografya"
    TARIH = "tarih"
    FELSEFE = "felsefe"
    EDEBIYAT = "edebiyat"
    TURKCE = "turkce"
    DIN_KULTURU = "din_kulturu"
    INKILAP_TARIHI = "inkilap_tarihi"
    INGILIZCE = "ingilizce"

class ExamType(str, Enum):
    TYT = "TYT"
    AYT = "AYT"
    YKS = "YKS"
    LGS = "LGS"

# Question Generation Models
class MultipleChoiceOption(BaseModel):
    option_letter: str = Field(description="Option letter (A, B, C, D, E)")
    option_text: str = Field(description="Option content")

class GeneratedQuestion(BaseModel):
    question_id: str = Field(description="Unique question identifier")
    question_text: str = Field(description="The actual question")
    question_type: QuestionType = Field(description="Type of question")
    subject: SubjectType = Field(description="Subject area")
    topic: str = Field(description="Specific topic within subject")
    difficulty: DifficultyLevel = Field(description="Difficulty level")
    options: Optional[List[MultipleChoiceOption]] = Field(description="Options for multiple choice questions")
    correct_answer: str = Field(description="Correct answer")
    explanation: str = Field(description="Detailed explanation of the answer")
    keywords: List[str] = Field(description="Important keywords in the question")
    estimated_time: int = Field(description="Estimated time to solve in minutes")
    
    @validator('options')
    def validate_options(cls, v, values):
        if values.get('question_type') == QuestionType.MULTIPLE_CHOICE and (not v or len(v) < 2):
            raise ValueError('Multiple choice questions must have at least 2 options')
        return v

class QuestionSet(BaseModel):
    set_id: str = Field(description="Question set identifier")
    title: str = Field(description="Title of the question set")
    description: str = Field(description="Description of the question set")
    subject: SubjectType = Field(description="Subject area")
    topics: List[str] = Field(description="Topics covered")
    difficulty: DifficultyLevel = Field(description="Overall difficulty level")
    questions: List[GeneratedQuestion] = Field(description="List of questions")
    total_questions: int = Field(description="Total number of questions")
    estimated_duration: int = Field(description="Estimated duration in minutes")
    created_at: datetime = Field(default_factory=datetime.now)

# Study Plan Models
class StudySession(BaseModel):
    session_id: str = Field(description="Session identifier")
    subject: SubjectType = Field(description="Subject to study")
    topic: str = Field(description="Specific topic")
    duration: int = Field(description="Duration in minutes")
    activities: List[str] = Field(description="Study activities")
    resources: List[str] = Field(description="Recommended resources")
    goals: List[str] = Field(description="Session goals")

class DailyStudyPlan(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    day_of_week: str = Field(description="Day of the week")
    total_study_hours: float = Field(description="Total study hours for the day")
    sessions: List[StudySession] = Field(description="Study sessions")
    breaks: List[str] = Field(description="Scheduled breaks")
    review_time: int = Field(description="Review time in minutes")
    
class WeeklyStudyPlan(BaseModel):
    week_start: str = Field(description="Week start date")
    week_end: str = Field(description="Week end date")
    focus_subjects: List[SubjectType] = Field(description="Focus subjects for the week")
    daily_plans: List[DailyStudyPlan] = Field(description="Daily study plans")
    weekly_goals: List[str] = Field(description="Weekly goals")
    assessment_schedule: List[str] = Field(description="Assessment schedule")

class StudyPlan(BaseModel):
    plan_id: str = Field(description="Study plan identifier")
    student_id: str = Field(description="Student identifier")
    exam_target: ExamType = Field(description="Target exam")
    exam_date: Optional[str] = Field(description="Target exam date")
    subjects: List[SubjectType] = Field(description="Subjects to study")
    weak_areas: List[str] = Field(description="Identified weak areas")
    strong_areas: List[str] = Field(description="Identified strong areas")
    weekly_plans: List[WeeklyStudyPlan] = Field(description="Weekly study plans")
    overall_strategy: str = Field(description="Overall study strategy")
    milestones: List[str] = Field(description="Study milestones")
    created_at: datetime = Field(default_factory=datetime.now)

# Content Analysis Models
class TopicAnalysis(BaseModel):
    topic_name: str = Field(description="Name of the topic")
    subject: SubjectType = Field(description="Subject area")
    complexity_score: float = Field(description="Complexity score (0-1)", ge=0, le=1)
    prerequisites: List[str] = Field(description="Required prerequisite topics")
    key_concepts: List[str] = Field(description="Key concepts to master")
    common_misconceptions: List[str] = Field(description="Common student misconceptions")
    learning_objectives: List[str] = Field(description="Learning objectives")
    estimated_study_time: int = Field(description="Estimated study time in hours")

class ContentSummary(BaseModel):
    summary_id: str = Field(description="Summary identifier")
    original_content: str = Field(description="Original content")
    summary_text: str = Field(description="Summarized content")
    key_points: List[str] = Field(description="Key points")
    important_formulas: List[str] = Field(description="Important formulas")
    examples: List[str] = Field(description="Key examples")
    summary_length: int = Field(description="Summary length in words")
    compression_ratio: float = Field(description="Compression ratio")

# Performance Analysis Models
class QuestionPerformance(BaseModel):
    question_id: str = Field(description="Question identifier")
    subject: SubjectType = Field(description="Subject")
    topic: str = Field(description="Topic")
    difficulty: DifficultyLevel = Field(description="Difficulty level")
    is_correct: bool = Field(description="Whether answer was correct")
    time_spent: int = Field(description="Time spent in seconds")
    attempts: int = Field(description="Number of attempts")
    confidence_level: float = Field(description="Student confidence (0-1)", ge=0, le=1)

class TopicPerformance(BaseModel):
    topic: str = Field(description="Topic name")
    subject: SubjectType = Field(description="Subject")
    total_questions: int = Field(description="Total questions attempted")
    correct_answers: int = Field(description="Number of correct answers")
    accuracy_rate: float = Field(description="Accuracy rate (0-1)", ge=0, le=1)
    average_time_per_question: float = Field(description="Average time per question in seconds")
    improvement_trend: str = Field(description="Improvement trend (improving/stable/declining)")
    weak_subtopics: List[str] = Field(description="Weak subtopics identified")

class StudentPerformanceReport(BaseModel):
    student_id: str = Field(description="Student identifier")
    reporting_period: str = Field(description="Reporting period")
    overall_performance: Dict[str, float] = Field(description="Overall performance metrics")
    subject_performances: List[TopicPerformance] = Field(description="Performance by subject")
    strengths: List[str] = Field(description="Identified strengths")
    weaknesses: List[str] = Field(description="Identified weaknesses")
    recommendations: List[str] = Field(description="Improvement recommendations")
    next_focus_areas: List[str] = Field(description="Next areas to focus on")
    generated_at: datetime = Field(default_factory=datetime.now)

# Search and Retrieval Models
class SearchResult(BaseModel):
    result_id: str = Field(description="Result identifier")
    content: str = Field(description="Content text")
    title: str = Field(description="Content title")
    subject: Optional[SubjectType] = Field(description="Subject if applicable")
    topic: Optional[str] = Field(description="Topic if applicable")
    relevance_score: float = Field(description="Relevance score (0-1)", ge=0, le=1)
    source_type: str = Field(description="Source type (curriculum/generated/conversation)")
    metadata: Dict[str, Any] = Field(description="Additional metadata")

class SearchResponse(BaseModel):
    query: str = Field(description="Original search query")
    results: List[SearchResult] = Field(description="Search results")
    total_results: int = Field(description="Total number of results")
    search_time: float = Field(description="Search execution time in seconds")
    filters_applied: Dict[str, Any] = Field(description="Filters that were applied")
    suggestions: List[str] = Field(description="Search suggestions")

# Conversation Models
class ConversationInsight(BaseModel):
    insight_type: str = Field(description="Type of insight")
    description: str = Field(description="Insight description")
    confidence: float = Field(description="Confidence level (0-1)", ge=0, le=1)
    supporting_evidence: List[str] = Field(description="Supporting evidence")

class ConversationAnalysis(BaseModel):
    session_id: str = Field(description="Conversation session ID")
    student_understanding_level: str = Field(description="Current understanding level")
    engagement_score: float = Field(description="Engagement score (0-1)", ge=0, le=1)
    confusion_indicators: List[str] = Field(description="Indicators of confusion")
    mastery_indicators: List[str] = Field(description="Indicators of mastery")
    learning_style_indicators: str = Field(description="Detected learning style")
    emotional_state: str = Field(description="Detected emotional state")
    insights: List[ConversationInsight] = Field(description="Generated insights")
    recommendations: List[str] = Field(description="Recommendations for improvement")

# Function Calling Result Models
class FunctionCallResult(BaseModel):
    function_name: str = Field(description="Name of the called function")
    parameters: Dict[str, Any] = Field(description="Parameters used")
    result: Dict[str, Any] = Field(description="Function result")
    execution_time: float = Field(description="Execution time in seconds")
    success: bool = Field(description="Whether function executed successfully")
    error_message: Optional[str] = Field(description="Error message if failed")

class AIResponse(BaseModel):
    response_id: str = Field(description="Response identifier")
    text_response: str = Field(description="Main text response")
    function_calls: List[FunctionCallResult] = Field(description="Function calls made")
    confidence_score: float = Field(description="Response confidence (0-1)", ge=0, le=1)
    sources_used: List[str] = Field(description="Sources referenced")
    follow_up_suggestions: List[str] = Field(description="Follow-up suggestions")
    personalization_applied: bool = Field(description="Whether personalization was applied")
    response_time: float = Field(description="Response generation time")
    model_used: str = Field(description="AI model used")

# Enhanced RAG Models
class RAGContext(BaseModel):
    query: str = Field(description="User query")
    retrieved_documents: List[SearchResult] = Field(description="Retrieved documents")
    context_used: str = Field(description="Context used for generation")
    relevance_threshold: float = Field(description="Relevance threshold applied")
    retrieval_method: str = Field(description="Retrieval method used")

class EnhancedResponse(BaseModel):
    answer: str = Field(description="Generated answer")
    confidence: float = Field(description="Answer confidence", ge=0, le=1)
    rag_context: RAGContext = Field(description="RAG context information")
    citations: List[str] = Field(description="Source citations")
    related_topics: List[str] = Field(description="Related topics")
    difficulty_level: DifficultyLevel = Field(description="Content difficulty level")
    personalization_notes: List[str] = Field(description="Personalization applied")

# Request Models
class DocumentAnalysisRequest(BaseModel):
    """Document analysis request model"""
    analysis_type: str = "educational"
    custom_prompt: Optional[str] = None
    session_id: Optional[str] = None

class WebAnalysisRequest(BaseModel):
    """Web analysis request model"""
    url: str
    analysis_type: str = "full"
    custom_prompt: Optional[str] = None
    session_id: Optional[str] = None

class YouTubeAnalysisRequest(BaseModel):
    """YouTube analysis request model"""
    url: str
    analysis_type: str = "full"
    custom_prompt: Optional[str] = None
    session_id: Optional[str] = None

# Web Analysis Response Models
class WebCurriculumCheck(BaseModel):
    """Web curriculum compliance check result"""
    is_educational: bool = Field(description="Whether content is educational")
    yks_relevant: bool = Field(description="Whether content is YKS relevant")
    subjects: List[str] = Field(description="Related YKS subjects")
    education_level: str = Field(description="Education level")
    confidence_score: float = Field(description="Confidence score", ge=0, le=1)
    reason: str = Field(description="Evaluation reason")

class WebAnalysisResult(BaseModel):
    """Web analysis result model"""
    success: bool = Field(description="Whether analysis was successful")
    url: str = Field(description="Analyzed URL")
    content_info: Dict[str, Any] = Field(description="Content information")
    curriculum_check: WebCurriculumCheck = Field(description="Curriculum compliance check")
    educational_analysis: str = Field(description="Educational analysis text")
    structured_data: Dict[str, Any] = Field(description="Structured analysis data")
    generated_questions: List[Dict[str, Any]] = Field(description="Generated questions")
    study_materials: Dict[str, Any] = Field(description="Study materials")
    processing_time: float = Field(description="Processing time in seconds")