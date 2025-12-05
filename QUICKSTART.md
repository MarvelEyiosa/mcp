# 🚀 MCP Server + Document Memory System - Quick Start

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd "c:\Users\DELL CORE i5\New folder\mcp"
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
copy .env.example .env
# Edit .env and add your API keys
```

### Step 3: Run Server
```bash
python main.py
```

You should see:
```
Initializing MCP Server: MCP Server v1.0.0
Starting MCP Server on 0.0.0.0:8000
Application startup complete
```

### Step 4: Test It
```bash
curl http://localhost:8000/health
```

## 📋 Project Status

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | MCP Framework | ✅ Complete | 8/8 |
| 1 | Quality Scorer | ✅ Complete | 9/9 |
| 1 | Content Router | ✅ Complete | 10/10 |
| 1 | Web Search | ✅ Complete | 6/6 |
| 1 | **Total Phase 1** | **✅ Complete** | **33/33** |
| 2 | Document Memory | ⏳ In Progress | - |
| 2 | Vector Database | ⏳ Planned | - |
| 3 | Memory Integration | 📋 Planned | - |
| 4 | Advanced Features | 📋 Planned | - |
| 5 | Optimization | 📋 Planned | - |

## 📚 Key Features Implemented

### ✅ MCP Server Framework
- Async request/response handling
- Tool registration and management  
- Middleware support
- Error handling system
- Resource lifecycle management

### ✅ Quality Scoring System
- 7-factor content evaluation
- Weighted scoring
- Quality level determination
- Customizable weights
- Comprehensive scoring breakdown

### ✅ Content Router
- 5 routing strategies (memory-first, external-first, balanced, etc)
- Source registration and discovery
- Content aggregation and synthesis
- Contradiction detection
- Gap identification and recommendations

### ✅ Web Search Integration
- Google Gemini API support
- Async search execution
- Result ranking and parsing
- Keyword extraction
- Mock fallback for testing

### ✅ Testing & Monitoring
- 33 comprehensive unit tests
- Tool execution statistics
- Server health checks
- Request/response metrics
- Detailed error logging

## 🎯 What You Can Do Now

### 1. List Available Tools
```bash
curl http://localhost:8000/tools
```

### 2. Execute Web Search
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

### 3. Get Server Statistics
```bash
curl http://localhost:8000/stats
```

### 4. Run Tests
```bash
pytest tests/ -v              # Run all tests
pytest tests/ --cov=src       # With coverage
pytest tests/test_quality_scorer.py -v  # Specific test
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         REST API (FastAPI - main.py)            │
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
└────────┘  └──────────┘  └──────────┘
```

## 📁 Directory Structure

```
mcp/
├── src/
│   ├── mcp_server/          # Core framework
│   ├── content_router/      # Routing logic
│   ├── web_search/          # Search integration
│   ├── document_memory/     # Phase 2 - Vector DB
│   ├── mcp_protocol.py      # Protocol definitions
│   └── utils.py             # Shared utilities
├── config/                  # Configuration
├── tests/                   # Test suite (33 tests)
├── data/                    # Data storage
├── logs/                    # Application logs
├── main.py                  # Entry point
└── PHASE1_DOCUMENTATION.md  # Detailed docs
```

## 🔧 Configuration

Key settings in `.env`:

```env
# Server
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

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_quality_scorer.py -v

# With coverage report
pytest tests/ --cov=src --cov-report=html

# Watch mode (requires pytest-watch)
ptw tests/
```

## 📊 Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| MCP Server | 8 | ✅ |
| Quality Scorer | 9 | ✅ |
| Content Router | 10 | ✅ |
| Web Search | 6 | ✅ |
| **Total** | **33** | **✅** |

## 🚨 Troubleshooting

### Port Already In Use
```bash
# Change port in .env
MCP_PORT=8001

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### API Key Issues
```bash
# Verify key is in .env
cat .env | grep GOOGLE_API_KEY

# Make sure it's valid
python -c "from config.settings import settings; print(settings.GOOGLE_API_KEY)"
```

### Permission Errors
```bash
# Ensure data/logs directories are writable
mkdir -p data logs
chmod 755 data logs
```

## 📖 Documentation

- **Phase 1 Details**: See `PHASE1_DOCUMENTATION.md`
- **API Usage**: See main.py docstrings
- **Configuration**: See config/settings.py
- **Logging**: See config/logging_config.py
- **Tests**: See tests/ directory

## 🎓 Learning Path

1. **Understand Structure**: Read `PHASE1_DOCUMENTATION.md`
2. **Explore Code**: Start with `main.py`, then `src/mcp_server/base_server.py`
3. **Run Tests**: `pytest tests/ -v` to see all features
4. **Make API Calls**: Use curl examples above
5. **Customize**: Add your own tools by extending `MCPTool`

## 🔮 What's Coming in Phase 2

- Vector database (ChromaDB + FAISS)
- Document processing (PDF, DOCX, PPTX, HTML, Images)
- Semantic search
- Document storage and versioning
- Usage-based optimization

## 💡 Tips

### Adding a New Tool
```python
from src.mcp_server import MCPServer, MCPTool, ToolType

class MyTool(MCPTool):
    async def execute(self, params):
        # Your code here
        return {"result": "success"}

# In main.py
my_tool = MyTool(...)
mcp_server.register_tool(my_tool)
```

### Understanding Quality Scores
- Memory source: 0.95 reliability
- Web search: 0.65 reliability  
- Fresh content: 1.0 freshness
- Older content: 0.2-0.5 freshness

### Memory-First Strategy
Queries memory first for speed, falls back to web if needed. Best for cost and performance.

## 📞 Getting Help

1. Check `PHASE1_DOCUMENTATION.md` for details
2. Review test examples in `tests/` 
3. Check logs in `logs/app.log`
4. Enable DEBUG=True in .env for verbose output

## 🎯 Next Steps

1. ✅ Install and run the server
2. ✅ Run the test suite
3. ✅ Try the API examples
4. ⏳ Phase 2: Document processing & vector DB
5. ⏳ Phase 3: Memory integration
6. ⏳ Phase 4: Advanced features
7. ⏳ Phase 5: Deployment & scaling

---

**Need help? Check the logs:**
```bash
tail -f logs/app.log
```

**Something broken? Run tests first:**
```bash
pytest tests/ -v
```

**Ready to extend? See PHASE1_DOCUMENTATION.md** 📚
