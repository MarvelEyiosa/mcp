"""
MCP Protocol core definitions and schemas
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ToolType(str, Enum):
    """Types of MCP tools"""
    TEXT_PROCESSING = "text_processing"
    DOCUMENT_OPERATION = "document_operation"
    SEARCH = "search"
    ANALYSIS = "analysis"
    CREATION = "creation"


class MCPRequest(BaseModel):
    """Standard MCP Request schema"""
    request_id: str = Field(..., description="Unique request identifier")
    method: str = Field(..., description="Method name")
    tool: str = Field(..., description="Tool identifier")
    params: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Request context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_123456",
                "method": "execute",
                "tool": "document_memory.search",
                "params": {"query": "AI trends", "limit": 10},
                "context": {"user_id": "user_123", "session_id": "sess_456"}
            }
        }


class MCPResponse(BaseModel):
    """Standard MCP Response schema"""
    request_id: str = Field(..., description="Original request identifier")
    status: str = Field(..., description="Response status: success, error, partial")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error details if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: float = Field(default=0, description="Execution time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_123456",
                "status": "success",
                "data": {
                    "results": [
                        {"id": "doc_1", "title": "AI Trends 2024", "score": 0.95}
                    ],
                    "count": 1
                },
                "metadata": {"source": "memory", "processing_time": 150}
            }
        }


class ToolDefinition(BaseModel):
    """Tool definition for MCP server"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    tool_type: ToolType = Field(..., description="Type of tool")
    input_schema: Dict[str, Any] = Field(..., description="Input parameters schema")
    output_schema: Dict[str, Any] = Field(..., description="Output schema")
    required_permissions: List[str] = Field(default_factory=list, description="Required permissions")
    version: str = Field(default="1.0.0", description="Tool version")


class ContentSource(BaseModel):
    """Content source information"""
    source_id: str = Field(..., description="Unique source identifier")
    source_type: str = Field(..., description="Type of source")
    name: str = Field(..., description="Source name")
    quality_score: float = Field(..., ge=0, le=1, description="Quality score 0-1")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    last_updated: datetime = Field(..., description="Last update time")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentBlock(BaseModel):
    """Single block of content"""
    content_id: str = Field(..., description="Unique content identifier")
    source: ContentSource = Field(..., description="Content source")
    title: Optional[str] = Field(default=None, description="Content title")
    body: str = Field(..., description="Content body")
    summary: Optional[str] = Field(default=None, description="Content summary")
    keywords: List[str] = Field(default_factory=list, description="Keywords/tags")
    relevance_score: float = Field(default=0.5, ge=0, le=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SynthesizedContent(BaseModel):
    """Synthesized content from multiple sources"""
    synthesis_id: str = Field(..., description="Unique synthesis identifier")
    query: str = Field(..., description="Original query")
    aggregated_content: str = Field(..., description="Aggregated content from all sources")
    sources: List[ContentSource] = Field(..., description="List of sources used")
    quality_score: float = Field(ge=0, le=1, description="Overall quality score")
    contradictions: List[Dict[str, Any]] = Field(default_factory=list, description="Identified contradictions")
    gaps: List[str] = Field(default_factory=list, description="Identified gaps in content")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
