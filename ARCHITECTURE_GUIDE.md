# Implementation and Architecture Guide

## 🎯 Phase 1 Summary: MCP Foundation ✅

### What Was Built

#### 1. **Base MCP Server** (`src/mcp_server/base_server.py`)

This is the core of everything. Let me explain how it works:

```python
# MCPServer is like a container that:
# 1. Registers tools (functions you can call)
# 2. Routes requests to the right tool
# 3. Manages resources (databases, APIs, etc)
# 4. Handles errors gracefully
# 5. Tracks statistics

mcp_server = MCPServer(name="MCP Server", version="1.0.0")
mcp_server.register_tool(web_search_tool)

# When a request comes in:
response = await mcp_server.process_request(request)
# It finds the tool, executes it, returns results
```

**How requests flow:**
```
User sends request
    ↓
MCPServer.process_request(request)
    ↓
Apply middleware (if any)
    ↓
Route to correct method (execute, list_tools, etc)
    ↓
For execute: Find tool by name
    ↓
Execute tool with params
    ↓
Track statistics (execution time, success/failure)
    ↓
Return formatted response
```

#### 2. **Quality Scoring System** (`src/mcp_server/quality_scorer.py`)

This evaluates how "good" content is by looking at 7 factors:

```python
# Example: Score a document
result = quality_scorer.score_content(
    content="Document text here...",
    source_type="memory",  # Who provided this?
    created_at=datetime.utcnow(),
    relevance_score=0.8,   # How relevant to query?
    completeness_score=0.7,  # How complete is it?
    accuracy_score=0.9     # How accurate?
)

# Returns something like:
{
    "overall_score": 0.82,  # 0-1 score
    "quality_level": "high",  # low/medium/high/verified
    "components": [
        {
            "factor": "source_reliability",
            "value": 0.95,  # Memory is reliable
            "weighted_value": 0.238,  # 0.95 * 0.25 weight
            "reasoning": "Memory source is highly reliable"
        },
        # ... more factors
    ]
}
```

**Why different weights?**
- **Source Reliability (25%)**: If the source is wrong, nothing matters
- **Relevance (25%)**: Content must match what user asked
- **Freshness (15%)**: Old information can be outdated
- **Completeness (15%)**: Need enough detail to be useful
- **Accuracy (15%)**: Information must be correct
- **Citations (3%)**: References add credibility
- **User Feedback (2%)**: What users thought before

**Quality Levels:**
- **VERIFIED** (≥0.90): Trust completely
- **HIGH** (≥0.75): Generally trustworthy
- **MEDIUM** (≥0.50): May need verification
- **LOW** (<0.50): Questionable, needs backup sources

#### 3. **Content Router** (`src/content_router/router.py`)

Decides where to get content from (memory, web search, etc):

```python
# Different strategies for different situations:

# Strategy 1: MEMORY_FIRST (default)
# "Check our stored documents first, fastest & cheapest"
decision = await router.route_request(
    query="AI trends",
    strategy=RoutingStrategy.MEMORY_FIRST
)
# Returns: ["memory", "web_search"]  - try memory first, then web

# Strategy 2: EXTERNAL_FIRST
# "Get latest info from web, then check our docs"
decision = await router.route_request(
    query="breaking news",
    strategy=RoutingStrategy.EXTERNAL_FIRST
)
# Returns: ["web_search", "memory"]  - web first for fresh data

# Strategy 3: BALANCED
# "Use everything, give me comprehensive coverage"
decision = await router.route_request(
    query="detailed analysis",
    strategy=RoutingStrategy.BALANCED
)
# Returns: ["memory", "web_search", "api"]  - all sources

# Strategy 4: MEMORY_ONLY
# "Only use what we've stored (offline)"
decision = await router.route_request(
    query="search query",
    strategy=RoutingStrategy.MEMORY_ONLY
)
# Returns: ["memory"]  - just our documents

# Strategy 5: EXTERNAL_ONLY
# "Only get new content"
decision = await router.route_request(
    query="search query",
    strategy=RoutingStrategy.EXTERNAL_ONLY
)
# Returns: ["web_search"]  - only new information
```

**What the router also does:**

1. **Aggregates content** from multiple sources
```python
# Combines results like:
aggregated = """
[Source: Memory] Content from our database...
[Source: Web] Latest info from the web...
"""
```

