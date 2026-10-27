"""
PromptCascade - Main Entry Point
Quick start script for running experiments.
"""

import sys
import os
import argparse
import logging
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import from src
from src.experiment_runner import ExperimentRunner
from src.visualization import PromptCascadeVisualizer


def setup_logging(verbose=False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def run_demo(args):
    """Run quick demo experiment"""
    print("=" * 70)
    print("PromptCascade Demo")
    print("=" * 70)
    print("\nRunning in OFFLINE mode (mock LLM responses)")
    print("This demonstrates the framework without requiring API keys.\n")
    
    runner = ExperimentRunner(config_path=args.config)
    
    # Generate small dataset
    print("Generating dataset...")
    dataset = runner.dataset_loader.create_combined_dataset(samples_per_domain=10)
    _, _, test = runner.dataset_loader.split_dataset(dataset)
    
    print(f"Dataset: {len(test)} test problems\n")
    
    # Run evaluation
    results = runner.run_full_evaluation(
        test,
        run_baselines=True,
        experiment_name="demo"
    )
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    visualizer = PromptCascadeVisualizer()
    visualizer.generate_all_plots(results)
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print(f"Results saved to: results/demo.json")
    print(f"Figures saved to: results/figures/")
    print("=" * 70)


def run_full_experiment(args):
    """Run full experiment"""
    print("=" * 70)
    print("PromptCascade - Full Experiment")
    print("=" * 70)
    
    runner = ExperimentRunner(config_path=args.config)
    
    # Generate or load dataset
    print(f"\nGenerating dataset ({args.samples} samples)...")
    dataset = runner.dataset_loader.create_combined_dataset(
        samples_per_domain=args.samples // 4
    )
    train, val, test = runner.dataset_loader.split_dataset(dataset)
    
    print(f"Dataset split: train={len(train)}, val={len(val)}, test={len(test)}\n")
    
    # Run evaluation
    results = runner.run_full_evaluation(
        test,
        run_baselines=args.run_baselines,
        experiment_name=args.name
    )
    
    # Generate visualizations
    if args.visualize:
        print("\nGenerating visualizations...")
        visualizer = PromptCascadeVisualizer()
        visualizer.generate_all_plots(results)
    
    print("\n" + "=" * 70)
    print("Experiment completed!")
    print(f"Results saved to: results/{args.name}.json")
    if args.visualize:
        print(f"Figures saved to: results/figures/")
    print("=" * 70)


def run_ablation(args):
    """Run ablation study"""
    print("=" * 70)
    print("PromptCascade - Ablation Study")
    print("=" * 70)
    
    runner = ExperimentRunner(config_path=args.config)
    
    # Generate dataset
    print(f"\nGenerating dataset ({args.samples} samples)...")
    dataset = runner.dataset_loader.create_combined_dataset(
        samples_per_domain=args.samples // 4
    )
    _, _, test = runner.dataset_loader.split_dataset(dataset)
    
    # Run ablation
    results = runner.run_ablation_study(test, experiment_name=args.name)
    
    # Visualize
    if args.visualize:
        print("\nGenerating visualizations...")
        visualizer = PromptCascadeVisualizer()
        visualizer.plot_ablation_study(results)
    
    print("\n" + "=" * 70)
    print("Ablation study completed!")
    print(f"Results saved to: results/{args.name}.json")
    print("=" * 70)


def run_visualization(args):
    """Generate visualizations from existing results"""
    print("=" * 70)
    print("Generating Visualizations")
    print("=" * 70)
    
    # Load results
    with open(args.results_file, 'r') as f:
        results = json.load(f)
    
    # Generate plots
    visualizer = PromptCascadeVisualizer(output_dir=args.output_dir)
    visualizer.generate_all_plots(results)
    
    print("\n" + "=" * 70)
    print(f"Visualizations saved to: {args.output_dir}/")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="PromptCascade: Difficulty-Adaptive Prompt Strategy Selection"
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run quick demo')
    
    # Full experiment command
    full_parser = subparsers.add_parser('experiment', help='Run full experiment')
    full_parser.add_argument('--name', default='experiment', help='Experiment name')
    full_parser.add_argument('--samples', type=int, default=1000, help='Number of samples')
    full_parser.add_argument('--no-baselines', dest='run_baselines', 
                            action='store_false', help='Skip baseline comparisons')
    full_parser.add_argument('--no-visualize', dest='visualize',
                            action='store_false', help='Skip visualization')
    
    # Ablation command
    ablation_parser = subparsers.add_parser('ablation', help='Run ablation study')
    ablation_parser.add_argument('--name', default='ablation', help='Experiment name')
    ablation_parser.add_argument('--samples', type=int, default=500, help='Number of samples')
    ablation_parser.add_argument('--no-visualize', dest='visualize',
                                action='store_false', help='Skip visualization')
    
    # Visualization command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualizations')
    viz_parser.add_argument('results_file', help='Path to results JSON file')
    viz_parser.add_argument('--output-dir', default='results/figures',
                           help='Output directory for figures')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Run command
    if args.command == 'demo':
        run_demo(args)
    elif args.command == 'experiment':
        run_full_experiment(args)
    elif args.command == 'ablation':
        run_ablation(args)
    elif args.command == 'visualize':
        run_visualization(args)
    else:
        parser.print_help()
        print("\nNo command specified. Try:")
        print("  python main.py demo              # Quick demo")
        print("  python main.py experiment        # Full experiment")
        print("  python main.py ablation          # Ablation study")
        print("  python main.py visualize <file>  # Generate plots")


if __name__ == "__main__":
    main()
