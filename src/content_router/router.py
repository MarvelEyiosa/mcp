"""
Intelligent Content Router with memory-first strategy
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from config.logging_config import log
from src.mcp_protocol import ContentSource, ContentBlock, SynthesizedContent
from src.mcp_server.quality_scorer import quality_scorer


class RoutingStrategy(str, Enum):
    """Content routing strategies"""
    MEMORY_FIRST = "memory_first"  # Check memory first, fallback to external
    EXTERNAL_FIRST = "external_first"  # Check external sources first
    BALANCED = "balanced"  # Mix memory and external
    MEMORY_ONLY = "memory_only"  # Only use memory
    EXTERNAL_ONLY = "external_only"  # Only external sources


@dataclass
class RoutingDecision:
    """Decision on which sources to query"""
    strategy: RoutingStrategy
    sources_to_query: List[str]
    expected_quality: float
    reasoning: str


class ContentRouter:
    """Routes content requests to appropriate sources"""
    
    def __init__(self, default_strategy: RoutingStrategy = RoutingStrategy.MEMORY_FIRST):
        self.default_strategy = default_strategy
        self.registered_sources: Dict[str, Any] = {}
        self.source_metrics: Dict[str, Dict[str, float]] = {}
        self.memory_hit_threshold = 0.7
        self.routing_decisions_log: List[Dict[str, Any]] = []
        
        log.info(f"ContentRouter initialized with strategy: {default_strategy}")
    
    # ============ Source Registration ============
    
    def register_source(
        self,
        source_id: str,
        source_type: str,
        source_handler: Any,
        priority: int = 0,
    ) -> None:
        """Register a content source"""
        self.registered_sources[source_id] = {
            "type": source_type,
            "handler": source_handler,
            "priority": priority,
            "registered_at": datetime.utcnow(),
        }
        
        # Initialize metrics
        self.source_metrics[source_id] = {
            "queries_count": 0,
            "successful_queries": 0,
            "avg_response_time": 0.0,
            "avg_quality_score": 0.0,
            "hit_rate": 0.0,
        }
        
        log.info(f"Source registered: {source_id} ({source_type})")
    
    def list_sources(self) -> List[Dict[str, Any]]:
        """List all registered sources"""
        sources = []
        for source_id, source_info in self.registered_sources.items():
            sources.append({
                "id": source_id,
                "type": source_info["type"],
                "priority": source_info["priority"],
                "metrics": self.source_metrics[source_id],
            })
        return sorted(sources, key=lambda x: x["priority"], reverse=True)
    
    # ============ Routing Logic ============
    
    async def route_request(
        self,
        query: str,
        strategy: Optional[RoutingStrategy] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> RoutingDecision:
        """
        Decide which sources to query for a request
        
        Args:
            query: User's query
            strategy: Routing strategy to use (None = use default)
            context: Additional context about the request
        
        Returns:
            RoutingDecision with sources to query
        """
        strategy = strategy or self.default_strategy
        context = context or {}
        
        if strategy == RoutingStrategy.MEMORY_FIRST:
            decision = await self._route_memory_first(query, context)
        elif strategy == RoutingStrategy.EXTERNAL_FIRST:
            decision = await self._route_external_first(query, context)
        elif strategy == RoutingStrategy.BALANCED:
            decision = await self._route_balanced(query, context)
        elif strategy == RoutingStrategy.MEMORY_ONLY:
            decision = await self._route_memory_only(query, context)
        elif strategy == RoutingStrategy.EXTERNAL_ONLY:
            decision = await self._route_external_only(query, context)
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")
        
        # Log decision
        self._log_routing_decision(decision, query)
        return decision
    
    async def _route_memory_first(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> RoutingDecision:
        """Memory-first routing: check memory, fallback to external"""
        memory_source = self._get_source_by_type("memory")
        
        sources_to_query = []
        reasoning = "Memory-first strategy: "
        
        if memory_source:
            sources_to_query.append(memory_source)
            reasoning += "querying memory first"
            
            # Check if memory has good results
            # (In real implementation, this would check actual results)
            external_source = self._get_source_by_type("web_search")
            if external_source:
                sources_to_query.append(external_source)
                reasoning += ", with web fallback"
        else:
            # No memory, fall back to external
            external_source = self._get_source_by_type("web_search")
            if external_source:
                sources_to_query.append(external_source)
                reasoning = "No memory source available, using web search"
        
        expected_quality = 0.8 if len(sources_to_query) >= 1 else 0.5
        
        return RoutingDecision(
            strategy=RoutingStrategy.MEMORY_FIRST,
            sources_to_query=sources_to_query,
            expected_quality=expected_quality,
            reasoning=reasoning,
        )
    
    async def _route_external_first(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> RoutingDecision:
        """External-first: check external sources first, then memory"""
        external_source = self._get_source_by_type("web_search")
        memory_source = self._get_source_by_type("memory")
        
        sources_to_query = []
        
        if external_source:
            sources_to_query.append(external_source)
        if memory_source:
            sources_to_query.append(memory_source)
        
        reasoning = f"External-first strategy: querying {len(sources_to_query)} sources"
        
        return RoutingDecision(
            strategy=RoutingStrategy.EXTERNAL_FIRST,
            sources_to_query=sources_to_query,
            expected_quality=0.85 if len(sources_to_query) == 2 else 0.6,
            reasoning=reasoning,
        )
    
    async def _route_balanced(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> RoutingDecision:
        """Balanced: use both memory and external sources equally"""
        sources_to_query = []
        
        for source_id in self.registered_sources:
            sources_to_query.append(source_id)
        
        reasoning = f"Balanced strategy: querying all {len(sources_to_query)} sources"
        
        return RoutingDecision(
            strategy=RoutingStrategy.BALANCED,
            sources_to_query=sources_to_query,
            expected_quality=0.9,
            reasoning=reasoning,
        )
    
    async def _route_memory_only(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> RoutingDecision:
        """Memory-only: use only memory sources"""
        memory_source = self._get_source_by_type("memory")
        sources_to_query = [memory_source] if memory_source else []
        
        reasoning = "Memory-only strategy"
        
        return RoutingDecision(
            strategy=RoutingStrategy.MEMORY_ONLY,
            sources_to_query=sources_to_query,
            expected_quality=0.75 if sources_to_query else 0.0,
            reasoning=reasoning,
        )
    
    async def _route_external_only(
        self,
        query: str,
        context: Dict[str, Any],
    ) -> RoutingDecision:
        """External-only: use only external sources"""
        external_source = self._get_source_by_type("web_search")
        sources_to_query = [external_source] if external_source else []
        
        reasoning = "External-only strategy"
        
        return RoutingDecision(
            strategy=RoutingStrategy.EXTERNAL_ONLY,
            sources_to_query=sources_to_query,
            expected_quality=0.7 if sources_to_query else 0.0,
            reasoning=reasoning,
        )
    
    # ============ Helper Methods ============
    
    def _get_source_by_type(self, source_type: str) -> Optional[str]:
        """Get highest priority source of given type"""
        candidates = [
            (source_id, info["priority"])
            for source_id, info in self.registered_sources.items()
            if info["type"] == source_type
        ]
        
        if not candidates:
            return None
        
        return max(candidates, key=lambda x: x[1])[0]
    
    def _log_routing_decision(self, decision: RoutingDecision, query: str) -> None:
        """Log routing decision"""
        log.debug(
            f"Routing decision for query '{query[:50]}...': "
            f"strategy={decision.strategy}, sources={decision.sources_to_query}"
        )
        
        self.routing_decisions_log.append({
            "query": query,
            "strategy": decision.strategy.value,
            "sources": decision.sources_to_query,
            "expected_quality": decision.expected_quality,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    # ============ Synthesis ============
    
    async def synthesize_content(
        self,
        query: str,
        content_blocks: List[ContentBlock],
    ) -> SynthesizedContent:
        """
        Synthesize content from multiple sources
        
        Args:
            query: Original query
            content_blocks: Content blocks from multiple sources
        
        Returns:
            Synthesized content with analysis
        """
        synthesis_id = f"syn_{datetime.utcnow().timestamp()}"
        
        # Aggregate content
        aggregated_content = self._aggregate_content(content_blocks)
        
        # Extract sources
        sources = list(set(block.source for block in content_blocks))
        
        # Find contradictions
        contradictions = self._find_contradictions(content_blocks)
        
        # Identify gaps
        gaps = self._identify_gaps(content_blocks, query)
        
        # Calculate overall quality
        quality_score = sum(
            block.relevance_score for block in content_blocks
        ) / len(content_blocks) if content_blocks else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            content_blocks,
            contradictions,
            gaps,
        )
        
        log.info(
            f"Synthesized content from {len(sources)} sources: "
            f"quality={quality_score:.2f}, contradictions={len(contradictions)}, gaps={len(gaps)}"
        )
        
        return SynthesizedContent(
            synthesis_id=synthesis_id,
            query=query,
            aggregated_content=aggregated_content,
            sources=sources,
            quality_score=quality_score,
            contradictions=contradictions,
            gaps=gaps,
            recommendations=recommendations,
        )
    
    def _aggregate_content(self, content_blocks: List[ContentBlock]) -> str:
        """Aggregate content from multiple blocks"""
        if not content_blocks:
            return ""
        
        # Sort by relevance score
        sorted_blocks = sorted(
            content_blocks,
            key=lambda x: x.relevance_score,
            reverse=True,
        )
        
        # Combine with source attribution
        aggregated = []
        for block in sorted_blocks:
            attribution = f"\n[Source: {block.source.name}]"
            aggregated.append(f"{block.body}{attribution}")
        
        return "\n\n".join(aggregated)
    
    def _find_contradictions(self, content_blocks: List[ContentBlock]) -> List[Dict[str, Any]]:
        """Find contradictions between sources"""
        # Simplified contradiction detection
        contradictions = []
        
        if len(content_blocks) >= 2:
            for i, block1 in enumerate(content_blocks):
                for block2 in content_blocks[i+1:]:
                    # Check for conflicting information (simplified)
                    # In real implementation, use semantic comparison
                    if self._blocks_contradict(block1, block2):
                        contradictions.append({
                            "source1": block1.source.name,
                            "source2": block2.source.name,
                            "description": "Potentially conflicting information detected",
                        })
        
        return contradictions
    
    def _blocks_contradict(self, block1: ContentBlock, block2: ContentBlock) -> bool:
        """Check if two blocks contain contradictions"""
        # Simplified check - in reality, use semantic analysis
        return False
    
    def _identify_gaps(self, content_blocks: List[ContentBlock], query: str) -> List[str]:
        """Identify gaps in content coverage"""
        gaps = []
        
        # Check for common query aspects not covered
        query_terms = query.lower().split()
        combined_text = " ".join(block.body.lower() for block in content_blocks)
        
        missing_terms = []
        for term in query_terms:
            if len(term) > 3 and term not in combined_text:
                missing_terms.append(term)
        
        if missing_terms:
            gaps.append(f"Missing coverage on: {', '.join(missing_terms)}")
        
        if not content_blocks:
            gaps.append("No content available for query")
        elif len(content_blocks) == 1:
            gaps.append("Only single source available, multiple sources recommended")
        
        return gaps
    
    def _generate_recommendations(
        self,
        content_blocks: List[ContentBlock],
        contradictions: List[Dict[str, Any]],
        gaps: List[str],
    ) -> List[str]:
        """Generate recommendations for improving content"""
        recommendations = []
        
        if contradictions:
            recommendations.append(
                f"Verify {len(contradictions)} contradiction(s) between sources"
            )
        
        if gaps:
            recommendations.append(f"Additional research needed: {gaps[0]}")
        
        if len(content_blocks) < 2:
            recommendations.append("Consult multiple sources for better coverage")
        
        # Quality-based recommendations
        avg_quality = sum(
            b.relevance_score for b in content_blocks
        ) / len(content_blocks) if content_blocks else 0
        
        if avg_quality < 0.6:
            recommendations.append("Consider re-querying with refined search terms")
        
        return recommendations


# Global router instance
content_router = ContentRouter()