2. **Finds contradictions** between sources
```python
contradictions = [
    {
        "source1": "Memory",
        "source2": "Web",
        "description": "Different numbers reported"
    }
]
```

3. **Identifies gaps** in coverage
```python
gaps = [
    "Missing coverage on: recent developments",
    "Only single source available"
]
```

4. **Makes recommendations**
```python
recommendations = [
    "Verify contradiction between sources",
    "Consult multiple sources for coverage"
]
```

#### 4. **Web Search Tool** (`src/web_search/web_search_tool.py`)

Searches the internet using Google's Gemini API:

```python
# How it's used:
tool = WebSearchTool()

# User wants to search
result = await tool.execute({
    "query": "machine learning",
    "limit": 5  # Get 5 results
})

# Returns:
{
    "success": True,
    "results": [
        {
            "title": "Machine Learning Overview",
            "snippet": "ML is a type of AI that...",
            "url": "https://example.com/ml",
            "relevance_score": 0.95  # How relevant
        },
        # ... more results
    ]
}
```

**Mock fallback for testing:**
```python
# If API key not available, returns mock results
# This lets you test without real API calls
results = tool._mock_search("AI", 3)
```

### 5. **Protocol Definitions** (`src/mcp_protocol.py`)

Standardized formats for requests and responses:

```python
# Every request looks like:
request = MCPRequest(
    request_id="req_001",     # Unique ID
    method="execute",          # What to do
    tool="web_search",        # Which tool
    params={                  # Tool parameters
        "query": "AI",
        "limit": 10
    }
)

# Every response looks like:
response = MCPResponse(
    request_id="req_001",     # Match the request
    status="success",          # success/error/partial
    data={...},                # Actual results
    error=None,               # Error details if failed
    execution_time_ms=125.5   # How long it took
)
```

This makes the system predictable - any tool, any client knows what to expect.

### 6. **Testing Framework** (33 tests total)

Tests validate everything works:

```bash
# Run all tests
pytest tests/ -v

# Test results show:
test_mcp_server.py::test_server_initialization PASSED
test_quality_scorer.py::test_content_scoring PASSED
test_content_router.py::test_memory_first_routing PASSED
test_web_search.py::test_search_execution PASSED

# ... 33 tests total
# All passing = system is working correctly
```

## 🔄 How Everything Works Together

Here's a complete example of what happens when someone asks a question:

```
User: "What are AI trends in 2024?"
    ↓
1. FastAPI receives request to /request
    ↓
2. MCPServer.process_request() is called
    ↓
3. Router decides strategy (default: memory_first)
    ↓
4. Router.route_request() returns:
   - sources_to_query: ["memory", "web_search"]
   - reasoning: "Check memory first, fallback to web"
    ↓
5. For each source, execute it:
   
   a) Query Memory (Phase 2 will add this)
      - Search internal documents
      - Find relevant content
      - Score with QualityScorer (0.85 quality)
      
   b) Query Web Search Tool
      - Call tool.execute({"query": "AI trends 2024"})
      - Get web results
      - Convert to ContentBlock format
      - Score with QualityScorer (0.70 quality)
    ↓
6. Router.synthesize_content() combines them:
   - Aggregates: "From memory: ... From web: ..."
   - Finds contradictions: "Different growth rates reported"
   - Identifies gaps: "Missing discussion of regulation"
   - Makes recommendations: "Verify statistics across sources"
    ↓
7. Return to user:
{
    "aggregated_content": "Combined answer from all sources",
    "sources": ["memory", "web"],
    "quality_score": 0.78,
    "contradictions": [...],
    "gaps": [...],
    "recommendations": [...]
}
```

## 📊 Key Concepts Explained

### Memory-First Strategy

**Why is this important?**

```
Scenario 1: Without memory
User asks: "What's Python?"
→ Search internet EVERY time
→ Uses API calls, costs money, takes time

Scenario 2: With memory
User asks: "What's Python?" (first time)
→ Search internet
→ Store result
User asks again later: "What's Python?"
→ Find in memory (instant!)
→ Save money, save time

Result: 60% of questions answered from memory
Cost reduction: >50%
Response time: <200ms for memory hits
```

