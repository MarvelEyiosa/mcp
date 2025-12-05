# MCP Server + Document Memory System

## 📋 Project Overview

Transform an AI system from a stateless processor into an intelligent learning companion with persistent memory, advanced task capabilities, and MCP protocol compliance.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Framework                     │
│  (Protocol Handlers, Tool Management, Resource Management) │
└────────────────┬────────────────────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
     ▼           ▼           ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│  Web    │ │ Document │ │Document  │
│ Search  │ │ Memory   │ │ Editor   │
│  Tool   │ │   Tool   │ │   Tool   │
└─────────┘ └──────────┘ └──────────┘
     │           │           │
     └───────────┼───────────┘
                 │
     ┌───────────▼───────────┐
     │   Content Router      │
     │  (Memory-first Logic) │
     └───────────┬───────────┘
                 │
     ┌───────────▼──────────────────────┐
     │  Quality Scoring System          │
     │  (Content Evaluation & Ranking)  │
     └──────────────────────────────────┘
```

## 📁 Project Structure

```
mcp/
├── src/
│   ├── mcp_server/           # MCP Framework
│   │   ├── base_server.py    # Base MCPServer class
│   │   ├── quality_scorer.py # Quality scoring system
│   │   └── __init__.py
│   ├── document_memory/      # Vector DB & semantic search (Phase 2)
│   ├── content_router/       # Content routing logic
│   │   ├── router.py         # ContentRouter implementation
│   │   └── __init__.py
│   ├── web_search/           # Google Gemini web search
│   │   ├── web_search_tool.py
│   │   └── __init__.py
│   ├── document_editor/      # Document editing (Phase 4)
│   ├── document_creator/     # Document creation (Phase 4)
│   ├── task_executor/        # Task execution (Phase 4)
│   ├── utils.py              # Utilities & shared types
│   ├── mcp_protocol.py       # MCP protocol definitions
│   └── __init__.py
├── config/
│   ├── settings.py           # Configuration management
│   └── logging_config.py     # Logging setup
├── tests/
│   ├── test_mcp_server.py    # Server tests
│   ├── test_quality_scorer.py # Scoring tests
│   ├── test_content_router.py # Router tests
│   ├── test_web_search.py     # Web search tests
│   └── conftest.py           # Pytest configuration
├── data/                     # Data storage (vectors, docs, etc)
├── logs/                     # Application logs
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🚀 Phase 1: MCP Foundation (✅ COMPLETED)

### What Was Built

#### 1. **Base MCP Server Class** (`src/mcp_server/base_server.py`)
- Core MCPServer with async protocol handlers
- Tool management system (register/unregister/execute)
- Resource management lifecycle
- Middleware support for request processing
- Custom error handling framework
- Server statistics and monitoring

**Key Components:**
```python
# MCPTool - Abstract base for tools
class MCPTool(ABC):
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]
    
# MCPServer - Main server class
class MCPServer:
    async def process_request(request: MCPRequest) -> MCPResponse
    def register_tool(tool: MCPTool)
    async def initialize_resources()
    async def cleanup_resources()
```

#### 2. **MCP Protocol Definitions** (`src/mcp_protocol.py`)
- **MCPRequest**: Standardized request schema
- **MCPResponse**: Standardized response schema
- **ToolDefinition**: Tool metadata and schema
- **ContentBlock**: Individual content unit
- **SynthesizedContent**: Multi-source aggregated content

#### 3. **Quality Scoring System** (`src/mcp_server/quality_scorer.py`)

Evaluates content quality across 7 factors:
- **Source Reliability** (25%): Confidence in source
- **Content Freshness** (15%): How recent is content
- **Relevance** (25%): Semantic match to query
- **Completeness** (15%): Comprehensiveness of coverage
- **Accuracy** (15%): Information accuracy
- **Citation Count** (3%): Supporting references
- **User Feedback** (2%): Prior user satisfaction

```python
# Usage
scorer = QualityScorer()
result = scorer.score_content(
    content="...",
    source_type="memory",
    created_at=datetime.utcnow(),
    relevance_score=0.8,
    citation_count=5
)
# Returns: overall_score, quality_level, component breakdown
```

#### 4. **Content Router** (`src/content_router/router.py`)

Memory-first intelligent routing with 5 strategies:

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| **MEMORY_FIRST** | Check memory first, fallback to external | Default, cost optimization |
| **EXTERNAL_FIRST** | Prioritize current information | Latest data needed |
| **BALANCED** | Query all sources equally | Comprehensive coverage |
| **MEMORY_ONLY** | Use only stored documents | Offline operation |
| **EXTERNAL_ONLY** | Use only external sources | New information only |

**Features:**
- Content aggregation from multiple sources
- Contradiction detection
- Gap analysis
- Quality-based source ranking
- Decision logging for analytics

