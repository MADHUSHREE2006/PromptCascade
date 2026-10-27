"""
Visualization Tools for PromptCascade
Generates plots and charts for research paper.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11


class PromptCascadeVisualizer:
    """
    Visualization tools for PromptCascade experiments.
    
    Generates:
    - Pareto frontier plots
    - Strategy distribution charts
    - Accuracy comparisons
    - Cost analysis
    - Ablation study results
    """
    
    def __init__(self, output_dir: str = "results/figures"):
        """
        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_pareto_frontier(
        self,
        results: Dict,
        save_path: Optional[str] = None
    ):
        """
        Plot quality-compute Pareto frontier.
        
        Args:
            results: Experiment results dictionary
            save_path: Optional path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Extract Pareto frontier points
        if 'cascade_detailed' in results and 'pareto_frontier' in results['cascade_detailed']:
            frontier = results['cascade_detailed']['pareto_frontier']
            
            strategies = [p['strategy'] for p in frontier]
            accuracies = [p['accuracy'] for p in frontier]
            costs = [p['cost'] for p in frontier]
            
            # Plot frontier
            ax.plot(costs, accuracies, 'b-o', linewidth=2, markersize=10, 
                   label='Pareto Frontier', zorder=3)
            
            # Annotate points
            for strategy, acc, cost in zip(strategies, accuracies, costs):
                ax.annotate(strategy.capitalize(), (cost, acc),
                           textcoords="offset points", xytext=(10, 5),
                           ha='left', fontsize=10, weight='bold')
        
        # Add baseline points
        if 'baselines' in results:
            baseline_names = []
            baseline_costs = []
            baseline_accs = []
            
            for name, metrics in results['baselines'].items():
                baseline_names.append(name.replace('always_', '').capitalize())
                baseline_costs.append(metrics['total_cost'] / metrics['num_queries'])
                baseline_accs.append(metrics['accuracy'])
            
            ax.scatter(baseline_costs, baseline_accs, s=150, c='red', 
                      marker='s', alpha=0.6, label='Baselines', zorder=2)
            
            for name, cost, acc in zip(baseline_names, baseline_costs, baseline_accs):
                ax.annotate(name, (cost, acc),
                           textcoords="offset points", xytext=(-10, -15),
                           ha='right', fontsize=9, style='italic')
        
        ax.set_xlabel('Average Cost per Query (tokens)', fontsize=12, weight='bold')
        ax.set_ylabel('Accuracy', fontsize=12, weight='bold')
        ax.set_title('PromptCascade: Quality-Compute Pareto Frontier', 
                    fontsize=14, weight='bold', pad=20)
        ax.legend(fontsize=11, loc='lower right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved Pareto frontier to {save_path}")
        else:
            plt.savefig(os.path.join(self.output_dir, 'pareto_frontier.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_strategy_distribution(
        self,
        results: Dict,
        save_path: Optional[str] = None
    ):
        """Plot strategy distribution pie chart"""
        fig, ax = plt.subplots(figsize=(10, 7))
        
        if 'cascade' in results and 'strategy_distribution' in results['cascade']:
            dist = results['cascade']['strategy_distribution']
            
            strategies = list(dist.keys())
            percentages = [dist[s] * 100 for s in strategies]
            
            colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
            explode = [0.05 if p == max(percentages) else 0 for p in percentages]
            
            ax.pie(percentages, labels=[s.capitalize() for s in strategies],
                  autopct='%1.1f%%', startangle=90, colors=colors,
                  explode=explode, textprops={'fontsize': 12, 'weight': 'bold'})
            
            ax.set_title('Strategy Selection Distribution\n(Adaptive Cascade)', 
                        fontsize=14, weight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, 'strategy_distribution.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_accuracy_comparison(
        self,
        results: Dict,
        save_path: Optional[str] = None
    ):
        """Plot accuracy comparison bar chart"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        methods = ['Cascade (Ours)']
        accuracies = [results['cascade']['accuracy']]
        
        if 'baselines' in results:
            for name, metrics in results['baselines'].items():
                methods.append(name.replace('always_', 'Always-').title())
                accuracies.append(metrics['accuracy'])
        
        # Create bars
        bars = ax.bar(range(len(methods)), accuracies, 
                     color=['#2ecc71' if 'Cascade' in m else '#95a5a6' for m in methods],
                     edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Annotate values
        for i, (bar, acc) in enumerate(zip(bars, accuracies)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{acc:.3f}', ha='center', va='bottom', 
                   fontsize=11, weight='bold')
        
        ax.set_ylabel('Accuracy', fontsize=12, weight='bold')
        ax.set_title('Accuracy Comparison: PromptCascade vs Baselines', 
                    fontsize=14, weight='bold', pad=20)
        ax.set_xticks(range(len(methods)))
        ax.set_xticklabels(methods, rotation=15, ha='right')
        ax.set_ylim(0, 1.0)
        ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, 'accuracy_comparison.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_cost_efficiency(
        self,
        results: Dict,
        save_path: Optional[str] = None
    ):
        """Plot cost efficiency comparison"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        methods = ['Cascade']
        costs = [results['cascade']['total_cost']]
        efficiencies = [results['cascade']['cost_efficiency']]
        
        if 'baselines' in results:
            for name, metrics in results['baselines'].items():
                methods.append(name.replace('always_', '').capitalize())
                costs.append(metrics['total_cost'])
                efficiencies.append(metrics['cost_efficiency'])
        
        # Cost comparison
        bars1 = ax1.bar(range(len(methods)), costs,
                       color=['#3498db' if 'Cascade' in m else '#bdc3c7' for m in methods],
                       edgecolor='black', linewidth=1.5, alpha=0.8)
        
        for bar, cost in zip(bars1, costs):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{cost:.1f}', ha='center', va='bottom', fontsize=10, weight='bold')
        
        ax1.set_ylabel('Total Cost (normalized units)', fontsize=11, weight='bold')
        ax1.set_title('Total Computational Cost', fontsize=13, weight='bold')
        ax1.set_xticks(range(len(methods)))
        ax1.set_xticklabels(methods, rotation=15, ha='right')
        ax1.grid(True, axis='y', alpha=0.3)
        
        # Efficiency comparison
        bars2 = ax2.bar(range(len(methods)), efficiencies,
                       color=['#2ecc71' if 'Cascade' in m else '#bdc3c7' for m in methods],
                       edgecolor='black', linewidth=1.5, alpha=0.8)
        
        for bar, eff in zip(bars2, efficiencies):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{eff:.4f}', ha='center', va='bottom', fontsize=10, weight='bold')
        
        ax2.set_ylabel('Cost Efficiency (accuracy/cost)', fontsize=11, weight='bold')
        ax2.set_title('Cost Efficiency', fontsize=13, weight='bold')
        ax2.set_xticks(range(len(methods)))
        ax2.set_xticklabels(methods, rotation=15, ha='right')
        ax2.grid(True, axis='y', alpha=0.3)
        
        fig.suptitle('Cost Analysis: PromptCascade vs Baselines', 
                    fontsize=15, weight='bold', y=1.02)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, 'cost_efficiency.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_ablation_study(
        self,
        ablation_results: Dict,
        save_path: Optional[str] = None
    ):
        """Plot ablation study results"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        if 'ablations' not in ablation_results:
            print("No ablation data found")
            return
        
        # Extract data
        ablation_names = ['Full Model'] + list(ablation_results['ablations'].keys())
        accuracies = [ablation_results['full_model']['accuracy']]
        
        for ablation in ablation_results['ablations'].values():
            accuracies.append(ablation['metrics']['accuracy'])
        
        # Format names
        display_names = ['Full Model'] + [
            name.replace('_', ' ').title() for name in ablation_results['ablations'].keys()
        ]
        
        # Create bars
        colors = ['#2ecc71'] + ['#e74c3c'] * (len(display_names) - 1)
        bars = ax.barh(range(len(display_names)), accuracies,
                      color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Annotate
        for i, (bar, acc) in enumerate(zip(bars, accuracies)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {acc:.3f}', ha='left', va='center', 
                   fontsize=11, weight='bold')
        
        ax.set_xlabel('Accuracy', fontsize=12, weight='bold')
        ax.set_title('Ablation Study: Impact of Feature Removal', 
                    fontsize=14, weight='bold', pad=20)
        ax.set_yticks(range(len(display_names)))
        ax.set_yticklabels(display_names)
        ax.set_xlim(0, 1.0)
        ax.grid(True, axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, 'ablation_study.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def generate_all_plots(self, results: Dict):
        """Generate all visualization plots"""
        print("Generating visualizations...")
        
        self.plot_pareto_frontier(results)
        print("✓ Pareto frontier plot")
        
        self.plot_strategy_distribution(results)
        print("✓ Strategy distribution plot")
        
        self.plot_accuracy_comparison(results)
        print("✓ Accuracy comparison plot")
        
        self.plot_cost_efficiency(results)
        print("✓ Cost efficiency plot")
        
        # Ablation study if available
        if 'ablations' in results:
            self.plot_ablation_study(results)
            print("✓ Ablation study plot")
        
        print(f"\nAll figures saved to: {self.output_dir}/")


if __name__ == "__main__":
    # Demo with mock data
    mock_results = {
        'cascade': {
            'accuracy': 0.85,
            'total_cost': 150.0,
            'cost_efficiency': 0.0057,
            'num_queries': 100,
            'strategy_distribution': {
                'direct': 0.30,
                'reasoning': 0.45,
                'verification': 0.20,
                'ensemble': 0.05
            }
        },
        'baselines': {
            'always_direct': {
                'accuracy': 0.72,
                'total_cost': 100.0,
                'cost_efficiency': 0.0072,
                'num_queries': 100
            },
            'always_reasoning': {
                'accuracy': 0.80,
                'total_cost': 250.0,
                'cost_efficiency': 0.0032,
                'num_queries': 100
            },
            'always_verification': {
                'accuracy': 0.83,
                'total_cost': 400.0,
                'cost_efficiency': 0.0021,
                'num_queries': 100
            },
            'always_ensemble': {
                'accuracy': 0.87,
                'total_cost': 600.0,
                'cost_efficiency': 0.0015,
                'num_queries': 100
            }
        },
        'cascade_detailed': {
            'pareto_frontier': [
                {'strategy': 'direct', 'accuracy': 0.72, 'cost': 50},
                {'strategy': 'reasoning', 'accuracy': 0.82, 'cost': 125},
                {'strategy': 'verification', 'accuracy': 0.88, 'cost': 200},
                {'strategy': 'ensemble', 'accuracy': 0.91, 'cost': 300}
            ]
        }
    }
    
    visualizer = PromptCascadeVisualizer()
    visualizer.generate_all_plots(mock_results)
