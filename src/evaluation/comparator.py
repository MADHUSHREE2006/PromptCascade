"""
Baseline Comparator
Compares adaptive cascade against always-X baseline strategies.
"""

import logging
from typing import List, Dict, Optional
from tqdm import tqdm

from dataset_loader import Problem
from strategies import (
    DirectStrategy, ReasoningStrategy, 
    VerificationStrategy, EnsembleStrategy
)
from evaluation.evaluator import Evaluator, EvaluationMetrics

logger = logging.getLogger(__name__)


class BaselineComparator:
    """
    Compares PromptCascade against baseline strategies:
    - Always-Direct
    - Always-Reasoning
    - Always-Verification
    - Always-Ensemble
    """
    
    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: LLM client for strategies
        """
        self.llm_client = llm_client
        
        # Initialize baseline strategies
        self.baselines = {
            'always_direct': DirectStrategy(llm_client),
            'always_reasoning': ReasoningStrategy(llm_client),
            'always_verification': VerificationStrategy(llm_client),
            'always_ensemble': EnsembleStrategy(llm_client)
        }
    
    def run_baseline(
        self,
        name: str,
        problems: List[Problem],
        show_progress: bool = True
    ) -> EvaluationMetrics:
        """
        Run a baseline strategy on a dataset.
        
        Args:
            name: Baseline name ('always_direct', etc.)
            problems: List of problems to evaluate
            show_progress: Show progress bar
            
        Returns:
            EvaluationMetrics
        """
        if name not in self.baselines:
            raise ValueError(f"Unknown baseline: {name}")
        
        strategy = self.baselines[name]
        evaluator = Evaluator()
        
        logger.info(f"Running baseline: {name}")
        
        iterator = tqdm(problems, desc=name) if show_progress else problems
        
        for problem in iterator:
            # Execute strategy
            result = strategy.execute(
                problem.query,
                ground_truth=problem.answer,
                difficulty=problem.difficulty
            )
            
            # Evaluate
            evaluator.evaluate_result(
                query=problem.query,
                predicted_answer=result.answer,
                ground_truth=problem.answer,
                strategy_name=name,
                tokens_used=result.tokens_used,
                latency=result.latency,
                cost_multiplier=strategy.get_cost_multiplier(),
                metadata={
                    'problem_id': problem.id,
                    'domain': problem.domain,
                    'difficulty': problem.difficulty
                }
            )
        
        metrics = evaluator.compute_metrics()
        logger.info(f"Baseline {name} completed: accuracy={metrics.accuracy:.3f}")
        
        return metrics
    
    def run_all_baselines(
        self,
        problems: List[Problem],
        show_progress: bool = True
    ) -> Dict[str, EvaluationMetrics]:
        """
        Run all baseline strategies.
        
        Args:
            problems: List of problems
            show_progress: Show progress bars
            
        Returns:
            Dictionary mapping baseline name to metrics
        """
        results = {}
        
        for name in self.baselines.keys():
            metrics = self.run_baseline(name, problems, show_progress)
            results[name] = metrics
        
        return results
    
    def compare_results(
        self,
        cascade_metrics: EvaluationMetrics,
        baseline_results: Dict[str, EvaluationMetrics]
    ) -> Dict:
        """
        Generate comparison report.
        
        Args:
            cascade_metrics: Metrics from adaptive cascade
            baseline_results: Metrics from baseline strategies
            
        Returns:
            Comparison dictionary
        """
        comparison = {
            'cascade': cascade_metrics.to_dict(),
            'baselines': {
                name: metrics.to_dict()
                for name, metrics in baseline_results.items()
            },
            'improvements': {}
        }
        
        # Compare cascade to each baseline
        for name, baseline_metrics in baseline_results.items():
            comparison['improvements'][name] = {
                'accuracy_delta': cascade_metrics.accuracy - baseline_metrics.accuracy,
                'cost_delta': cascade_metrics.total_cost - baseline_metrics.total_cost,
                'cost_reduction_pct': (
                    (baseline_metrics.total_cost - cascade_metrics.total_cost) /
                    baseline_metrics.total_cost * 100
                ),
                'efficiency_improvement': (
                    cascade_metrics.cost_efficiency / baseline_metrics.cost_efficiency - 1.0
                ) * 100
            }
        
        return comparison
    
    def print_comparison_table(
        self,
        cascade_metrics: EvaluationMetrics,
        baseline_results: Dict[str, EvaluationMetrics]
    ):
        """Print formatted comparison table"""
        print("\n" + "=" * 100)
        print("PromptCascade vs Baselines Comparison")
        print("=" * 100)
        
        # Header
        print(f"{'Strategy':<20} {'Accuracy':<12} {'Total Cost':<12} {'Cost Eff.':<12} {'Accuracy/1k':<15}")
        print("-" * 100)
        
        # Cascade
        print(
            f"{'Cascade (Ours)':<20} "
            f"{cascade_metrics.accuracy:<12.3f} "
            f"{cascade_metrics.total_cost:<12.2f} "
            f"{cascade_metrics.cost_efficiency:<12.3f} "
            f"{cascade_metrics.accuracy_per_1k_tokens:<15.3f}"
        )
        
        print("-" * 100)
        
        # Baselines
        for name, metrics in baseline_results.items():
            display_name = name.replace('always_', 'Always-').title()
            print(
                f"{display_name:<20} "
                f"{metrics.accuracy:<12.3f} "
                f"{metrics.total_cost:<12.2f} "
                f"{metrics.cost_efficiency:<12.3f} "
                f"{metrics.accuracy_per_1k_tokens:<15.3f}"
            )
        
        print("=" * 100)
        
        # Improvements
        print("\nImprovements over Baselines:")
        print("-" * 100)
        
        for name, metrics in baseline_results.items():
            display_name = name.replace('always_', 'Always-').title()
            acc_delta = cascade_metrics.accuracy - metrics.accuracy
            cost_delta = cascade_metrics.total_cost - metrics.total_cost
            cost_reduction = (metrics.total_cost - cascade_metrics.total_cost) / metrics.total_cost * 100
            
            print(f"{display_name}:")
            print(f"  Accuracy: {acc_delta:+.3f} ({acc_delta/metrics.accuracy*100:+.1f}%)")
            print(f"  Cost: {cost_delta:+.2f} units ({cost_reduction:+.1f}% reduction)")
            print()
        
        print("=" * 100)


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    from ..dataset_loader import DatasetLoader
    
    # Create test dataset
    loader = DatasetLoader()
    problems = loader.create_combined_dataset(samples_per_domain=10)
    
    # Run comparison
    comparator = BaselineComparator()
    
    print("Running baselines (this may take a while)...")
    baseline_results = comparator.run_all_baselines(problems[:20])  # Small subset for demo
    
    # Create mock cascade metrics for demonstration
    from .evaluator import EvaluationMetrics
    cascade_metrics = EvaluationMetrics(
        accuracy=0.85,
        total_latency=45.0,
        total_tokens=5000,
        total_cost=50.0,
        accuracy_per_1k_tokens=3.4,
        avg_latency_per_query=2.25,
        cost_efficiency=0.017,
        strategy_distribution={'direct': 0.3, 'reasoning': 0.4, 'verification': 0.2, 'ensemble': 0.1},
        strategy_accuracy={'direct': 0.9, 'reasoning': 0.85, 'verification': 0.8, 'ensemble': 0.75},
        num_queries=20,
        expensive_stage_rate=0.3
    )
    
    # Print comparison
    comparator.print_comparison_table(cascade_metrics, baseline_results)