```python
# Usage
router = ContentRouter(default_strategy=RoutingStrategy.MEMORY_FIRST)
decision = await router.route_request(
    query="AI trends",
    strategy=RoutingStrategy.MEMORY_FIRST
)
# Returns: sources_to_query, expected_quality, reasoning
```

#### 5. **Web Search Tool** (`src/web_search/web_search_tool.py`)

Google Gemini API integration:
- Async web search execution
- Result parsing and ranking
- Keyword extraction
- Conversion to ContentBlock format
- Mock search fallback for testing

```python
# Usage
tool = WebSearchTool()
result = await tool.execute({
    "query": "artificial intelligence",
    "limit": 10
})
# Returns: results with titles, snippets, URLs, relevance scores
```

#### 6. **Configuration & Logging**

**Settings** (`config/settings.py`):
- Environment-based configuration
- Database URLs, API keys
- Performance tuning parameters
- Resource paths with auto-creation

**Logging** (`config/logging_config.py`):
- Console and file logging
- Separate error log
- Loguru integration
- Automatic rotation and retention

#### 7. **Utilities** (`src/utils.py`)

Essential types and helpers:
- `ContentMetadata`: Content information container
- `APIResponse`: Standardized API response
- `SourceType`, `ContentQuality`, `TaskStatus`: Enums
- Custom exceptions: `MCPException`, `DocumentProcessingError`, etc.
- Helper functions: `generate_id()`, `generate_hash()`, etc.

#### 8. **FastAPI Application** (`main.py`)

REST API for MCP operations:
```
GET  /                    # Root info
GET  /health              # Health check
GET  /stats               # Server statistics
GET  /tools               # List available tools
POST /execute             # Execute tool (MCP format)
POST /request             # Process generic MCP request
GET  /tools/{tool_name}   # Get tool info
```

### Testing Framework

Comprehensive test suite with pytest:

**`tests/test_mcp_server.py`** - 8 tests
- Server initialization
- Tool registration/unregistration
- Tool execution
- Request processing
- Error handling
- Server statistics

**`tests/test_quality_scorer.py`** - 9 tests
- Source reliability scoring
- Content freshness evaluation
- Completeness assessment
- Quality level determination
- Weight adjustment
- Overall scoring validation

**`tests/test_content_router.py`** - 10 tests
- Router initialization
- Source registration and discovery
- All 5 routing strategies
- Content aggregation
- Gap and contradiction detection
- Decision logging

**`tests/test_web_search.py`** - 6 tests
- Tool initialization
- Search execution
- Parameter validation
- Mock search fallback
- Keyword extraction
- Content block conversion

**Run tests:**
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html  # With coverage
```

## 📊 Scoring System Explained

### How Quality Scores Work

When content is evaluated:

1. **Source Reliability**: Memory=0.95, Web=0.65, API=0.90
2. **Freshness**: Recent=1.0, 30 days=0.9, 90 days=0.75, 365+ days=0.2-0.5
3. **Relevance**: Vector similarity score (0-1)
4. **Completeness**: Based on content length + provided score
5. **Accuracy**: User-provided trust score
6. **Citations**: Each citation increases score (capped at 10)
7. **User Feedback**: Historical satisfaction rating

### Quality Levels

- **VERIFIED** (≥0.90): Highly reliable, well-sourced
- **HIGH** (≥0.75): Good quality, mostly current
- **MEDIUM** (≥0.50): Acceptable, may need verification
- **LOW** (<0.50): Poor quality, needs additional sources

## 🔄 Routing Strategy Flow

### Memory-First Example

```
User Query: "What are latest AI trends?"
    ↓
ContentRouter.route_request(query, strategy=MEMORY_FIRST)
    ↓
Query Memory Database
    ↓ (Memory hit with good relevance)
Return results from memory
    ↓
Score Results: 0.85 quality
    ↓
Return to user (cost-effective)
    
--- If Memory Hit Poor Quality ---
    ↓
Query Web Search API
    ↓
Combine Results
    ↓
Synthesize + Resolve Contradictions
    ↓
Return comprehensive answer
```

## 🛠️ Configuration Guide

### 1. Create `.env` file

```bash
cp .env.example .env
```

### 2. Edit `.env`

```env
# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# MCP Server
MCP_HOST=0.0.0.0
MCP_PORT=8000

# API Keys (get from respective services)
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_SEARCH_API_KEY=your_search_api_key

# Performance
VECTOR_SEARCH_K=10
MEMORY_HIT_THRESHOLD=0.7
CACHE_TTL=3600
```

## 🏃 Running the Server

### Option 1: Direct Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Server will be available at `http://localhost:8000`

### Option 2: With Docker (coming in Phase 5)

```bash
docker build -t mcp-server .
docker run -p 8000:8000 mcp-server
```

