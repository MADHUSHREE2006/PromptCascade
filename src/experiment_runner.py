"""
Experiment Runner
Orchestrates experiments, ablation studies, and comprehensive evaluations.
"""

import json
import os
import time
import yaml
import logging
from typing import Dict, List, Optional
from datetime import datetime
from tqdm import tqdm

from dataset_loader import DatasetLoader, Problem
from difficulty_estimator import DifficultyEstimator
from prompt_router import PromptRouter, PromptStrategy
from strategies import DirectStrategy, ReasoningStrategy, VerificationStrategy, EnsembleStrategy
from evaluation import Evaluator, BaselineComparator

logger = logging.getLogger(__name__)


class ExperimentRunner:
    """
    Runs comprehensive experiments for PromptCascade research.
    
    Features:
    - Full cascade evaluation
    - Baseline comparisons
    - Ablation studies
    - Multiple runs with statistical analysis
    - Result persistence
    """
    
    def __init__(self, config_path: str = "config.yaml", llm_client=None):
        """
        Args:
            config_path: Path to configuration file
            llm_client: LLM client for strategies
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.llm_client = llm_client
        
        # Initialize components
        self.dataset_loader = DatasetLoader()
        self.difficulty_estimator = DifficultyEstimator()
        self.prompt_router = PromptRouter(self.difficulty_estimator)
        
        # Initialize strategies
        self.strategies = {
            PromptStrategy.DIRECT: DirectStrategy(llm_client),
            PromptStrategy.REASONING: ReasoningStrategy(llm_client),
            PromptStrategy.VERIFICATION: VerificationStrategy(llm_client),
            PromptStrategy.ENSEMBLE: EnsembleStrategy(llm_client)
        }
        
        # Experiment tracking
        self.experiment_id = None
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def run_cascade_experiment(
        self,
        problems: List[Problem],
        experiment_name: str = "cascade",
        show_progress: bool = True
    ) -> Evaluator:
        """
        Run adaptive cascade experiment.
        
        Args:
            problems: List of problems to evaluate
            experiment_name: Name of experiment
            show_progress: Show progress bar
            
        Returns:
            Evaluator with results
        """
        logger.info(f"Running cascade experiment: {experiment_name}")
        
        evaluator = Evaluator()
        iterator = tqdm(problems, desc="Cascade") if show_progress else problems
        
        for problem in iterator:
            # Route query
            decision = self.prompt_router.route(
                problem.query,
                metadata={'domain': problem.domain, 'ground_truth_difficulty': problem.difficulty}
            )
            
            # Execute selected strategy
            strategy = self.strategies[decision.strategy]
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
                strategy_name=decision.strategy.value,
                tokens_used=result.tokens_used,
                latency=result.latency,
                cost_multiplier=decision.estimated_cost,
                metadata={
                    'problem_id': problem.id,
                    'domain': problem.domain,
                    'ground_truth_difficulty': problem.difficulty,
                    'predicted_difficulty': decision.difficulty_score,
                    'routing_confidence': decision.confidence
                }
            )
        
        logger.info(f"Cascade experiment completed")
        return evaluator
    
    def run_full_evaluation(
        self,
        problems: List[Problem],
        run_baselines: bool = True,
        experiment_name: Optional[str] = None
    ) -> Dict:
        """
        Run full evaluation: cascade + baselines.
        
        Args:
            problems: List of problems
            run_baselines: Whether to run baseline comparisons
            experiment_name: Optional experiment name
            
        Returns:
            Dictionary of results
        """
        if experiment_name is None:
            experiment_name = f"full_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.experiment_id = experiment_name
        logger.info(f"Starting full evaluation: {experiment_name}")
        
        results = {
            'experiment_id': experiment_name,
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'dataset_size': len(problems)
        }
        
        # Run cascade
        print("\n" + "=" * 70)
        print("Running Adaptive Cascade")
        print("=" * 70)
        cascade_evaluator = self.run_cascade_experiment(problems, experiment_name)
        cascade_metrics = cascade_evaluator.compute_metrics()
        results['cascade'] = cascade_metrics.to_dict()
        results['cascade_detailed'] = cascade_evaluator.get_detailed_statistics()
        
        # Run baselines
        if run_baselines:
            print("\n" + "=" * 70)
            print("Running Baseline Comparisons")
            print("=" * 70)
            
            comparator = BaselineComparator(self.llm_client)
            baseline_results = comparator.run_all_baselines(problems)
            
            results['baselines'] = {
                name: metrics.to_dict()
                for name, metrics in baseline_results.items()
            }
            
            # Generate comparison
            comparison = comparator.compare_results(cascade_metrics, baseline_results)
            results['comparison'] = comparison
            
            # Print comparison table
            comparator.print_comparison_table(cascade_metrics, baseline_results)
        
        # Save results
        self._save_results(results, experiment_name)
        
        return results
    
    def run_ablation_study(
        self,
        problems: List[Problem],
        experiment_name: Optional[str] = None
    ) -> Dict:
        """
        Run ablation study by removing features one at a time.
        
        Args:
            problems: List of problems
            experiment_name: Optional experiment name
            
        Returns:
            Ablation study results
        """
        if experiment_name is None:
            experiment_name = f"ablation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting ablation study: {experiment_name}")
        
        print("\n" + "=" * 70)
        print("Ablation Study")
        print("=" * 70)
        
        results = {
            'experiment_id': experiment_name,
            'timestamp': datetime.now().isoformat(),
            'ablations': {}
        }
        
        # Baseline: full model
        print("\nBaseline: Full Model")
        print("-" * 70)
        full_evaluator = self.run_cascade_experiment(problems, "full_model", show_progress=True)
        full_metrics = full_evaluator.compute_metrics()
        results['full_model'] = full_metrics.to_dict()
        
        # Define ablations
        ablations = {
            'no_confidence': 'Remove predicted confidence feature',
            'no_task_family': 'Remove task family (domain) feature',
            'no_historical': 'Remove historical performance feature',
            'random_routing': 'Replace routing with random strategy selection'
        }
        
        for ablation_name, description in ablations.items():
            print(f"\nAblation: {ablation_name}")
            print(f"Description: {description}")
            print("-" * 70)
            
            # Run with ablation (simplified - would need to modify estimator)
            ablation_evaluator = self._run_with_ablation(problems, ablation_name)
            ablation_metrics = ablation_evaluator.compute_metrics()
            
            # Compute degradation
            degradation = {
                'accuracy_loss': full_metrics.accuracy - ablation_metrics.accuracy,
                'cost_increase': ablation_metrics.total_cost - full_metrics.total_cost,
                'efficiency_loss': full_metrics.cost_efficiency - ablation_metrics.cost_efficiency
            }
            
            results['ablations'][ablation_name] = {
                'description': description,
                'metrics': ablation_metrics.to_dict(),
                'degradation': degradation
            }
            
            print(f"  Accuracy loss: {degradation['accuracy_loss']:+.3f}")
            print(f"  Cost increase: {degradation['cost_increase']:+.2f}")
        
        # Save results
        self._save_results(results, experiment_name)
        
        return results
    
    def _run_with_ablation(self, problems: List[Problem], ablation_type: str) -> Evaluator:
        """Run experiment with specific feature ablated"""
        # Simplified implementation - would need proper feature masking
        if ablation_type == 'random_routing':
            # Random routing
            import random
            evaluator = Evaluator()
            
            for problem in tqdm(problems, desc=ablation_type):
                # Randomly select strategy
                strategy_enum = random.choice(list(PromptStrategy))
                strategy = self.strategies[strategy_enum]
                result = strategy.execute(
                    problem.query,
                    ground_truth=problem.answer,
                    difficulty=problem.difficulty
                )
                
                evaluator.evaluate_result(
                    query=problem.query,
                    predicted_answer=result.answer,
                    ground_truth=problem.answer,
                    strategy_name=strategy_enum.value,
                    tokens_used=result.tokens_used,
                    latency=result.latency,
                    cost_multiplier=strategy.get_cost_multiplier()
                )
            
            return evaluator
        else:
            # For other ablations, use full model (in real implementation, would mask features)
            logger.warning(f"Ablation {ablation_type} not fully implemented. Using full model.")
            return self.run_cascade_experiment(problems, ablation_type, show_progress=True)
    
    def run_multiple_trials(
        self,
        problems: List[Problem],
        num_trials: int = 5,
        experiment_name: Optional[str] = None
    ) -> Dict:
        """
        Run multiple trials for statistical significance.
        
        Args:
            problems: List of problems
            num_trials: Number of trials to run
            experiment_name: Optional experiment name
            
        Returns:
            Aggregated results across trials
        """
        if experiment_name is None:
            experiment_name = f"multi_trial_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Running {num_trials} trials: {experiment_name}")
        
        results = {
            'experiment_id': experiment_name,
            'num_trials': num_trials,
            'trials': []
        }
        
        for trial in range(num_trials):
            print(f"\n{'='*70}")
            print(f"Trial {trial + 1}/{num_trials}")
            print(f"{'='*70}")
            
            trial_results = self.run_full_evaluation(
                problems,
                run_baselines=True,
                experiment_name=f"{experiment_name}_trial{trial+1}"
            )
            
            results['trials'].append(trial_results)
        
        # Aggregate statistics
        results['aggregated'] = self._aggregate_trials(results['trials'])
        
        # Save aggregated results
        self._save_results(results, f"{experiment_name}_aggregated")
        
        return results
    
    def _aggregate_trials(self, trials: List[Dict]) -> Dict:
        """Aggregate results across multiple trials"""
        import numpy as np
        
        # Extract cascade metrics from each trial
        cascade_accuracies = [t['cascade']['accuracy'] for t in trials]
        cascade_costs = [t['cascade']['total_cost'] for t in trials]
        
        aggregated = {
            'cascade': {
                'accuracy_mean': np.mean(cascade_accuracies),
                'accuracy_std': np.std(cascade_accuracies),
                'accuracy_min': np.min(cascade_accuracies),
                'accuracy_max': np.max(cascade_accuracies),
                'cost_mean': np.mean(cascade_costs),
                'cost_std': np.std(cascade_costs)
            }
        }
        
        # Aggregate baselines if available
        if 'baselines' in trials[0]:
            aggregated['baselines'] = {}
            for baseline_name in trials[0]['baselines'].keys():
                baseline_accuracies = [
                    t['baselines'][baseline_name]['accuracy'] for t in trials
                ]
                baseline_costs = [
                    t['baselines'][baseline_name]['total_cost'] for t in trials
                ]
                
                aggregated['baselines'][baseline_name] = {
                    'accuracy_mean': np.mean(baseline_accuracies),
                    'accuracy_std': np.std(baseline_accuracies),
                    'cost_mean': np.mean(baseline_costs),
                    'cost_std': np.std(baseline_costs)
                }
        
        return aggregated
    
    def _save_results(self, results: Dict, experiment_name: str):
        """Save results to file"""
        filepath = os.path.join(self.results_dir, f"{experiment_name}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {filepath}")
        print(f"\nResults saved to: {filepath}")


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    # Create experiment runner
    runner = ExperimentRunner()
    
    # Generate test dataset
    print("Generating dataset...")
    dataset = runner.dataset_loader.create_combined_dataset(samples_per_domain=25)
    train, val, test = runner.dataset_loader.split_dataset(dataset)
    
    # Run quick evaluation on validation set
    print(f"\nRunning evaluation on {len(val)} problems...")
    results = runner.run_full_evaluation(val, run_baselines=True, experiment_name="demo_eval")
    
    print("\n" + "=" * 70)
    print("Experiment completed successfully!")
    print("=" * 70)
