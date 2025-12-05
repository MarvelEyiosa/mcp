"""
Main MCP Server Application
"""
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from config.logging_config import log
from config.settings import settings
from src.mcp_server.base_server import MCPServer
from src.mcp_protocol import MCPRequest, MCPResponse
from src.web_search.web_search_tool import WebSearchTool

# Initialize FastAPI app
app = FastAPI(
    title="MCP Server + Document Memory System",
    version="1.0.0",
    description="Intelligent learning companion with persistent memory"
)

# Initialize MCP Server
mcp_server = MCPServer(
    name="MCP Server",
    version="1.0.0"
)

# Register tools
web_search_tool = WebSearchTool()
mcp_server.register_tool(web_search_tool)


@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    log.info("=" * 50)
    log.info("MCP Server Starting Up")
    log.info("=" * 50)
    
    try:
        await mcp_server.initialize_resources()
        log.info("All resources initialized successfully")
    except Exception as e:
        log.error(f"Failed to initialize resources: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    log.info("Shutting down MCP Server")
    await mcp_server.cleanup_resources()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": mcp_server.name,
        "version": mcp_server.version,
        "status": "running",
        "description": "MCP Server + Document Memory System"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    health_status = await mcp_server.check_resources_health()
    return {
        "status": "healthy" if all(
            h.get("status") == "healthy" 
            for h in health_status.values()
        ) else "degraded",
        "resources": health_status
    }


@app.get("/stats")
async def stats():
    """Get server statistics"""
    return mcp_server.get_stats()


@app.get("/tools")
async def list_tools():
    """List all available tools"""
    tools = mcp_server.list_tools()
    return {
        "count": len(tools),
        "tools": [tool.dict() for tool in tools]
    }


@app.post("/execute")
async def execute_tool(request: MCPRequest):
    """Execute a tool via MCP protocol"""
    try:
        response = await mcp_server.process_request(request)
        return response.dict()
    except Exception as e:
        log.error(f"Error executing tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/request")
async def process_request(request: MCPRequest):
    """Process generic MCP request"""
    try:
        response = await mcp_server.process_request(request)
        return response.dict()
    except Exception as e:
        log.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    tool = mcp_server.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
    
    return {
        "tool": tool.get_definition().dict(),
        "stats": tool.get_stats()
    }


if __name__ == "__main__":
    import uvicorn
    
    log.info(f"Starting MCP Server on {settings.MCP_HOST}:{settings.MCP_PORT}")
    
    uvicorn.run(
        app,
        host=settings.MCP_HOST,
        port=settings.MCP_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
