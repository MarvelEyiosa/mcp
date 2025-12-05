"""
Quality Scoring System for content evaluation and ranking
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from config.logging_config import log
from src.utils import ContentQuality


class ScoringFactors(str, Enum):
    """Scoring factors for content quality"""
    SOURCE_RELIABILITY = "source_reliability"
    CONTENT_FRESHNESS = "content_freshness"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CITATION_COUNT = "citation_count"
    USER_FEEDBACK = "user_feedback"
    PROCESSING_QUALITY = "processing_quality"


@dataclass
class ScoreComponent:
    """Individual score component"""
    factor: ScoringFactors
    weight: float  # 0-1
    value: float  # 0-1
    reasoning: str
    
    def calculate(self) -> float:
        """Calculate weighted score"""
        return self.value * self.weight


class QualityScorer:
    """Evaluate and score content quality"""
    
    def __init__(self):
        # Default weights for scoring factors
        self.factor_weights: Dict[ScoringFactors, float] = {
            ScoringFactors.SOURCE_RELIABILITY: 0.25,
            ScoringFactors.CONTENT_FRESHNESS: 0.15,
            ScoringFactors.RELEVANCE: 0.25,
            ScoringFactors.COMPLETENESS: 0.15,
            ScoringFactors.ACCURACY: 0.15,
            ScoringFactors.CITATION_COUNT: 0.03,
            ScoringFactors.USER_FEEDBACK: 0.02,
        }
        
        # Source reliability scores
        self.source_reliability_scores: Dict[str, float] = {
            "memory": 0.95,  # User's own memory is highly reliable
            "verified_api": 0.90,
            "published_research": 0.85,
            "news_aggregator": 0.75,
            "web_search": 0.65,
            "social_media": 0.40,
            "user_generated": 0.50,
        }
        
        self.max_freshness_days = 365  # Content older than this starts losing points
    
    def score_content(
        self,
        content: str,
        source_type: str,
        created_at: datetime,
        relevance_score: float = 0.5,
        completeness_score: float = 0.5,
        accuracy_score: float = 0.5,
        citation_count: int = 0,
        user_feedback_score: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Calculate overall quality score for content
        
        Args:
            content: The content to score
            source_type: Type of source (memory, web, api, etc)
            created_at: When the content was created
            relevance_score: 0-1 relevance to query
            completeness_score: 0-1 how complete the content is
            accuracy_score: 0-1 accuracy of information
            citation_count: Number of citations
            user_feedback_score: 0-1 user satisfaction
        
        Returns:
            Dictionary with overall score and component breakdown
        """
        components: List[ScoreComponent] = []
        
        # 1. Source Reliability
        source_reliability = self._score_source_reliability(source_type)
        components.append(ScoreComponent(
            factor=ScoringFactors.SOURCE_RELIABILITY,
            weight=self.factor_weights[ScoringFactors.SOURCE_RELIABILITY],
            value=source_reliability,
            reasoning=f"Source type '{source_type}' has reliability score {source_reliability}"
        ))
        
        # 2. Content Freshness
        freshness = self._score_freshness(created_at)
        components.append(ScoreComponent(
            factor=ScoringFactors.CONTENT_FRESHNESS,
            weight=self.factor_weights[ScoringFactors.CONTENT_FRESHNESS],
            value=freshness,
            reasoning=f"Content created {self._days_old(created_at)} days ago"
        ))
        
        # 3. Relevance
        components.append(ScoreComponent(
            factor=ScoringFactors.RELEVANCE,
            weight=self.factor_weights[ScoringFactors.RELEVANCE],
            value=relevance_score,
            reasoning=f"Semantic relevance to query: {relevance_score:.2f}"
        ))
        
        # 4. Completeness
        completeness = self._score_completeness(content, completeness_score)
        components.append(ScoreComponent(
            factor=ScoringFactors.COMPLETENESS,
            weight=self.factor_weights[ScoringFactors.COMPLETENESS],
            value=completeness,
            reasoning=f"Content completeness score: {completeness:.2f}"
        ))
        
        # 5. Accuracy
        components.append(ScoreComponent(
            factor=ScoringFactors.ACCURACY,
            weight=self.factor_weights[ScoringFactors.ACCURACY],
            value=accuracy_score,
            reasoning=f"Claimed accuracy score: {accuracy_score:.2f}"
        ))
        
        # 6. Citation Count
        citation_score = min(citation_count / 10, 1.0)  # Max score at 10+ citations
        components.append(ScoreComponent(
            factor=ScoringFactors.CITATION_COUNT,
            weight=self.factor_weights[ScoringFactors.CITATION_COUNT],
            value=citation_score,
            reasoning=f"Number of citations: {citation_count}"
        ))
        
        # 7. User Feedback
        components.append(ScoreComponent(
            factor=ScoringFactors.USER_FEEDBACK,
            weight=self.factor_weights[ScoringFactors.USER_FEEDBACK],
            value=user_feedback_score,
            reasoning=f"User feedback score: {user_feedback_score:.2f}"
        ))
        
        # Calculate overall score
        overall_score = sum(component.calculate() for component in components)
        overall_score = min(max(overall_score, 0), 1)  # Clamp to 0-1
        
        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)
        
        log.debug(f"Scored content from {source_type}: {overall_score:.3f} ({quality_level})")
        
        return {
            "overall_score": overall_score,
            "quality_level": quality_level,
            "components": [
                {
                    "factor": component.factor.value,
                    "weight": component.weight,
                    "value": component.value,
                    "weighted_value": component.calculate(),
                    "reasoning": component.reasoning,
                }
                for component in components
            ],
        }
    
    def _score_source_reliability(self, source_type: str) -> float:
        """Score source reliability"""
        return self.source_reliability_scores.get(source_type, 0.5)
    
    def _score_freshness(self, created_at: datetime) -> float:
        """Score content freshness based on age"""
        days_old = self._days_old(created_at)
        
        if days_old <= 30:
            return 1.0  # Very fresh
        elif days_old <= 90:
            return 0.9
        elif days_old <= 180:
            return 0.75
        elif days_old <= 365:
            return 0.5
        else:
            return max(0.2, 1.0 - (days_old / (365 * 2)))  # Slowly decay
    
    def _days_old(self, created_at: datetime) -> int:
        """Calculate days since creation"""
        return (datetime.utcnow() - created_at).days
    
    def _score_completeness(self, content: str, base_score: float) -> float:
        """Score content completeness based on length and structure"""
        # Content length as a factor
        word_count = len(content.split())
        length_score = min(word_count / 500, 1.0)  # Max score at 500+ words
        
        # Combine with base score
        return (length_score * 0.3) + (base_score * 0.7)
    
    def _determine_quality_level(self, score: float) -> ContentQuality:
        """Determine quality level from score"""
        if score >= 0.9:
            return ContentQuality.VERIFIED
        elif score >= 0.75:
            return ContentQuality.HIGH
        elif score >= 0.5:
            return ContentQuality.MEDIUM
        else:
            return ContentQuality.LOW
    
    def set_factor_weight(self, factor: ScoringFactors, weight: float) -> None:
        """Adjust weight for a scoring factor"""
        if not 0 <= weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
        
        self.factor_weights[factor] = weight
        
        # Normalize weights to sum to approximately 1
        total = sum(self.factor_weights.values())
        for key in self.factor_weights:
            self.factor_weights[key] /= total
        
        log.info(f"Updated weight for {factor}: {weight}")
    
    def set_source_reliability(self, source_type: str, reliability: float) -> None:
        """Set reliability score for a source type"""
        if not 0 <= reliability <= 1:
            raise ValueError("Reliability must be between 0 and 1")
        
        self.source_reliability_scores[source_type] = reliability
        log.info(f"Updated reliability for source '{source_type}': {reliability}")


# Global scorer instance
quality_scorer = QualityScorer()
