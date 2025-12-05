# 🧠 MCP Server + Document Memory System

> Transform your AI from stateless to intelligent with persistent memory, semantic search, and advanced task capabilities.

## 🎯 Mission

Build a production-ready MCP Server that enables an AI system to:
- ✅ **Remember** all user interactions and documents
- ✅ **Understand** document context and meaning
- ✅ **Route** requests intelligently (memory-first strategy)
- ✅ **Synthesize** content from multiple sources
- ✅ **Edit** documents based on user feedback
- ✅ **Create** new documents from requirements
- ✅ **Execute** complex multi-step tasks
- ✅ **Learn** from every interaction

## 📊 Project Status

**Phase 1: MCP Foundation** ✅ COMPLETE
- Base MCP Server framework
- Quality scoring system (7 factors)
- Content router (5 strategies)
- Web search integration
- 33 unit tests (all passing)
- Comprehensive documentation

**Phase 2-5: In Progress** (Starting soon)
- Document memory & vector DB
- Semantic search
- Document editing/creation
- Advanced task execution
- Testing & deployment

## 🚀 Quick Start (5 minutes)

### 1. Clone & Install
```bash
cd "c:\Users\DELL CORE i5\New folder\mcp"
pip install -r requirements.txt
```

### 2. Configure
```bash
copy .env.example .env
# Add your API keys to .env
```

### 3. Run
```bash
python main.py
```

### 4. Test
```bash
curl http://localhost:8000/health
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** | 5-minute setup & common tasks |
| **[PHASE1_DOCUMENTATION.md](PHASE1_DOCUMENTATION.md)** | Complete Phase 1 details |
| **[ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)** | How everything works |

## 📁 Key Components

### Core Framework
- **MCP Server** (`src/mcp_server/base_server.py`): Protocol handler, tool management, resource lifecycle
- **Quality Scorer** (`src/mcp_server/quality_scorer.py`): 7-factor content evaluation
- **Content Router** (`src/content_router/router.py`): Intelligent source selection
- **Web Search Tool** (`src/web_search/web_search_tool.py`): Google Gemini integration

### Infrastructure  
- **Configuration** (`config/settings.py`): Environment-based config
- **Logging** (`config/logging_config.py`): Structured logging
- **Protocols** (`src/mcp_protocol.py`): Request/response schemas
- **Utilities** (`src/utils.py`): Shared types & helpers

### Testing (33 tests)
- `tests/test_mcp_server.py` - Server functionality
- `tests/test_quality_scorer.py` - Scoring system
- `tests/test_content_router.py` - Routing logic
- `tests/test_web_search.py` - Web search tool\

## 🎯 Key Features

### ✅ Phase 1: MCP Foundation

**Base MCP Server**
- Async request/response handling
- Tool registration and discovery
- Middleware support
- Custom error handling
- Resource management lifecycle

**Quality Scoring (7 Factors)**
- Source reliability (25%)
- Content freshness (15%)
- Relevance (25%)
- Completeness (15%)
- Accuracy (15%)
- Citation count (3%)
- User feedback (2%)

**Content Router (5 Strategies)**
- MEMORY_FIRST: Check cache first (default)
- EXTERNAL_FIRST: Get latest info
- BALANCED: Comprehensive coverage
- MEMORY_ONLY: Offline mode
- EXTERNAL_ONLY: Fresh data only

**Web Search Integration**
- Google Gemini API
- Async execution
- Result ranking
- Mock fallback for testing

### ⏳ Phase 2-5: Advanced Features

**Phase 2: Document Memory**
- Vector database (ChromaDB + FAISS)
- Document processing (PDF, DOCX, PPTX, HTML, Images)
- Semantic search
- Usage-based optimization

**Phase 3: Memory Integration**
- Document Memory MCP Server
- Memory-first routing
- Content synthesis
- Performance analytics

**Phase 4: Advanced Features**
- Document Editor (edit/version control)
- Document Creator (generation from requirements)
- Task Executor (complex operations)
- Feedback integration

**Phase 5: Production Ready**
- Comprehensive testing (90%+ coverage)
- Performance optimization
- Security hardening
- Docker deployment
- Kubernetes configuration

## 💻 API Examples

### Web Search
```bash
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{
	"request_id": "req_001",
	"method": "execute",
	"tool": "web_search",
	"params": {"query": "AI trends", "limit": 5}
  }'
```

### List Tools
```bash
curl http://localhost:8000/tools
```

### Server Health
```bash
curl http://localhost:8000/health
```

### Statistics
```bash
curl http://localhost:8000/stats
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_quality_scorer.py -v

