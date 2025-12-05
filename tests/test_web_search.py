"""
Tests for Web Search Tool
"""
import pytest
from src.web_search.web_search_tool import WebSearchTool
from src.mcp_server.base_server import ToolType


class TestWebSearchTool:
    """Test web search tool functionality"""
    
    @pytest.fixture
    def tool(self):
        """Create test web search tool"""
        return WebSearchTool()
    
    def test_tool_initialization(self, tool):
        """Test tool initializes correctly"""
        assert tool.name == "web_search"
        assert tool.tool_type == ToolType.SEARCH
        assert "query" in tool.input_schema["properties"]
    
    @pytest.mark.asyncio
    async def test_search_execution(self, tool):
        """Test search execution"""
        result = await tool.execute({
            "query": "artificial intelligence",
            "limit": 5
        })
        
        assert "success" in result
        assert "results" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_search_with_missing_query(self, tool):
        """Test search with missing query parameter"""
        result = await tool.execute({
            "limit": 5
        })
        
        assert result["success"] == False
        assert "error" in result
    
    def test_mock_search(self, tool):
        """Test mock search fallback"""
        results = tool._mock_search("test query", 3)
        
        assert len(results) <= 3
        assert all("title" in r for r in results)
        assert all("snippet" in r for r in results)
        assert all("url" in r for r in results)
        assert all("relevance_score" in r for r in results)
    
    def test_keyword_extraction(self, tool):
        """Test keyword extraction"""
        text = "Artificial intelligence is a field of computer science"
        keywords = tool._extract_keywords(text)
        
        assert len(keywords) > 0
        assert all(len(k) > 3 for k in keywords)
    
    @pytest.mark.asyncio
    async def test_convert_to_content_blocks(self, tool):
        """Test converting search results to content blocks"""
        results = [
            {
                "title": "Test Article",
                "snippet": "This is a test article about artificial intelligence",
                "url": "https://example.com/test",
                "relevance_score": 0.95
            }
        ]
        
        blocks = await tool.convert_to_content_blocks(results)
        
        assert len(blocks) == 1
        assert blocks[0].title == "Test Article"
        assert blocks[0].relevance_score == 0.95