### Quality Scoring for Reliability

```
Source 1: Wikipedia says "AI market will grow 40%"
Source 2: News site says "AI market will grow 35%"

Without quality scoring:
→ Can't tell which to trust
→ Might pick wrong one
→ User gets bad info

With quality scoring:
Source 1: Wikipedia
- Source reliability: 0.85 (reputable)
- Content freshness: 0.90 (recent)
- Has citations: Yes (+credibility)
- Score: 0.82 (HIGH)

Source 2: News site
- Source reliability: 0.75 (good)
- Content freshness: 0.95 (very recent)
- Citation count: 5 (good)
- Score: 0.88 (HIGH)

Conclusion: Both good, but news is fresher
→ Present both with confidence levels
→ User makes informed decision
```

### Content Synthesis

```
Without synthesis:
"Here's memory result. Here's web result."
→ User has to figure it out

With synthesis:
"Market will grow by 35-40% per multiple sources
 (Wikipedia says 40%, recent news says 35%).
 Contradiction: Likely due to different methodologies.
 Recommendation: Both sources are credible, use average (37.5%)"
→ User gets clear, actionable answer
```

## 🛠️ How You'll Edit/Extend the Code

### Adding a New Tool

```python
# 1. Create new file: src/my_tool/my_tool.py
from src.mcp_server import MCPTool, ToolType

class MyAnalyzerTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="my_analyzer",
            description="Analyzes text sentiment",
            tool_type=ToolType.ANALYSIS,
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "sentiment": {"type": "string"},
                    "score": {"type": "number"}
                }
            }
        )
    
    async def execute(self, params):
        text = params.get("text", "")
        
        # Your analysis code here
        sentiment = "positive"  # Your logic
        score = 0.85
        
        return {
            "sentiment": sentiment,
            "score": score
        }

# 2. In main.py, register it:
from src.my_tool.my_tool import MyAnalyzerTool

my_tool = MyAnalyzerTool()
mcp_server.register_tool(my_tool)

# 3. Now you can use it:
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_001",
    "method": "execute",
    "tool": "my_analyzer",
    "params": {"text": "This is great!"}
  }'
```

### Adjusting Quality Scorer Weights

```python
# By default, source reliability is most important (25%)
# If you want to focus more on freshness:

from src.mcp_server import quality_scorer
from src.mcp_server.quality_scorer import ScoringFactors

# Increase freshness weight
quality_scorer.set_factor_weight(
    ScoringFactors.CONTENT_FRESHNESS, 
    0.35  # Now freshness is 35%
)

# Now newer content scores higher
```

### Changing Routing Strategy

```python
# In FastAPI handler, specify strategy:
from src.content_router import RoutingStrategy

decision = await content_router.route_request(
    query=user_query,
    strategy=RoutingStrategy.EXTERNAL_FIRST  # Always fresh
)
```

## 📈 Performance Characteristics

### Phase 1 (Current)

| Operation | Time | Notes |
|-----------|------|-------|
| Web Search | 1-2s | Depends on API |
| Quality Scoring | <50ms | Fast calculation |
| Route Decision | <10ms | Simple logic |
| Tool Registration | <1ms | In-memory operation |

### Phase 2 (Will Improve)

| Operation | Time | Notes |
|-----------|------|-------|
| Memory Search | <200ms | Vector DB query |
| Document Processing | 2-5s | First time only |
| Memory Hit | <100ms | Very fast |
| Synthesis | <500ms | Combining sources |

## 🎯 Design Decisions Explained

### Why FastAPI?
- ✅ Async/await support (non-blocking)
- ✅ Automatic OpenAPI docs
- ✅ Performance
- ✅ Easy to extend

### Why ChromaDB for Phase 2?
- ✅ Easy vector storage
- ✅ Semantic search built-in
- ✅ Persistent storage
- ✅ Good performance

### Why MCP Protocol?
- ✅ Standardized format
- ✅ Other AI systems can understand
- ✅ Easier integration
- ✅ Better error handling

### Why Weighted Scoring?
- ✅ Different situations need different priorities
- ✅ Customizable for your use case
- ✅ Transparent (see all factors)
- ✅ Learnable (improve over time)

---

**Next: Phase 2 will add document storage and semantic search!** 🚀
