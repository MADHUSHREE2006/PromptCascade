# PromptCascade - Quick Start Guide

Get up and running with PromptCascade in 5 minutes!

## 🚀 Installation

```bash
# 1. Navigate to project directory
cd PromptCascade

# 2. Install dependencies
pip install -r requirements.txt
```

**That's it!** No API keys needed - runs in offline mode with mock LLM responses.

## 🎯 Run Your First Experiment

### Option 1: Quick Demo

```bash
python main.py demo
```

This runs a small experiment (40 problems) in **offline mode** with mock LLM responses. Perfect for:
- Testing the framework
- Understanding the workflow
- Generating sample visualizations

**No API keys required!**

**Output:**
- `results/demo.json` - Experiment results
- `results/figures/` - Visualizations

### Option 2: Full Experiment

```bash
python main.py experiment --samples 1000 --name my_first_experiment
```

This runs a full experiment with:
- 1000 problems across 4 domains
- Adaptive cascade + 4 baseline comparisons
- Complete metrics and visualizations

**Uses offline mode with mock LLM responses for fast, cost-free research.**

## 📊 View Results

### Results JSON
```bash
# View results
cat results/my_first_experiment.json
```

### Visualizations
Open these files in `results/figures/`:
- `pareto_frontier.png` - Quality-compute trade-off
- `strategy_distribution.png` - How queries are routed
- `accuracy_comparison.png` - Cascade vs baselines
- `cost_efficiency.png` - Cost analysis

## 🔬 Run Ablation Study

```bash
python main.py ablation --samples 500 --name feature_ablation
```

Tests the impact of removing each feature from the difficulty estimator.

## 🎨 Generate Custom Visualizations

```bash
python main.py visualize results/my_first_experiment.json --output-dir my_figures
```

## 🐍 Python API Usage

```python
from src.experiment_runner import ExperimentRunner

# Initialize
runner = ExperimentRunner()

# Generate dataset
dataset = runner.dataset_loader.create_combined_dataset(samples_per_domain=250)
_, _, test = runner.dataset_loader.split_dataset(dataset)

# Run experiment
results = runner.run_full_evaluation(test, run_baselines=True)

# Results are automatically saved!
print(f"Accuracy: {results['cascade']['accuracy']:.3f}")
print(f"Cost: {results['cascade']['total_cost']:.1f}")
```

## 🎓 For Research

### Step 1: Generate Dataset
```python
from src.dataset_loader import DatasetLoader

loader = DatasetLoader()
dataset = loader.create_combined_dataset(samples_per_domain=250)

# Save for reproducibility
loader.save_dataset("combined_1000", "data/dataset.json")
```

### Step 2: Run Experiments
```bash
# Full evaluation
python main.py experiment --samples 1000 --name exp1

# Ablation study
python main.py ablation --samples 500 --name ablation1

# Multiple trials
# (Currently: run experiment command multiple times with different names)
```

### Step 3: Analyze Results
```python
from src.visualization import PromptCascadeVisualizer
import json

# Load results
with open('results/exp1.json', 'r') as f:
    results = json.load(f)

# Generate all plots
viz = PromptCascadeVisualizer()
viz.generate_all_plots(results)

# Access metrics
print(f"Cascade accuracy: {results['cascade']['accuracy']}")
print(f"Strategy distribution: {results['cascade']['strategy_distribution']}")
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# LLM settings (Offline Mode)
llm:
  provider: "offline"  # Uses mock responses
  model: "mock-llm"
  temperature: 0.7

# Difficulty thresholds
difficulty:
  thresholds:
    easy: 0.3      # Adjust these to tune routing
    moderate: 0.6
    hard: 0.85

# Cost multipliers
strategies:
  direct:
    cost_multiplier: 1.0
  reasoning:
    cost_multiplier: 2.5
  verification:
    cost_multiplier: 4.0
  ensemble:
    cost_multiplier: 6.0
```

## 🐛 Troubleshooting

### "No module named 'src'"
```bash
# Make sure you're in the PromptCascade directory
cd PromptCascade
python main.py demo
```

### "Import errors"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Want faster experiments?
```bash
# Use fewer samples for quick testing
python main.py experiment --samples 100 --name quick_test
```

## 📚 Next Steps

1. **Read the full README**: `README.md` for detailed documentation
2. **Customize the framework**: Modify strategies, add features
3. **Run full experiments**: Use your own datasets
4. **Write your paper**: Use `docs/RESEARCH_PAPER_TEMPLATE.md`

## 💡 Example Commands

```bash
# Quick test
python main.py demo

# Small experiment
python main.py experiment --samples 200 --name test_run

# Full evaluation (1000 problems)
python main.py experiment --samples 1000 --name full_eval

# Ablation study
python main.py ablation --samples 500 --name ablation_study

# Just visualizations
python main.py visualize results/full_eval.json

# Experiment without baselines (faster)
python main.py experiment --samples 1000 --no-baselines --name cascade_only
```

## 🎉 Success!

You're now ready to:
- Run experiments
- Analyze results
- Write your research paper
- Present your findings

**Good luck with your research! 🚀**

---

For more details, see:
- `README.md` - Full documentation
- `docs/RESEARCH_PAPER_TEMPLATE.md` - Paper template
- `config.yaml` - Configuration options
