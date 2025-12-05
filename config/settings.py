"""
Central configuration management for MCP Server System
"""
import os
from typing import List
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Settings:
    """Application settings with environment variable support"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # MCP Server
    MCP_HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mcp.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Vector Database
    CHROMADB_PATH: str = os.getenv("CHROMADB_PATH", str(DATA_DIR / "chromadb"))
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", str(DATA_DIR / "faiss"))
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_SEARCH_API_KEY: str = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    
    # Document Processing
    MAX_DOCUMENT_SIZE: int = int(os.getenv("MAX_DOCUMENT_SIZE", "50000000"))
    SUPPORTED_FORMATS: List[str] = os.getenv(
        "SUPPORTED_FORMATS", 
        "pdf,docx,pptx,html,txt,md"
    ).split(",")
    
    # Performance
    VECTOR_SEARCH_K: int = int(os.getenv("VECTOR_SEARCH_K", "10"))
    MEMORY_HIT_THRESHOLD: float = float(os.getenv("MEMORY_HIT_THRESHOLD", "0.7"))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    
    # Task Processing
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    
    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_chromadb_path(cls) -> str:
        """Get ChromaDB path"""
        path = Path(cls.CHROMADB_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    @classmethod
    def get_faiss_path(cls) -> str:
        """Get FAISS index path"""
        path = Path(cls.FAISS_INDEX_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)


# Create settings instance
settings = Settings()
