import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Google Gemini Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Gemini 2.5 Models
    GEMINI_PRO_MODEL: str = "gemini-2.5-pro"  # Most powerful reasoning model
    GEMINI_FLASH_MODEL: str = "gemini-2.5-flash"  # Multi-modal with next-gen capabilities  
    GEMINI_FLASH_LITE_MODEL: str = "gemini-2.5-flash-lite"  # Fastest and most cost-effective
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    
    # Backward compatibility
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_THINKING_MODEL: str = "gemini-2.5-pro"
    
    # Application Settings
    APP_NAME: str = "Promptitron AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database Configuration  
    DATABASE_URL: str = "sqlite:///./promptitron.db"
    REDIS_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # ChromaDB Settings
    CHROMA_PERSIST_DIR: str = "chroma_db"
    CHROMA_COLLECTION_NAME: str = "yks_documents"
    
    # Content Settings
    JSON_DIR: str = "data/jsonn/yks"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Model Configuration
    TEMPERATURE: float = 0.7
    MAX_OUTPUT_TOKENS: int = 8192  # Increased for longer responses
    TOP_P: float = 0.95
    TOP_K: int = 40
    
    # Function Calling Configuration
    FUNCTION_CALLING_MODE: str = "AUTO"  # AUTO, ANY, NONE
    MAX_FUNCTION_CALLS: int = 10
    
    # Embedding Configuration
    EMBEDDING_DIMENSIONS: int = 768  # 128-3072 (recommended: 768, 1536, 3072)
    EMBEDDING_TASK_TYPE: str = "SEMANTIC_SIMILARITY"
    
    # Safety Settings (CIVIC_INTEGRITY not available in current API version)
    SAFETY_FILTER_HARASSMENT: str = "BLOCK_MEDIUM_AND_ABOVE"
    SAFETY_FILTER_HATE_SPEECH: str = "BLOCK_MEDIUM_AND_ABOVE" 
    SAFETY_FILTER_SEXUALLY_EXPLICIT: str = "BLOCK_MEDIUM_AND_ABOVE"
    SAFETY_FILTER_DANGEROUS_CONTENT: str = "BLOCK_MEDIUM_AND_ABOVE"
    # SAFETY_FILTER_CIVIC_INTEGRITY: str = "BLOCK_MEDIUM_AND_ABOVE"  # Not available
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()