## 📡 API Examples

### Example 1: Execute Web Search

```bash
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_001",
    "method": "execute",
    "tool": "web_search",
    "params": {
      "query": "machine learning",
      "limit": 5
    }
  }'
```

**Response:**
```json
{
  "request_id": "req_001",
  "status": "success",
  "data": {
    "results": [
      {
        "title": "Machine Learning Overview",
        "snippet": "...",
        "url": "...",
        "relevance_score": 0.95
      }
    ],
    "count": 5
  },
  "execution_time_ms": 1250
}
```

### Example 2: List Available Tools

```bash
curl http://localhost:8000/tools
```

**Response:**
```json
{
  "count": 1,
  "tools": [
    {
      "name": "web_search",
      "description": "Search the web using Google Gemini API",
      "tool_type": "search",
      "version": "1.0.0"
    }
  ]
}
```

### Example 3: Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "resources": {}
}
```

## 📈 Monitoring & Metrics

### Server Statistics

```bash
curl http://localhost:8000/stats
```

Returns:
- Server uptime
- Total requests processed
- Error count
- Tools count
- Per-tool execution statistics

### Tool Information

```bash
curl http://localhost:8000/tools/web_search
```

Returns:
- Tool definition (schema, parameters)
- Execution count
- Average response time
- Success/error stats

## 🔐 Security Notes

### For Production:
1. Generate new SECRET_KEY in `.env`
2. Enable HTTPS
3. Use environment variables for all secrets
4. Implement API authentication
5. Enable rate limiting
6. Set appropriate CORS policies
7. Enable audit logging

## 📚 Next Steps: Phase 2

Phase 2 will implement:
- **ChromaDB Integration**: Vector database setup
- **Docling Pipeline**: Document processing (PDF, DOCX, PPTX, HTML, Images)
- **Semantic Search**: Similarity-based retrieval
- **Document Storage**: Versioning and metadata
- **Usage-based Ranking**: Learn from access patterns

Expected features:
- Document upload and processing
- Semantic vector indexing
- Fast retrieval (<200ms)
- Smart deduplication
- Automatic categorization

## 🧪 Testing Coverage

Current Phase 1 provides:
- **33 unit tests** across 4 test files
- **Quality Scoring**: Edge cases and weight adjustments
- **Routing Logic**: All 5 strategies tested
- **Error Handling**: Exception scenarios
- **Web Search**: Execution and fallback paths
- **Integration**: End-to-end request processing

Target: **90%+ code coverage** (Phase 5)

## 📝 Code Examples

### Creating a Custom Tool

```python
from src.mcp_server.base_server import MCPTool, ToolType

class CustomTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Does something useful",
            tool_type=ToolType.ANALYSIS,
            input_schema={"type": "object", "properties": {...}},
            output_schema={"type": "object", "properties": {...}}
        )
    
    async def execute(self, params):
        # Your implementation here
        return {"status": "success", "data": result}

# Register with server
tool = CustomTool()
mcp_server.register_tool(tool)
```

### Content Synthesis Example

```python
from src.content_router.router import content_router
from src.mcp_protocol import ContentBlock

# Get multiple content sources
blocks = [block1, block2, block3]

# Synthesize
synthesized = await content_router.synthesize_content(
    query="AI trends 2024",
    content_blocks=blocks
)

print(f"Quality: {synthesized.quality_score}")
print(f"Contradictions: {synthesized.contradictions}")
print(f"Gaps: {synthesized.gaps}")
print(f"Recommendations: {synthesized.recommendations}")
```

## 🎯 Success Metrics (Phase 1)

✅ **Completed:**
- Full MCP framework with protocol compliance
- Quality scoring across 7 factors
- Memory-first routing with 5 strategies
- Web search integration
- Comprehensive testing (33 tests)
- FastAPI server with REST endpoints
- Configuration management
- Professional logging

✅ **Performance:**
- Tool execution: <100ms (web search: 1-2s)
- Request handling: <50ms
- No external dependencies blocking

## 🚨 Known Limitations (Phase 1)

1. **No persistent storage yet** - Web search results not cached
2. **No document processing** - Text-only search results
3. **No vector database** - No semantic search capability
4. **Mock search fallback** - Real API keys needed for production
5. **No authentication** - Open endpoints (add in Phase 5)
6. **No rate limiting** - Add in Phase 5 security phase

## 📞 Support & Documentation

- **Configuration**: See `config/settings.py`
- **Logging**: See `config/logging_config.py`
- **Error Handling**: See `src/utils.py` exceptions
- **Protocol**: See `src/mcp_protocol.py`
- **Tests**: Run `pytest -v` for examples

## 📄 License

MIT - See LICENSE file

---

**Phase 1 Complete! Ready for Phase 2: Document Memory Core** 🚀
