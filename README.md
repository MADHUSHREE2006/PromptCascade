# PromptCascade: Difficulty-Adaptive Prompt Strategy Selection

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A research framework for optimizing LLM prompting strategies based on problem difficulty

## 📋 Table of Contents

- [Overview](#overview)
- [Research Question](#research-question)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Methodology](#methodology)
- [Running Experiments](#running-experiments)
- [Results & Visualization](#results--visualization)
- [Configuration](#configuration)
- [For Final Year Students](#for-final-year-students)
- [Citation](#citation)
- [License](#license)

---

## 🎯 Overview

PromptCascade is a research framework that addresses a fundamental question in LLM optimization: **Should easy and difficult questions receive the same prompting strategy?**

Current approaches apply uniform strategies (always-direct, always-reasoning) across all queries, leading to:
- **Over-computation**: Wasting resources on simple problems
- **Under-computation**: Using insufficient strategies for complex problems
- **Suboptimal cost-accuracy trade-offs**

PromptCascade solves this by:
1. **Estimating problem difficulty** using linguistic and semantic features
2. **Routing queries adaptively** to the least expensive sufficient strategy
3. **Optimizing the quality-compute Pareto frontier** explicitly

---

## 🔬 Research Question

**Can we route queries to the least expensive sufficient prompting strategy based on problem difficulty, achieving better cost-accuracy trade-offs than uniform baselines?**

---

## ✨ Key Features

### 🧠 Difficulty Estimator
- **7 linguistic features**: query length, lexical complexity, syntactic depth, numerical complexity, domain specificity, keyword density, question complexity
- **Heuristic + ML modes**: Rule-based or supervised learning
- **Confidence scoring**: Estimates prediction confidence

### 🔀 Cascade Router
- **4 strategies**: Direct, Reasoning (CoT), Verification, Ensemble
- **Adaptive thresholds**: Optimizable based on validation data
- **Cost-aware**: Explicit cost multipliers (1.0×, 2.5×, 4.0×, 6.0×)

### 📊 Comprehensive Evaluation
- **1,000+ problems**: 4 domains (math, logic, QA, coding)
- **Multiple baselines**: Always-direct, always-reasoning, always-verification, always-ensemble
- **Rich metrics**: Accuracy, latency, tokens, cost efficiency, Pareto frontier

### 🔬 Research Tools
- **Ablation studies**: Feature importance analysis
- **Multiple trials**: Statistical significance testing
- **Visualizations**: Pareto plots, strategy distributions, comparisons
- **Result persistence**: JSON export for analysis

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) API keys for OpenAI, Anthropic, or Groq

### Step 1: Clone or Download
```bash
cd PromptCascade
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python -c "import sys; sys.path.append('src'); from difficulty_estimator import DifficultyEstimator; print('✓ Installation successful')"
```

**Note**: PromptCascade runs in **offline mode** using mock LLM responses. No API keys required!

---

## ⚡ Quick Start

### Run Demo Experiment (Offline Mode)

```bash
# Demo runs in offline mode with mock LLM responses
python src/experiment_runner.py
```

This will:
1. Generate a synthetic dataset (100 problems)
2. Run adaptive cascade evaluation
3. Compare against 4 baselines
4. Save results to `results/demo_eval.json`

**All using mock LLM responses - perfect for research and development!**

### Run Full Experiment

```python
from src.experiment_runner import ExperimentRunner
from src.dataset_loader import DatasetLoader

# Initialize
runner = ExperimentRunner(config_path="config.yaml")

# Load or generate dataset
loader = DatasetLoader()
dataset = loader.create_combined_dataset(samples_per_domain=250)
train, val, test = loader.split_dataset(dataset)

# Run evaluation
results = runner.run_full_evaluation(
    test, 
    run_baselines=True, 
    experiment_name="my_experiment"
)

# Results saved to results/my_experiment.json
```

---

## 📁 Project Structure

```
PromptCascade/
│
├── src/                           # Source code
│   ├── __init__.py
│   ├── difficulty_estimator.py    # Difficulty prediction (7 features)
│   ├── prompt_router.py           # Cascade routing logic
│   ├── dataset_loader.py          # Data generation & loading
│   ├── experiment_runner.py       # Experiment orchestration
│   ├── visualization.py           # Plotting tools
│   │
│   ├── strategies/                # Prompting strategies
│   │   ├── __init__.py
│   │   ├── base_strategy.py      # Abstract base class
│   │   ├── direct_strategy.py    # Direct prompting (1.0×)
│   │   ├── reasoning_strategy.py # Chain-of-Thought (2.5×)
│   │   ├── verification_strategy.py  # With verification (4.0×)
│   │   └── ensemble_strategy.py  # Multiple candidates (6.0×)
│   │
│   └── evaluation/                # Evaluation framework
│       ├── __init__.py
│       ├── evaluator.py          # Metrics tracking
│       └── comparator.py         # Baseline comparison
│
├── data/                          # Datasets (generated)
├── results/                       # Experiment results
├── experiments/                   # Experiment configs
├── notebooks/                     # Jupyter notebooks
├── docs/                          # Documentation
│   └── RESEARCH_PAPER_TEMPLATE.md
│
├── config.yaml                    # Main configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore
└── README.md                      # This file
```

---

## 🔬 Methodology

### Difficulty Estimation Pipeline

```
Query → Feature Extraction → Difficulty Score (0.0-1.0) → Category
```

**7 Features**:
1. **Query Length**: Normalized word count
2. **Lexical Complexity**: Word sophistication
3. **Syntactic Depth**: Sentence structure
4. **Numerical Complexity**: Math operations
5. **Domain Specificity**: Technical terms
6. **Keyword Density**: Reasoning indicators
7. **Question Complexity**: Multi-part questions

**Difficulty Categories**:
- Easy (0.0-0.3): Simple factual questions
- Moderate (0.3-0.6): Requires logical steps
- Hard (0.6-0.85): Complex reasoning
- Very Hard (0.85-1.0): Expert-level problems

### Cascade Routing Logic

```python
if difficulty < 0.3:
    strategy = Direct              # Fast, cheap
elif difficulty < 0.6:
    strategy = Reasoning (CoT)     # Moderate cost
elif difficulty < 0.85:
    strategy = Verification        # High accuracy
else:
    strategy = Ensemble            # Maximum accuracy
```

### Evaluation Metrics

1. **Primary Metrics**:
   - Accuracy (% correct)
   - Total tokens consumed
   - Total latency (seconds)
   - Total cost (normalized units)

2. **Derived Metrics**:
   - Accuracy per 1,000 tokens
   - Cost efficiency (accuracy/cost)
   - Expensive stage rate (% verification/ensemble)

3. **Pareto Analysis**:
   - Quality-compute frontier
   - Dominated vs. non-dominated strategies

---

## 🧪 Running Experiments

### 1. Basic Cascade Evaluation

```python
from src.experiment_runner import ExperimentRunner

runner = ExperimentRunner()
dataset = runner.dataset_loader.create_combined_dataset()
_, _, test = runner.dataset_loader.split_dataset(dataset)

results = runner.run_cascade_experiment(test, "my_cascade")
metrics = results.compute_metrics()
print(metrics)
```

### 2. Full Comparison (Cascade + Baselines)

```python
results = runner.run_full_evaluation(
    test, 
    run_baselines=True,
    experiment_name="full_comparison"
)
# Saves to results/full_comparison.json
```

### 3. Ablation Study

```python
ablation_results = runner.run_ablation_study(
    test,
    experiment_name="ablation_study"
)
# Tests: no_confidence, no_task_family, no_historical, random_routing
```

### 4. Multiple Trials (Statistical Significance)

```python
multi_trial_results = runner.run_multiple_trials(
    test,
    num_trials=5,
    experiment_name="statistical_test"
)
# Computes mean, std, min, max across trials
```

### 5. Generate Visualizations

```python
from src.visualization import PromptCascadeVisualizer
import json

with open('results/full_comparison.json', 'r') as f:
    results = json.load(f)

visualizer = PromptCascadeVisualizer(output_dir="results/figures")
visualizer.generate_all_plots(results)
# Creates: pareto_frontier.png, strategy_distribution.png, etc.
```

---

## 📊 Results & Visualization

### Expected Results

| Method | Accuracy | Cost | Cost Efficiency | Exp. Stage Rate |
|--------|----------|------|-----------------|-----------------|
| Always-Direct | ~0.70 | 100 | 0.0070 | 0% |
| Always-Reasoning | ~0.80 | 250 | 0.0032 | 0% |
| Always-Verification | ~0.83 | 400 | 0.0021 | 0% |
| Always-Ensemble | ~0.87 | 600 | 0.0015 | 0% |
| **PromptCascade** | **~0.85** | **~150** | **~0.0057** | **25%** |

### Generated Figures

1. **Pareto Frontier**: `results/figures/pareto_frontier.png`
2. **Strategy Distribution**: `results/figures/strategy_distribution.png`
3. **Accuracy Comparison**: `results/figures/accuracy_comparison.png`
4. **Cost Efficiency**: `results/figures/cost_efficiency.png`
5. **Ablation Study**: `results/figures/ablation_study.png`

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# LLM Configuration
llm:
  provider: "openai"  # or "anthropic", "groq", "local"
  model: "gpt-3.5-turbo"
  temperature: 0.7

# Difficulty Thresholds
difficulty:
  thresholds:
    easy: 0.3
    moderate: 0.6
    hard: 0.85

# Cost Multipliers
strategies:
  direct:
    cost_multiplier: 1.0
  reasoning:
    cost_multiplier: 2.5
  verification:
    cost_multiplier: 4.0
  ensemble:
    cost_multiplier: 6.0

# Dataset
data:
  total_samples: 1000
  domains:
    - mathematical_reasoning
    - logical_reasoning
    - question_answering
    - coding
```

---

## 🎓 For Final Year Students

This project is designed as a complete final year research project. Here's how to use it:

### Project Timeline (12-16 weeks)

**Weeks 1-2: Setup & Literature Review**
- Install and configure the framework
- Read `docs/RESEARCH_PAPER_TEMPLATE.md`
- Review related work on prompting and adaptive computation

**Weeks 3-4: Data Preparation**
- Generate or collect datasets
- Annotate difficulty labels (if using real benchmarks)
- Validate data quality

**Weeks 5-8: Experimentation**
- Run baseline comparisons
- Conduct ablation studies
- Perform multiple trials for statistical significance
- Optimize thresholds on validation set

**Weeks 9-10: Analysis**
- Generate all visualizations
- Analyze Pareto frontier
- Identify failure modes (over-routing, under-routing)
- Compare against state-of-the-art

**Weeks 11-12: Writing**
- Use `docs/RESEARCH_PAPER_TEMPLATE.md` as starting point
- Fill in methodology, results, discussion sections
- Create presentation slides

**Weeks 13-14: Refinement**
- Address advisor feedback
- Run additional experiments if needed
- Polish figures and tables

**Weeks 15-16: Final Submission**
- Proofread paper
- Prepare demo/presentation
- Submit code + paper

### Research Extensions

1. **Advanced Difficulty Estimators**:
   - Train neural networks on large-scale data
   - Use LLM embeddings as features
   - Incorporate domain-specific models

2. **Dynamic Routing**:
   - Online learning from user feedback
   - Contextual bandit algorithms
   - Reinforcement learning for threshold optimization

3. **Multi-Task Transfer**:
   - Transfer difficulty estimators across domains
   - Meta-learning for new task types

4. **Cost Modeling**:
   - Explicit token prediction models
   - Latency-aware routing
   - Budget-constrained optimization

5. **Real-World Deployment**:
   - A/B testing in production
   - User study on perceived quality
   - API wrapper for easy integration

### Deliverables Checklist

- [ ] Working code (this repository)
- [ ] Experimental results (JSON files in `results/`)
- [ ] Visualizations (figures in `results/figures/`)
- [ ] Research paper (using template in `docs/`)
- [ ] Presentation slides (create using results)
- [ ] Demo video (optional but recommended)
- [ ] README with clear instructions (this file)

---

## 📚 Additional Resources

### Recommended Reading

1. **Prompting Strategies**:
   - Wei et al. (2022) - "Chain-of-Thought Prompting"
   - Kojima et al. (2022) - "Zero-Shot CoT"
   - Wang et al. (2023) - "Self-Consistency"

2. **Adaptive Computation**:
   - Graves (2016) - "Adaptive Computation Time"
   - Dehghani et al. (2019) - "Universal Transformers"

3. **Difficulty Estimation**:
   - Settles & Meeder (2016) - "Second Language Acquisition Difficulty"
   - Maddela & Xu (2018) - "Text Complexity Assessment"

### Useful Commands

```bash
# Run tests (if implemented)
pytest tests/

# Generate dataset only
python src/dataset_loader.py

# Test difficulty estimator
python src/difficulty_estimator.py

# Test router
python src/prompt_router.py

# Quick visualization test
python src/visualization.py
```

---

## 🤝 Contributing

This is a research project template. Feel free to:
- Add new prompting strategies
- Implement additional difficulty features
- Create new evaluation metrics
- Extend to other domains

---

## 📄 Citation

If you use this framework in your research, please cite:

```bibtex
@article{promptcascade2024,
  title={PromptCascade: Difficulty-Adaptive Prompt Strategy Selection},
  author={[Your Name]},
  journal={[Conference/Journal]},
  year={2024}
}
```

---

## 📧 Contact

For questions or issues:
- Open an issue on GitHub
- Email: [your.email@university.edu]

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Inspired by research on adaptive computation and prompt engineering
- Built with Python, matplotlib, seaborn, scikit-learn
- Designed for educational and research purposes

---

**Good luck with your research! 🚀**
