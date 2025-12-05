"""
Tests for Quality Scorer
"""
import pytest
from datetime import datetime, timedelta
from src.mcp_server.quality_scorer import QualityScorer, ScoringFactors
from src.utils import ContentQuality


class TestQualityScorer:
    """Test quality scoring functionality"""
    
    @pytest.fixture
    def scorer(self):
        """Create test scorer"""
        return QualityScorer()
    
    def test_scorer_initialization(self, scorer):
        """Test scorer initializes correctly"""
        assert len(scorer.factor_weights) > 0
        assert len(scorer.source_reliability_scores) > 0
    
    def test_source_reliability_scoring(self, scorer):
        """Test source reliability scoring"""
        memory_score = scorer._score_source_reliability("memory")
        web_score = scorer._score_source_reliability("web_search")
        
        assert memory_score > web_score
        assert 0 <= memory_score <= 1
        assert 0 <= web_score <= 1
    
    def test_freshness_scoring(self, scorer):
        """Test freshness scoring"""
        now = datetime.utcnow()
        
        fresh = now  # Just created
        old_30 = now - timedelta(days=30)  # 30 days old
        old_90 = now - timedelta(days=90)  # 90 days old
        
        score_fresh = scorer._score_freshness(fresh)
        score_30 = scorer._score_freshness(old_30)
        score_90 = scorer._score_freshness(old_90)
        
        assert score_fresh >= score_30 >= score_90
    
    def test_completeness_scoring(self, scorer):
        """Test completeness scoring"""
        short_content = "Short text"
        long_content = "A" * 1000  # Long content
        
        score_short = scorer._score_completeness(short_content, 0.5)
        score_long = scorer._score_completeness(long_content, 0.5)
        
        assert score_long >= score_short
    
    def test_quality_level_determination(self, scorer):
        """Test quality level determination"""
        assert scorer._determine_quality_level(0.95) == ContentQuality.VERIFIED
        assert scorer._determine_quality_level(0.8) == ContentQuality.HIGH
        assert scorer._determine_quality_level(0.6) == ContentQuality.MEDIUM
        assert scorer._determine_quality_level(0.3) == ContentQuality.LOW
    
    def test_content_scoring(self, scorer):
        """Test overall content scoring"""
        content = "This is a test document with some meaningful content."
        
        result = scorer.score_content(
            content=content,
            source_type="memory",
            created_at=datetime.utcnow(),
            relevance_score=0.8,
            completeness_score=0.7,
            accuracy_score=0.9,
            citation_count=5
        )
        
        assert "overall_score" in result
        assert "quality_level" in result
        assert "components" in result
        
        assert 0 <= result["overall_score"] <= 1
        assert result["quality_level"] in ["low", "medium", "high", "verified"]
        assert len(result["components"]) > 0
    
    def test_factor_weight_adjustment(self, scorer):
        """Test adjusting factor weights"""
        original_weight = scorer.factor_weights[ScoringFactors.RELEVANCE]
        
        scorer.set_factor_weight(ScoringFactors.RELEVANCE, 0.5)
        
        assert scorer.factor_weights[ScoringFactors.RELEVANCE] != original_weight
    
    def test_source_reliability_adjustment(self, scorer):
        """Test adjusting source reliability"""
        original = scorer.source_reliability_scores.get("custom_source", None)
        
        scorer.set_source_reliability("custom_source", 0.8)
        
        assert scorer.source_reliability_scores["custom_source"] == 0.8
    
    def test_weighted_score_calculation(self, scorer):
        """Test that weights affect final score"""
        content = "Test document"
        
        result1 = scorer.score_content(
            content=content,
            source_type="memory",
            created_at=datetime.utcnow(),
            relevance_score=0.9,
            completeness_score=0.5,
            accuracy_score=0.5,
        )
        
        # Adjust weights to favor relevance
        original_relevance_weight = scorer.factor_weights[ScoringFactors.RELEVANCE]
        scorer.set_factor_weight(ScoringFactors.RELEVANCE, 0.9)
        
        result2 = scorer.score_content(
            content=content,
            source_type="memory",
            created_at=datetime.utcnow(),
            relevance_score=0.9,
            completeness_score=0.5,
            accuracy_score=0.5,
        )
        
        # Score should be higher when relevance is weighted more heavily
        assert result2["overall_score"] >= result1["overall_score"]
        
        # Reset weight
        scorer.factor_weights[ScoringFactors.RELEVANCE] = original_relevance_weight
