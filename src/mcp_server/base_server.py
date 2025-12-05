"""
Base MCP Server class with protocol handlers and tool management
"""
from typing import Any, Dict, List, Optional, Callable, Awaitable
from abc import ABC, abstractmethod
import time
import json
from datetime import datetime
from config.logging_config import log
from src.mcp_protocol import (
    MCPRequest,
    MCPResponse,
    ToolDefinition,
    ToolType,
)
from src.utils import (
    MCPException,
    generate_id,
    get_current_timestamp,
)


class MCPTool(ABC):
    """Base class for MCP tools"""
    
    def __init__(
        self,
        name: str,
        description: str,
        tool_type: ToolType,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        required_permissions: Optional[List[str]] = None,
    ):
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.required_permissions = required_permissions or []
        self.execution_count = 0
        self.total_execution_time = 0.0
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def get_definition(self) -> ToolDefinition:
        """Get tool definition"""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            tool_type=self.tool_type,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            required_permissions=self.required_permissions,
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics"""
        avg_time = (
            self.total_execution_time / self.execution_count
            if self.execution_count > 0
            else 0
        )
        return {
            "name": self.name,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_time,
        }


class BaseResourceManager(ABC):
    """Base class for resource management"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize resources"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check for resources"""
        pass


class MCPServer:
    """Base MCP Server with protocol compliance"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, BaseResourceManager] = {}
        self.middleware: List[Callable] = []
        self.error_handlers: Dict[type, Callable] = {}
        self.request_count = 0
        self.error_count = 0
        self.start_time = get_current_timestamp()
        
        log.info(f"Initializing MCP Server: {name} v{version}")
    
    # ============ Tool Management ============
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool with the server"""
        if tool.name in self.tools:
            log.warning(f"Tool {tool.name} already registered, overwriting")
        self.tools[tool.name] = tool
        log.info(f"Tool registered: {tool.name}")
    
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            log.info(f"Tool unregistered: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a registered tool"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[ToolDefinition]:
        """List all available tools"""
        return [tool.get_definition() for tool in self.tools.values()]
    
    # ============ Resource Management ============
    
    def register_resource(self, resource_id: str, resource: BaseResourceManager) -> None:
        """Register a resource"""
        self.resources[resource_id] = resource
        log.info(f"Resource registered: {resource_id}")
    
    async def initialize_resources(self) -> None:
        """Initialize all registered resources"""
        for resource_id, resource in self.resources.items():
            try:
                await resource.initialize()
                log.info(f"Resource initialized: {resource_id}")
            except Exception as e:
                log.error(f"Failed to initialize resource {resource_id}: {e}")
                raise
    
    async def cleanup_resources(self) -> None:
        """Cleanup all resources"""
        for resource_id, resource in self.resources.items():
            try:
                await resource.cleanup()
                log.info(f"Resource cleaned up: {resource_id}")
            except Exception as e:
                log.error(f"Failed to cleanup resource {resource_id}: {e}")
    
    async def check_resources_health(self) -> Dict[str, Any]:
        """Check health of all resources"""
        health_status = {}
        for resource_id, resource in self.resources.items():
            try:
                health = await resource.health_check()
                health_status[resource_id] = health
            except Exception as e:
                log.error(f"Health check failed for {resource_id}: {e}")
                health_status[resource_id] = {"status": "unhealthy", "error": str(e)}
        return health_status
    
    # ============ Middleware Management ============
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to request processing"""
        self.middleware.append(middleware)
    
    async def apply_middleware(self, request: MCPRequest) -> MCPRequest:
        """Apply all middleware to request"""
        for middleware in self.middleware:
            request = await middleware(request)
        return request
    
    # ============ Error Handling ============
    
    def register_error_handler(self, error_type: type, handler: Callable) -> None:
        """Register custom error handler"""
        self.error_handlers[error_type] = handler
    
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle errors with registered handlers"""
        error_type = type(error)
        
        if error_type in self.error_handlers:
            handler = self.error_handlers[error_type]
            return await handler(error) if hasattr(handler, '__await__') else handler(error)
        
        # Default error handling
        return {
            "error_type": error_type.__name__,
            "message": str(error),
            "details": getattr(error, 'details', {}),
        }
    
    # ============ Request Processing ============
    
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """Process an MCP request"""
        request_id = request.request_id
        start_time = time.time()
        self.request_count += 1
        
        try:
            log.info(f"Processing request {request_id}: {request.method} {request.tool}")
            
            # Apply middleware
            request = await self.apply_middleware(request)
            
            # Route to appropriate handler
            if request.method == "execute":
                response = await self._execute_tool(request)
            elif request.method == "list_tools":
                response = await self._list_tools(request)
            elif request.method == "get_tool_info":
                response = await self._get_tool_info(request)
            else:
                raise MCPException(f"Unknown method: {request.method}")
            
            return response
            
        except Exception as error:
            log.error(f"Error processing request {request_id}: {error}")
            self.error_count += 1
            error_data = await self.handle_error(error)
            
            execution_time = (time.time() - start_time) * 1000
            return MCPResponse(
                request_id=request_id,
                status="error",
                error=error_data,
                execution_time_ms=execution_time,
            )
    
    async def _execute_tool(self, request: MCPRequest) -> MCPResponse:
        """Execute a tool"""
        tool_name = request.tool
        params = request.params
        
        tool = self.get_tool(tool_name)
        if not tool:
            raise MCPException(f"Tool not found: {tool_name}")
        
        start_time = time.time()
        
        try:
            result = await tool.execute(params)
            execution_time = time.time() - start_time
            
            # Update tool stats
            tool.execution_count += 1
            tool.total_execution_time += execution_time
            
            log.info(f"Tool {tool_name} executed successfully in {execution_time*1000:.2f}ms")
            
            return MCPResponse(
                request_id=request.request_id,
                status="success",
                data=result,
                metadata={
                    "tool": tool_name,
                    "execution_time": execution_time,
                },
                execution_time_ms=execution_time * 1000,
            )
        except Exception as error:
            log.error(f"Tool execution failed: {tool_name}: {error}")
            raise
    
    async def _list_tools(self, request: MCPRequest) -> MCPResponse:
        """List all available tools"""
        tools = self.list_tools()
        return MCPResponse(
            request_id=request.request_id,
            status="success",
            data={
                "tools": [json.loads(tool.json()) for tool in tools],
                "count": len(tools),
            },
        )
    
    async def _get_tool_info(self, request: MCPRequest) -> MCPResponse:
        """Get information about a specific tool"""
        tool_name = request.params.get("tool_name")
        if not tool_name:
            raise MCPException("tool_name parameter required")
        
        tool = self.get_tool(tool_name)
        if not tool:
            raise MCPException(f"Tool not found: {tool_name}")
        
        return MCPResponse(
            request_id=request.request_id,
            status="success",
            data={
                "tool": json.loads(tool.get_definition().json()),
                "stats": tool.get_stats(),
            },
        )
    
    # ============ Server Stats ============
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        uptime = (get_current_timestamp() - self.start_time).total_seconds()
        
        tool_stats = [tool.get_stats() for tool in self.tools.values()]
        
        return {
            "name": self.name,
            "version": self.version,
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "tools_count": len(self.tools),
            "tools": tool_stats,
        }
