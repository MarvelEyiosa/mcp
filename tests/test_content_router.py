"""
Tests for Content Router
"""
import pytest
from datetime import datetime
from src.content_router.router import ContentRouter, RoutingStrategy
from src.mcp_protocol import ContentBlock, ContentSource


class TestContentRouter:
    """Test content routing functionality"""
    
    @pytest.fixture
    def router(self):
        """Create test router"""
        router = ContentRouter(default_strategy=RoutingStrategy.MEMORY_FIRST)
        
        # Register mock sources
        router.register_source("memory", "memory", None, priority=10)
        router.register_source("web", "web_search", None, priority=5)
        
        return router
    
    def test_router_initialization(self, router):
        """Test router initializes correctly"""
        assert router.default_strategy == RoutingStrategy.MEMORY_FIRST
        assert len(router.registered_sources) == 2
    
    def test_source_registration(self, router):
        """Test source registration"""
        sources = router.list_sources()
        
        assert len(sources) == 2
        assert sources[0]["id"] == "memory"  # Higher priority
        assert sources[1]["id"] == "web"
    
    def test_source_lookup(self, router):
        """Test source lookup by type"""
        memory_source = router._get_source_by_type("memory")
        web_source = router._get_source_by_type("web_search")
        
        assert memory_source == "memory"
        assert web_source == "web"
    
    @pytest.mark.asyncio
    async def test_memory_first_routing(self, router):
        """Test memory-first routing strategy"""
        decision = await router.route_request(
            query="test query",
            strategy=RoutingStrategy.MEMORY_FIRST
        )
        
        assert decision.strategy == RoutingStrategy.MEMORY_FIRST
        assert len(decision.sources_to_query) > 0
        assert "memory" in decision.sources_to_query
    
    @pytest.mark.asyncio
    async def test_external_first_routing(self, router):
        """Test external-first routing strategy"""
        decision = await router.route_request(
            query="test query",
            strategy=RoutingStrategy.EXTERNAL_FIRST
        )
        
        assert decision.strategy == RoutingStrategy.EXTERNAL_FIRST
        assert len(decision.sources_to_query) > 0
    
    @pytest.mark.asyncio
    async def test_balanced_routing(self, router):
        """Test balanced routing strategy"""
        decision = await router.route_request(
            query="test query",
            strategy=RoutingStrategy.BALANCED
        )
        
        assert decision.strategy == RoutingStrategy.BALANCED
        assert len(decision.sources_to_query) == 2  # All sources
    
    @pytest.mark.asyncio
    async def test_memory_only_routing(self, router):
        """Test memory-only routing strategy"""
        decision = await router.route_request(
            query="test query",
            strategy=RoutingStrategy.MEMORY_ONLY
        )
        
        assert decision.strategy == RoutingStrategy.MEMORY_ONLY
        assert decision.sources_to_query == ["memory"]
    
    @pytest.mark.asyncio
    async def test_default_routing_strategy(self, router):
        """Test default routing strategy"""
        decision = await router.route_request(query="test query")
        
        assert decision.strategy == RoutingStrategy.MEMORY_FIRST
    
    @pytest.mark.asyncio
    async def test_content_aggregation(self, router):
        """Test content aggregation"""
        # Create sample content blocks
        source1 = ContentSource(
            source_id="src1",
            source_type="memory",
            name="Memory Source",
            quality_score=0.95,
            confidence_score=0.9,
            last_updated=datetime.utcnow()
        )
        
        source2 = ContentSource(
            source_id="src2",
            source_type="web_search",
            name="Web Source",
            quality_score=0.85,
            confidence_score=0.8,
            last_updated=datetime.utcnow()
        )
        
        block1 = ContentBlock(
            content_id="block1",
            source=source1,
            title="Memory Content",
            body="Content from memory",
            relevance_score=0.9
        )
        
        block2 = ContentBlock(
            content_id="block2",
            source=source2,
            title="Web Content",
            body="Content from web",
            relevance_score=0.8
        )
        
        synthesized = await router.synthesize_content(
            query="test query",
            content_blocks=[block1, block2]
        )
        
        assert synthesized.query == "test query"
        assert len(synthesized.sources) == 2
        assert synthesized.quality_score > 0
        assert "Memory Content" in synthesized.aggregated_content or "Web Content" in synthesized.aggregated_content
    
    def test_routing_decisions_logging(self, router):
        """Test that routing decisions are logged"""
        initial_count = len(router.routing_decisions_log)
        
        # Trigger routing decision logging
        router._log_routing_decision(
            decision=type('obj', (object,), {
                'strategy': RoutingStrategy.MEMORY_FIRST,
                'sources_to_query': ['memory']
            }),
            query="test query"
        )
        
        assert len(router.routing_decisions_log) == initial_count + 1
