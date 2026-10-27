"""
Prompt Strategy Router
Routes queries to appropriate prompting strategies based on difficulty estimation.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from difficulty_estimator import DifficultyEstimator, DifficultyFeatures

logger = logging.getLogger(__name__)


class PromptStrategy(Enum):
    """Enumeration of available prompt strategies"""
    DIRECT = "direct"
    REASONING = "reasoning"
    VERIFICATION = "verification"
    ENSEMBLE = "ensemble"


@dataclass
class RoutingDecision:
    """Container for routing decision information"""
    strategy: PromptStrategy
    difficulty_score: float
    difficulty_category: str
    confidence: float
    estimated_cost: float
    features: Optional[DifficultyFeatures] = None
    reasoning: str = ""


class PromptRouter:
    """
    Routes queries to appropriate prompt strategies using cascade logic.
    
    Cascade Strategy:
    - Easy (< 0.3): Direct prompting
    - Moderate (0.3-0.6): Structured reasoning (Chain-of-Thought)
    - Hard (0.6-0.85): Reasoning + Verification
    - Very Hard (> 0.85): Multiple candidates + Verifier (Ensemble)
    """
    
    def __init__(
        self,
        difficulty_estimator: Optional[DifficultyEstimator] = None,
        thresholds: Optional[Dict[str, float]] = None,
        cost_multipliers: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            difficulty_estimator: DifficultyEstimator instance
            thresholds: Custom difficulty thresholds
            cost_multipliers: Cost multipliers for each strategy
        """
        self.difficulty_estimator = difficulty_estimator or DifficultyEstimator()
        
        # Default thresholds
        self.thresholds = thresholds or {
            'easy': 0.3,
            'moderate': 0.6,
            'hard': 0.85
        }
        
        # Default cost multipliers (relative to direct prompting)
        self.cost_multipliers = cost_multipliers or {
            PromptStrategy.DIRECT: 1.0,
            PromptStrategy.REASONING: 2.5,
            PromptStrategy.VERIFICATION: 4.0,
            PromptStrategy.ENSEMBLE: 6.0
        }
        
        # Statistics tracking
        self.routing_stats = {
            PromptStrategy.DIRECT: 0,
            PromptStrategy.REASONING: 0,
            PromptStrategy.VERIFICATION: 0,
            PromptStrategy.ENSEMBLE: 0
        }
        
        self.total_routed = 0
    
    def route(
        self, 
        query: str, 
        metadata: Optional[Dict] = None,
        return_features: bool = False
    ) -> RoutingDecision:
        """
        Route a query to the appropriate prompt strategy.
        
        Args:
            query: Input question/problem
            metadata: Optional metadata (domain, historical performance)
            return_features: Whether to include features in decision
            
        Returns:
            RoutingDecision with strategy and supporting information
        """
        # Estimate difficulty
        difficulty_score, features = self.difficulty_estimator.estimate_difficulty(
            query, metadata, return_features=True
        )
        
        # Categorize
        difficulty_category = self.difficulty_estimator.categorize_difficulty(difficulty_score)
        
        # Select strategy based on difficulty
        if difficulty_score < self.thresholds['easy']:
            strategy = PromptStrategy.DIRECT
            reasoning = "Query is straightforward; direct prompting should suffice"
        elif difficulty_score < self.thresholds['moderate']:
            strategy = PromptStrategy.REASONING
            reasoning = "Query requires structured reasoning (Chain-of-Thought)"
        elif difficulty_score < self.thresholds['hard']:
            strategy = PromptStrategy.VERIFICATION
            reasoning = "Complex query requires reasoning with self-verification"
        else:
            strategy = PromptStrategy.ENSEMBLE
            reasoning = "Very difficult query requires multiple attempts with verification"
        
        # Get confidence
        confidence = self.difficulty_estimator.get_confidence(difficulty_score, features)
        
        # Estimate cost
        estimated_cost = self.cost_multipliers[strategy]
        
        # Update statistics
        self.routing_stats[strategy] += 1
        self.total_routed += 1
        
        # Log decision
        logger.info(
            f"Routed to {strategy.value}: difficulty={difficulty_score:.3f}, "
            f"category={difficulty_category}, confidence={confidence:.3f}"
        )
        
        return RoutingDecision(
            strategy=strategy,
            difficulty_score=difficulty_score,
            difficulty_category=difficulty_category,
            confidence=confidence,
            estimated_cost=estimated_cost,
            features=features if return_features else None,
            reasoning=reasoning
        )
    
    def route_batch(
        self, 
        queries: List[str], 
        metadata_list: Optional[List[Dict]] = None
    ) -> List[RoutingDecision]:
        """
        Route multiple queries efficiently.
        
        Args:
            queries: List of queries
            metadata_list: Optional list of metadata dicts
            
        Returns:
            List of RoutingDecisions
        """
        if metadata_list is None:
            metadata_list = [None] * len(queries)
        
        decisions = []
        for query, metadata in zip(queries, metadata_list):
            decision = self.route(query, metadata)
            decisions.append(decision)
        
        return decisions
    
    def get_statistics(self) -> Dict:
        """Get routing statistics"""
        if self.total_routed == 0:
            return {
                'total_routed': 0,
                'strategy_distribution': {}
            }
        
        distribution = {
            strategy.value: count / self.total_routed 
            for strategy, count in self.routing_stats.items()
        }
        
        return {
            'total_routed': self.total_routed,
            'strategy_distribution': distribution,
            'strategy_counts': {k.value: v for k, v in self.routing_stats.items()}
        }
    
    def reset_statistics(self):
        """Reset routing statistics"""
        self.routing_stats = {
            PromptStrategy.DIRECT: 0,
            PromptStrategy.REASONING: 0,
            PromptStrategy.VERIFICATION: 0,
            PromptStrategy.ENSEMBLE: 0
        }
        self.total_routed = 0
    
    def optimize_thresholds(
        self, 
        validation_data: List[Tuple[str, float, bool]],
        cost_weight: float = 0.3
    ) -> Dict[str, float]:
        """
        Optimize routing thresholds based on validation data.
        
        Args:
            validation_data: List of (query, ground_truth_difficulty, success)
            cost_weight: Weight for cost in optimization (0-1)
            
        Returns:
            Optimized thresholds
        """
        # Grid search over threshold combinations
        best_thresholds = self.thresholds.copy()
        best_score = float('-inf')
        
        for easy_thresh in [0.2, 0.25, 0.3, 0.35, 0.4]:
            for mod_thresh in [0.5, 0.55, 0.6, 0.65, 0.7]:
                for hard_thresh in [0.75, 0.8, 0.85, 0.9]:
                    if easy_thresh >= mod_thresh or mod_thresh >= hard_thresh:
                        continue
                    
                    # Test these thresholds
                    self.thresholds = {
                        'easy': easy_thresh,
                        'moderate': mod_thresh,
                        'hard': hard_thresh
                    }
                    
                    # Evaluate
                    total_cost = 0
                    correct = 0
                    
                    for query, true_diff, success in validation_data:
                        decision = self.route(query)
                        total_cost += decision.estimated_cost
                        
                        # Check if routing was appropriate
                        if success and decision.difficulty_score <= true_diff + 0.1:
                            correct += 1
                        elif not success and decision.difficulty_score >= true_diff - 0.1:
                            correct += 1
                    
                    # Compute score (accuracy - cost_weight * normalized_cost)
                    accuracy = correct / len(validation_data)
                    normalized_cost = total_cost / (len(validation_data) * 6.0)  # Max cost
                    score = accuracy - cost_weight * normalized_cost
                    
                    if score > best_score:
                        best_score = score
                        best_thresholds = {
                            'easy': easy_thresh,
                            'moderate': mod_thresh,
                            'hard': hard_thresh
                        }
        
        # Set best thresholds
        self.thresholds = best_thresholds
        logger.info(f"Optimized thresholds: {best_thresholds} (score: {best_score:.4f})")
        
        return best_thresholds
    
    def explain_routing(self, decision: RoutingDecision) -> str:
        """
        Generate human-readable explanation of routing decision.
        
        Args:
            decision: RoutingDecision to explain
            
        Returns:
            Explanation string
        """
        explanation = f"""
Routing Decision Explanation:
-----------------------------
Selected Strategy: {decision.strategy.value.upper()}
Difficulty Score: {decision.difficulty_score:.3f} ({decision.difficulty_category})
Confidence: {decision.confidence:.3f}
Estimated Cost: {decision.estimated_cost:.1f}x baseline

Reasoning: {decision.reasoning}

Feature Breakdown:
"""
        
        if decision.features:
            features = decision.features
            explanation += f"  - Query Length: {features.query_length} words\n"
            explanation += f"  - Lexical Complexity: {features.lexical_complexity:.3f}\n"
            explanation += f"  - Syntactic Depth: {features.syntactic_depth}\n"
            explanation += f"  - Numerical Complexity: {features.numerical_complexity:.3f}\n"
            explanation += f"  - Domain Specificity: {features.domain_specificity:.3f}\n"
            explanation += f"  - Keyword Density: {features.keyword_density:.3f}\n"
            explanation += f"  - Question Complexity: {features.question_complexity:.3f}\n"
        
        return explanation


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    router = PromptRouter()
    
    # Test queries
    test_queries = [
        "What is 2 + 2?",
        "Explain how a binary search tree works.",
        "Prove that the square root of 2 is irrational.",
        "Derive and implement a solution to the traveling salesman problem using dynamic programming, analyze its time and space complexity, and compare it with approximation algorithms.",
    ]
    
    print("=" * 70)
    print("Prompt Strategy Router Demo")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 70)
        
        decision = router.route(query, return_features=True)
        print(router.explain_routing(decision))
    
    # Display statistics
    print("\n" + "=" * 70)
    print("Routing Statistics")
    print("=" * 70)
    stats = router.get_statistics()
    print(f"Total Routed: {stats['total_routed']}")
    print("\nStrategy Distribution:")
    for strategy, percentage in stats['strategy_distribution'].items():
        print(f"  {strategy}: {percentage*100:.1f}%")
