"""
Evaluation Framework
Tracks and computes metrics for PromptCascade experiments.
"""

import json
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics"""
    # Primary metrics
    accuracy: float
    total_latency: float
    total_tokens: int
    total_cost: float  # Normalized cost units
    
    # Derived metrics
    accuracy_per_1k_tokens: float
    avg_latency_per_query: float
    cost_efficiency: float  # accuracy / cost
    
    # Strategy-specific metrics
    strategy_distribution: Dict[str, float]
    strategy_accuracy: Dict[str, float]
    
    # Additional metrics
    num_queries: int
    expensive_stage_rate: float  # % queries routed to verification/ensemble
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def __str__(self) -> str:
        """String representation"""
        return f"""
Evaluation Metrics:
------------------
Accuracy: {self.accuracy:.3f}
Total Latency: {self.total_latency:.2f}s
Total Tokens: {self.total_tokens:,}
Total Cost: {self.total_cost:.2f} units
Accuracy per 1k Tokens: {self.accuracy_per_1k_tokens:.3f}
Avg Latency per Query: {self.avg_latency_per_query:.2f}s
Cost Efficiency: {self.cost_efficiency:.3f}
Expensive Stage Rate: {self.expensive_stage_rate:.1%}
Queries Evaluated: {self.num_queries}
"""


class Evaluator:
    """
    Evaluates prompting strategies on a dataset.
    
    Tracks multiple metrics:
    - Accuracy (correct answers)
    - Latency (response time)
    - Tokens (computational cost)
    - Cost efficiency (accuracy per token)
    - Strategy distribution
    """
    
    def __init__(self):
        """Initialize evaluator"""
        self.results = []
        self.reset()
    
    def reset(self):
        """Reset evaluation state"""
        self.results = []
        self.total_tokens = 0
        self.total_latency = 0.0
        self.total_cost = 0.0
        self.correct_count = 0
        self.total_queries = 0
        
        # Track by strategy
        self.strategy_counts = defaultdict(int)
        self.strategy_correct = defaultdict(int)
        self.strategy_tokens = defaultdict(int)
        self.strategy_latency = defaultdict(float)
    
    def evaluate_result(
        self, 
        query: str,
        predicted_answer: str,
        ground_truth: Optional[str],
        strategy_name: str,
        tokens_used: int,
        latency: float,
        cost_multiplier: float,
        metadata: Optional[Dict] = None
    ):
        """
        Evaluate a single result.
        
        Args:
            query: Input query
            predicted_answer: Model's answer
            ground_truth: Correct answer (if available)
            strategy_name: Strategy used
            tokens_used: Tokens consumed
            latency: Response time
            cost_multiplier: Strategy cost multiplier
            metadata: Additional metadata
        """
        # Check correctness (simplified - in practice would use better matching)
        is_correct = self._check_correctness(predicted_answer, ground_truth)
        
        # Update totals
        self.total_queries += 1
        self.total_tokens += tokens_used
        self.total_latency += latency
        self.total_cost += cost_multiplier
        
        if is_correct:
            self.correct_count += 1
        
        # Update strategy-specific metrics
        self.strategy_counts[strategy_name] += 1
        self.strategy_tokens[strategy_name] += tokens_used
        self.strategy_latency[strategy_name] += latency
        
        if is_correct:
            self.strategy_correct[strategy_name] += 1
        
        # Store result
        result = {
            'query': query,
            'predicted_answer': predicted_answer,
            'ground_truth': ground_truth,
            'is_correct': is_correct,
            'strategy': strategy_name,
            'tokens_used': tokens_used,
            'latency': latency,
            'cost_multiplier': cost_multiplier,
            'metadata': metadata or {}
        }
        
        self.results.append(result)
        
        logger.debug(
            f"Evaluated: {strategy_name} - "
            f"{'CORRECT' if is_correct else 'WRONG'} - "
            f"{tokens_used} tokens - {latency:.2f}s"
        )
    
    def _check_correctness(
        self, 
        predicted: str, 
        ground_truth: Optional[str]
    ) -> bool:
        """
        Check if answer is correct.
        
        Args:
            predicted: Predicted answer
            ground_truth: Ground truth answer
            
        Returns:
            True if correct (or if no ground truth available)
        """
        if ground_truth is None:
            # No ground truth available — cannot evaluate, treat as incorrect
            return False
        
        # Simple string matching (case-insensitive, strip whitespace)
        predicted_clean = predicted.lower().strip()
        truth_clean = ground_truth.lower().strip()
        
        # Exact match
        if predicted_clean == truth_clean:
            return True
        
        # Check if truth is contained in prediction
        if truth_clean in predicted_clean:
            return True
        
        # Numeric comparison (for math problems)
        try:
            pred_num = float(predicted_clean.split()[0])
            truth_num = float(truth_clean.split()[0])
            if abs(pred_num - truth_num) < 0.01:
                return True
        except (ValueError, IndexError):
            pass
        
        return False
    
    def compute_metrics(self) -> EvaluationMetrics:
        """
        Compute comprehensive evaluation metrics.
        
        Returns:
            EvaluationMetrics object
        """
        if self.total_queries == 0:
            logger.warning("No queries evaluated yet")
            return EvaluationMetrics(
                accuracy=0.0,
                total_latency=0.0,
                total_tokens=0,
                total_cost=0.0,
                accuracy_per_1k_tokens=0.0,
                avg_latency_per_query=0.0,
                cost_efficiency=0.0,
                strategy_distribution={},
                strategy_accuracy={},
                num_queries=0,
                expensive_stage_rate=0.0
            )
        
        # Primary metrics
        accuracy = self.correct_count / self.total_queries
        avg_latency = self.total_latency / self.total_queries
        
        # Derived metrics
        accuracy_per_1k_tokens = (accuracy * 1000.0) / max(self.total_tokens / self.total_queries, 1)
        cost_efficiency = accuracy / max(self.total_cost, 1e-6)
        
        # Strategy distribution
        strategy_dist = {
            strategy: count / self.total_queries
            for strategy, count in self.strategy_counts.items()
        }
        
        # Strategy-specific accuracy
        strategy_acc = {
            strategy: self.strategy_correct[strategy] / max(count, 1)
            for strategy, count in self.strategy_counts.items()
        }
        
        # Expensive stage rate (verification + ensemble)
        expensive_count = (
            self.strategy_counts.get('verification', 0) +
            self.strategy_counts.get('ensemble', 0)
        )
        expensive_stage_rate = expensive_count / self.total_queries
        
        return EvaluationMetrics(
            accuracy=accuracy,
            total_latency=self.total_latency,
            total_tokens=self.total_tokens,
            total_cost=self.total_cost,
            accuracy_per_1k_tokens=accuracy_per_1k_tokens,
            avg_latency_per_query=avg_latency,
            cost_efficiency=cost_efficiency,
            strategy_distribution=strategy_dist,
            strategy_accuracy=strategy_acc,
            num_queries=self.total_queries,
            expensive_stage_rate=expensive_stage_rate
        )
    
    def get_detailed_statistics(self) -> Dict:
        """Get detailed statistics breakdown"""
        metrics = self.compute_metrics()
        
        stats = {
            'summary': metrics.to_dict(),
            'by_strategy': {},
            'pareto_frontier': self._compute_pareto_frontier()
        }
        
        # Per-strategy breakdown
        for strategy in self.strategy_counts.keys():
            count = self.strategy_counts[strategy]
            if count == 0:
                continue
            
            stats['by_strategy'][strategy] = {
                'count': count,
                'percentage': count / self.total_queries,
                'accuracy': self.strategy_correct[strategy] / count,
                'avg_tokens': self.strategy_tokens[strategy] / count,
                'avg_latency': self.strategy_latency[strategy] / count
            }
        
        return stats
    
    def _compute_pareto_frontier(self) -> List[Dict]:
        """
        Compute quality-compute Pareto frontier.
        
        Returns:
            List of points on the Pareto frontier
        """
        # Group results by strategy
        strategy_points = {}
        
        for strategy in self.strategy_counts.keys():
            count = self.strategy_counts[strategy]
            if count == 0:
                continue
            
            accuracy = self.strategy_correct[strategy] / count
            cost = self.strategy_tokens[strategy] / count
            
            strategy_points[strategy] = {
                'strategy': strategy,
                'accuracy': accuracy,
                'cost': cost,
                'cost_efficiency': accuracy / max(cost, 1)
            }
        
        # Sort by cost
        points = sorted(strategy_points.values(), key=lambda x: x['cost'])
        
        # Find Pareto frontier (non-dominated points)
        frontier = []
        max_accuracy_seen = -1
        
        for point in points:
            if point['accuracy'] > max_accuracy_seen:
                frontier.append(point)
                max_accuracy_seen = point['accuracy']
        
        return frontier
    
    def save_results(self, filepath: str):
        """Save evaluation results to file"""
        output = {
            'metrics': self.compute_metrics().to_dict(),
            'detailed_statistics': self.get_detailed_statistics(),
            'individual_results': self.results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Saved evaluation results to {filepath}")
    
    def load_results(self, filepath: str):
        """Load evaluation results from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.results = data.get('individual_results', [])
        
        # Reconstruct state from results
        self.reset()
        for result in self.results:
            self.total_queries += 1
            self.total_tokens += result['tokens_used']
            self.total_latency += result['latency']
            self.total_cost += result['cost_multiplier']
            
            if result['is_correct']:
                self.correct_count += 1
                self.strategy_correct[result['strategy']] += 1
            
            self.strategy_counts[result['strategy']] += 1
            self.strategy_tokens[result['strategy']] += result['tokens_used']
            self.strategy_latency[result['strategy']] += result['latency']
        
        logger.info(f"Loaded evaluation results from {filepath}")
    
    def compare_to_baseline(
        self, 
        baseline_metrics: EvaluationMetrics
    ) -> Dict:
        """
        Compare current metrics to a baseline.
        
        Args:
            baseline_metrics: Baseline metrics to compare against
            
        Returns:
            Dictionary of comparisons
        """
        current_metrics = self.compute_metrics()
        
        comparison = {
            'accuracy_improvement': current_metrics.accuracy - baseline_metrics.accuracy,
            'accuracy_improvement_pct': (
                (current_metrics.accuracy - baseline_metrics.accuracy) / 
                max(baseline_metrics.accuracy, 1e-6) * 100
            ),
            'cost_reduction': baseline_metrics.total_cost - current_metrics.total_cost,
            'cost_reduction_pct': (
                (baseline_metrics.total_cost - current_metrics.total_cost) /
                max(baseline_metrics.total_cost, 1e-6) * 100
            ),
            'efficiency_improvement': (
                current_metrics.cost_efficiency - baseline_metrics.cost_efficiency
            ),
            'latency_change': current_metrics.total_latency - baseline_metrics.total_latency
        }
        
        return comparison


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    evaluator = Evaluator()
    
    # Simulate some evaluations
    test_cases = [
        ("What is 2+2?", "4", "4", "direct", 50, 0.5, 1.0),
        ("Explain recursion", "A function calling itself", "Recursion is when a function calls itself", "reasoning", 150, 1.5, 2.5),
        ("Prove theorem", "Proof by induction...", "Correct proof", "verification", 300, 3.0, 4.0),
    ]
    
    for query, answer, truth, strategy, tokens, latency, cost in test_cases:
        evaluator.evaluate_result(
            query=query,
            predicted_answer=answer,
            ground_truth=truth,
            strategy_name=strategy,
            tokens_used=tokens,
            latency=latency,
            cost_multiplier=cost
        )
    
    # Compute and display metrics
    metrics = evaluator.compute_metrics()
    print(metrics)
    
    # Display detailed statistics
    stats = evaluator.get_detailed_statistics()
    print("\nPareto Frontier:")
    for point in stats['pareto_frontier']:
        print(f"  {point['strategy']}: accuracy={point['accuracy']:.3f}, cost={point['cost']:.1f}")
