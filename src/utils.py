"""
Core utilities and helper functions
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import hashlib
import uuid


class SourceType(str, Enum):
    """Types of content sources"""
    MEMORY = "memory"
    WEB_SEARCH = "web_search"
    API = "api"
    EXTERNAL = "external"
    USER_UPLOADED = "user_uploaded"


class ContentQuality(str, Enum):
    """Content quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def generate_id(prefix: str = "") -> str:
    """Generate unique ID"""
    unique_id = str(uuid.uuid4()).replace("-", "")
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_hash(content: str) -> str:
    """Generate SHA256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.utcnow()


class ContentMetadata:
    """Metadata container for content"""
    
    def __init__(
        self,
        source: SourceType,
        quality: ContentQuality = ContentQuality.MEDIUM,
        confidence: float = 0.5,
        relevance_score: float = 0.0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.source = source
        self.quality = quality
        self.confidence = confidence
        self.relevance_score = relevance_score
        self.created_at = created_at or get_current_timestamp()
        self.updated_at = updated_at or get_current_timestamp()
        self.tags = tags or []
        self.custom_metadata = custom_metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "source": self.source.value,
            "quality": self.quality.value,
            "confidence": self.confidence,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "custom_metadata": self.custom_metadata,
        }


class APIResponse:
    """Standardized API response format"""
    
    def __init__(
        self,
        success: bool,
        data: Any = None,
        message: str = "",
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.data = data
        self.message = message
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = get_current_timestamp().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class MCPException(Exception):
    """Base exception for MCP errors"""
    
    def __init__(self, message: str, code: str = "MCP_ERROR", details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class DocumentProcessingError(MCPException):
    """Raised when document processing fails"""
    pass


class ContentRoutingError(MCPException):
    """Raised when content routing fails"""
    pass


class VectorDatabaseError(MCPException):
    """Raised when vector database operations fail"""
    pass


class TaskExecutionError(MCPException):
    """Raised when task execution fails"""
    pass
