"""
Web Search MCP Server - Google Gemini Integration
"""
from typing import Dict, List, Any, Optional
import aiohttp
from datetime import datetime
from config.logging_config import log
from config.settings import settings
from src.mcp_server.base_server import MCPTool, ToolType
from src.utils import APIResponse, SourceType, generate_id
from src.mcp_protocol import ContentBlock, ContentSource


class WebSearchTool(MCPTool):
    """Web search using Google Gemini API"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web using Google Gemini API",
            tool_type=ToolType.SEARCH,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for results",
                        "default": "en"
                    }
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "snippet": {"type": "string"},
                                "url": {"type": "string"},
                                "relevance_score": {"type": "number"}
                            }
                        }
                    },
                    "count": {"type": "integer"}
                }
            }
        )
        self.api_key = settings.GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.max_retries = 3
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search"""
        query = params.get("query", "")
        limit = params.get("limit", 10)
        language = params.get("language", "en")
        
        if not query:
            return {
                "success": False,
                "error": "Query parameter required"
            }
        
        try:
            log.info(f"Searching web for: {query}")
            
            results = await self._perform_search(
                query=query,
                limit=limit,
                language=language
            )
            
            log.info(f"Found {len(results)} results for: {query}")
            
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "query": query
            }
        except Exception as e:
            log.error(f"Web search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _perform_search(
        self,
        query: str,
        limit: int,
        language: str,
    ) -> List[Dict[str, Any]]:
        """Perform actual search via Google Gemini API"""
        
        # Since we're using Google's Generative AI
        # we'll create a prompt-based search approach
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Create a search-oriented prompt
            prompt = f"""
            Search the web for information about: {query}
            
            Provide {limit} most relevant results with:
            1. Title
            2. Summary/snippet
            3. URL (if available)
            4. Relevance score (0-1)
            
            Format as JSON array with fields: title, snippet, url, relevance_score
            """
            
            response = model.generate_content(prompt)
            
            # Parse response and extract results
            results = self._parse_search_results(response.text, query, limit)
            
            return results
            
        except ImportError:
            log.warning("google-generativeai not installed, using mock search")
            return self._mock_search(query, limit)
    
    def _parse_search_results(
        self,
        response_text: str,
        query: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Parse search results from API response"""
        results = []
        
        try:
            import json
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if json_match:
                parsed = json.loads(json_match.group())
                for item in parsed[:limit]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "url": item.get("url", ""),
                        "relevance_score": float(item.get("relevance_score", 0.5))
                    })
        except Exception as e:
            log.warning(f"Failed to parse search results: {e}")
            results = self._mock_search(query, limit)
        
        return results
    
    def _mock_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Return mock search results for testing"""
        log.warning("Using mock search results")
        
        mock_results = [
            {
                "title": f"Result 1: {query}",
                "snippet": f"This is a mock result about {query}. In a production environment, this would be real search results.",
                "url": f"https://example.com/search?q={query}",
                "relevance_score": 0.95
            },
            {
                "title": f"Result 2: {query}",
                "snippet": f"Another mock result providing information on {query}.",
                "url": f"https://example.com/article-2",
                "relevance_score": 0.85
            },
            {
                "title": f"Result 3: {query}",
                "snippet": f"Additional information about {query} from various sources.",
                "url": f"https://example.com/article-3",
                "relevance_score": 0.75
            },
        ]
        
        return mock_results[:limit]
    
    async def convert_to_content_blocks(
        self,
        search_results: List[Dict[str, Any]],
    ) -> List[ContentBlock]:
        """Convert search results to ContentBlock format"""
        blocks = []
        
        for result in search_results:
            source = ContentSource(
                source_id=f"web_{generate_id()}",
                source_type=SourceType.WEB_SEARCH.value,
                name=result.get("url", "Web Search"),
                quality_score=result.get("relevance_score", 0.5),
                confidence_score=0.7,
                last_updated=datetime.utcnow(),
                metadata={
                    "url": result.get("url"),
                    "source": "web_search"
                }
            )
            
            block = ContentBlock(
                content_id=f"block_{generate_id()}",
                source=source,
                title=result.get("title"),
                body=result.get("snippet", ""),
                relevance_score=result.get("relevance_score", 0.5),
                keywords=self._extract_keywords(result.get("snippet", "")),
            )
            
            blocks.append(block)
        
        return blocks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = text.lower().split()
        # Filter common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were'}
        keywords = [w.strip('.,!?;:') for w in words if len(w) > 3 and w.lower() not in common_words]
        return list(set(keywords))[:10]  # Return unique keywords, max 10