# Run single test
pytest tests/test_mcp_server.py::test_server_initialization -v
```

**Current Status**: 33/33 tests passing ✅

## 📋 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Memory hit rate | >60% | Phase 2+ |
| Response time (memory) | <200ms | Phase 2+ |
| Response time (web) | <2s | ✅ |
| API cost reduction | >50% | Phase 3+ |
| Test coverage | >90% | Phase 5 |
| Document processing accuracy | >95% | Phase 2+ |
| Task completion success | >90% | Phase 4+ |

## 🔧 Configuration

Key settings in `.env`:

```env
# Server
ENVIRONMENT=development
MCP_HOST=0.0.0.0
MCP_PORT=8000

# API Keys
GOOGLE_API_KEY=your_key_here

# Performance
VECTOR_SEARCH_K=10
MEMORY_HIT_THRESHOLD=0.7
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
DEBUG=True
```

## 📚 Learning Path

1. **Read**: [QUICKSTART.md](QUICKSTART.md) - 10 min
2. **Run**: `python main.py` - 5 min
3. **Test**: `pytest tests/ -v` - 5 min
4. **Explore**: [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - 20 min
5. **Code**: Review `src/mcp_server/base_server.py` - 30 min
6. **Extend**: Add custom tool - 30 min

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         REST API (FastAPI)                      │
│  GET / POST /health /stats /tools /request     │
└────────────────┬────────────────────────────────┘
				 │
		 ┌───────▼────────┐
		 │  MCP Protocol  │
		 │   Processor    │
		 └───────┬────────┘
				 │
	┌────────────┼────────────┐
	│            │            │
	▼            ▼            ▼
┌────────┐  ┌──────────┐  ┌──────────┐
│  Web   │  │ Quality  │  │ Content  │
│ Search │  │ Scorer   │  │ Router   │
│  Tool  │  │  (7x)    │  │(5 modes) │
└────────┘  └──────────┘  └──────────┘
	│            │            │
	└────────────┼────────────┘
				 │
	┌────────────▼────────────┐
	│  Storage Layer (Phase 2+)
	│  - ChromaDB (vectors)
	│  - PostgreSQL (metadata)
	│  - Redis (cache)
	└─────────────────────────┘
```

## 🚨 Known Limitations (Phase 1)

- No persistent storage (added in Phase 2)
- No document processing (added in Phase 2)
- No vector database (added in Phase 2)
- No semantic search (added in Phase 2)
- Mock search fallback (real API key needed)
- No authentication (added in Phase 5)

## 📝 Implementation Timeline

| Phase | Duration | Focus | Status |
|-------|----------|-------|--------|
| 1 | 1-2 weeks | Foundation | ✅ Complete |
| 2 | 2-3 weeks | Memory & Vectors | ⏳ Next |
| 3 | 1-2 weeks | Integration | 📋 Planned |
| 4 | 2-3 weeks | Advanced Features | 📋 Planned |
| 5 | 2-3 weeks | Testing & Deploy | 📋 Planned |

## 🎓 Code Examples

### Creating a Custom Tool

```python
from src.mcp_server import MCPTool, ToolType

class MyTool(MCPTool):
	async def execute(self, params):
		# Your code here
		return {"result": "success"}

# Register and use
mcp_server.register_tool(MyTool(...))
```

### Using Quality Scorer

```python
from src.mcp_server import quality_scorer

score = quality_scorer.score_content(
	content="...",
	source_type="memory",
	created_at=datetime.utcnow(),
	relevance_score=0.8
)
# Returns: overall_score, quality_level, components
```

### Content Routing

```python
from src.content_router import content_router, RoutingStrategy

decision = await content_router.route_request(
	query="AI trends",
	strategy=RoutingStrategy.MEMORY_FIRST
)
# Returns: sources_to_query, expected_quality, reasoning
```

## 📞 Support

- **Quick Questions**: See [QUICKSTART.md](QUICKSTART.md)
- **How It Works**: See [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)
- **Detailed Docs**: See [PHASE1_DOCUMENTATION.md](PHASE1_DOCUMENTATION.md)
- **Tests**: Run `pytest tests/ -v` for examples
- **Logs**: Check `logs/app.log` for troubleshooting

## 🎯 Next Steps

1. Install and run the server
2. Run test suite (`pytest tests/ -v`)
3. Try API examples (see QUICKSTART.md)
4. Read architecture guide
5. Extend with custom tools
6. **Phase 2**: Add document memory & vectors

## 📄 License

MIT - See LICENSE file (to be added)

## 👥 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

---

**Built with Python 3.11+, FastAPI, ChromaDB, Docling**

**Phase 1 Complete! Ready for Phase 2: Document Memory** 🚀
# mcp