"""
Tests for MCP Server Framework
"""
import pytest
import asyncio
from datetime import datetime
from src.mcp_server.base_server import MCPServer, MCPTool, ToolType
from src.mcp_protocol import MCPRequest, MCPResponse
from src.utils import MCPException, ContentQuality


class DummyTool(MCPTool):
    """Dummy tool for testing"""
    
    async def execute(self, params):
        return {
            "status": "success",
            "data": params.get("input", "no input")
        }


class TestMCPServer:
    """Test MCP Server functionality"""
    
    @pytest.fixture
    def server(self):
        """Create test server"""
        return MCPServer(name="TestServer", version="1.0.0")
    
    def test_server_initialization(self, server):
        """Test server initializes correctly"""
        assert server.name == "TestServer"
        assert server.version == "1.0.0"
        assert len(server.tools) == 0
    
    def test_tool_registration(self, server):
        """Test tool registration"""
        tool = DummyTool(
            name="dummy",
            description="Dummy tool",
            tool_type=ToolType.TEXT_PROCESSING,
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        server.register_tool(tool)
        
        assert "dummy" in server.tools
        assert server.get_tool("dummy") == tool
    
    def test_tool_unregistration(self, server):
        """Test tool unregistration"""
        tool = DummyTool(
            name="dummy",
            description="Dummy tool",
            tool_type=ToolType.TEXT_PROCESSING,
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        server.register_tool(tool)
        assert "dummy" in server.tools
        
        server.unregister_tool("dummy")
        assert "dummy" not in server.tools
    
    def test_list_tools(self, server):
        """Test listing tools"""
        tool = DummyTool(
            name="dummy",
            description="Dummy tool",
            tool_type=ToolType.TEXT_PROCESSING,
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        server.register_tool(tool)
        tools = server.list_tools()
        
        assert len(tools) == 1
        assert tools[0].name == "dummy"
    
    @pytest.mark.asyncio
    async def test_execute_tool(self, server):
        """Test tool execution"""
        tool = DummyTool(
            name="test_tool",
            description="Test tool",
            tool_type=ToolType.TEXT_PROCESSING,
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        server.register_tool(tool)
        
        request = MCPRequest(
            request_id="req_123",
            method="execute",
            tool="test_tool",
            params={"input": "test data"}
        )
        
        response = await server.process_request(request)
        
        assert response.status == "success"
        assert response.data["status"] == "success"
        assert response.data["data"] == "test data"
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self, server):
        """Test executing non-existent tool"""
        request = MCPRequest(
            request_id="req_123",
            method="execute",
            tool="nonexistent",
            params={}
        )
        
        response = await server.process_request(request)
        
        assert response.status == "error"
        assert response.error is not None
    
    @pytest.mark.asyncio
    async def test_list_tools_request(self, server):
        """Test list_tools request"""
        tool = DummyTool(
            name="dummy",
            description="Dummy tool",
            tool_type=ToolType.TEXT_PROCESSING,
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        server.register_tool(tool)
        
        request = MCPRequest(
            request_id="req_123",
            method="list_tools",
            tool="",
            params={}
        )
        
        response = await server.process_request(request)
        
        assert response.status == "success"
        assert response.data["count"] == 1
    
    def test_server_stats(self, server):
        """Test server statistics"""
        stats = server.get_stats()
        
        assert stats["name"] == "TestServer"
        assert stats["version"] == "1.0.0"
        assert stats["tools_count"] == 0
        assert stats["total_requests"] == 0
