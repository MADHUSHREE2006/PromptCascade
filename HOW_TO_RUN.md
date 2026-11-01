# 🚀 How to Run PromptCascade

## ✅ Prerequisites

- **Python 3.8+** (You have Python 3.14.6 ✓)
- **pip** package manager
- **No API keys required** - runs in offline mode!

---

## 📦 Step 1: Install Dependencies

```bash
cd d:\project\prompt\PromptCascade
pip install -r requirements.txt
```

This installs:
- numpy, pandas, scipy (data processing)
- scikit-learn, xgboost (ML models)
- matplotlib, seaborn, plotly (visualizations)
- tqdm (progress bars)
- pyyaml (configuration)

**Installation time:** ~2-5 minutes

---

## 🎯 Step 2: Choose Your Run Mode

### **Option 1: Quick Demo (Recommended for First Time)**

```bash
python main.py demo
```

**What it does:**
- Generates 40 problems (10 per domain)
- Runs adaptive cascade on 8 test problems
- Compares against 4 baselines
- Generates visualizations
- **Takes ~5 seconds**

**Output:**
```
Results saved to: results/demo.json
Figures saved to: results/figures/
```

---

### **Option 2: Full Experiment**

```bash
# Run with 1000 problems
python main.py experiment --samples 1000 --name my_experiment

# Run with custom settings
python main.py experiment --samples 500 --name test_run --no-baselines
```

**What it does:**
- Generates 1000 problems (250 per domain)
- Full cascade evaluation
- Baseline comparisons (optional)
- Statistical analysis
- **Takes ~30-60 seconds**

**Output:**
```
Results saved to: results/my_experiment.json
Figures saved to: results/figures/
```

---

### **Option 3: Ablation Study**

```bash
python main.py ablation --samples 500 --name ablation_study
```

**What it does:**
- Tests impact of removing each feature
- Compares: full model vs ablated versions
- Shows feature importance
- **Takes ~1-2 minutes**

**Features tested:**
- No confidence scoring
- No task family (domain)
- No historical performance
- Random routing (baseline)

---

### **Option 4: Generate Visualizations Only**

```bash
python main.py visualize results/demo.json
```

**What it does:**
- Loads existing results
- Regenerates all plots
- Useful for customizing visualizations

---

## 📊 Step 3: View Results

### **A. Check Results Files**

```bash
# View results JSON
cat results/demo.json

# Or open in text editor
notepad results/demo.json
```

### **B. Open Visualizations**

The following plots are generated in `results/figures/`:

1. **`pareto_frontier.png`** - Cost vs Accuracy trade-off
2. **`strategy_distribution.png`** - How queries are routed
3. **`accuracy_comparison.png`** - Cascade vs baselines
4. **`cost_efficiency.png`** - Efficiency analysis
5. **`ablation_study.png`** - Feature importance (if ablation run)

```bash
# Open all figures
start results/figures/pareto_frontier.png
start results/figures/strategy_distribution.png
start results/figures/accuracy_comparison.png
start results/figures/cost_efficiency.png
```

---

## 🐍 Step 4: Use Python API (Advanced)

Create a custom script:

```python
# my_experiment.py
from src.experiment_runner import ExperimentRunner
from src.visualization import PromptCascadeVisualizer

# Initialize
runner = ExperimentRunner(config_path="config.yaml")

# Generate dataset
dataset = runner.dataset_loader.create_combined_dataset(samples_per_domain=100)
train, val, test = runner.dataset_loader.split_dataset(dataset)

print(f"Dataset: {len(train)} train, {len(val)} val, {len(test)} test")

# Run cascade only (no baselines)
results = runner.run_full_evaluation(
    test, 
    run_baselines=False,
    experiment_name="custom_exp"
)

# Print results
print(f"\nAccuracy: {results['cascade']['accuracy']:.3f}")
print(f"Total Cost: {results['cascade']['total_cost']:.1f}")
print(f"Cost Efficiency: {results['cascade']['cost_efficiency']:.3f}")

# Generate visualizations
viz = PromptCascadeVisualizer()
viz.generate_all_plots(results)

print("\nDone! Results saved to results/custom_exp.json")
```

Run it:
```bash
python my_experiment.py
```

---

## ⚙️ Step 5: Customize Configuration

Edit `config.yaml` to customize behavior:

```yaml
# Difficulty thresholds (adjust routing sensitivity)
difficulty:
  thresholds:
    easy: 0.3      # Lower = more easy queries
    moderate: 0.6  # Adjust moderate range
    hard: 0.85     # Higher = fewer ensemble calls

# Cost multipliers (adjust strategy costs)
strategies:
  direct:
    cost_multiplier: 1.0
  reasoning:
    cost_multiplier: 2.5   # Increase if reasoning is more expensive
  verification:
    cost_multiplier: 4.0
  ensemble:
    cost_multiplier: 6.0   # Adjust based on your ensemble size

# Dataset size
data:
  total_samples: 1000
  min_samples_per_domain: 250
```

After editing, run:
```bash
python main.py experiment --samples 1000 --name custom_config
```

---

## 🧪 Step 6: Test Individual Components

### **Test Difficulty Estimator**

```bash
python src/difficulty_estimator.py
```

Output:
```
Query: What is 2 + 2?
Difficulty Score: 0.150
Category: EASY

Query: Prove that the square root of 2 is irrational.
Difficulty Score: 0.752
Category: HARD
```

### **Test Prompt Router**

```bash
python src/prompt_router.py
```

Output:
```
Query: What is 2 + 2?
Selected Strategy: DIRECT
Estimated Cost: 1.0x

Query: Derive backpropagation algorithm...
Selected Strategy: ENSEMBLE
Estimated Cost: 6.0x
```

### **Test Dataset Loader**

```bash
python src/dataset_loader.py
```

Output:
```
Generated 200 synthetic problems
Split: train=120, val=40, test=40
```

---

## 📈 Understanding Results

### **Key Metrics to Look At:**

1. **Accuracy** - % of correct answers (higher is better)
2. **Total Cost** - Normalized cost units (lower is better)
3. **Cost Efficiency** - Accuracy per cost unit (higher is better)
4. **Expensive Stage Rate** - % queries using verification/ensemble

### **What Good Results Look Like:**

```
Strategy             Accuracy    Cost    Cost Efficiency
Cascade (Ours)       0.850       150     0.0057
Always-Ensemble      0.870       600     0.0015
```

**Interpretation:**
- Cascade achieves 98% of ensemble's accuracy
- At only 25% of the cost
- 3.8x better cost efficiency

---

## 🔧 Troubleshooting

### **Problem: Import Errors**

```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### **Problem: "No module named 'src'"**

```bash
# Solution: Make sure you're in the project directory
cd d:\project\prompt\PromptCascade
python main.py demo
```

### **Problem: Visualization Not Generating**

```bash
# Check if matplotlib backend is set correctly
python -c "import matplotlib; print(matplotlib.get_backend())"

# If issues persist, try:
pip install matplotlib --upgrade
```

### **Problem: Slow Execution**

```bash
# Use fewer samples for faster testing
python main.py experiment --samples 100 --name quick_test
```

---

## 🎓 Next Steps

### **For Research:**

1. **Run Multiple Trials:**
```bash
python main.py experiment --samples 1000 --name trial1
python main.py experiment --samples 1000 --name trial2
python main.py experiment --samples 1000 --name trial3
```

2. **Run Ablation Study:**
```bash
python main.py ablation --samples 500 --name feature_importance
```

3. **Analyze Results:**
```python
import json

# Load results
with open('results/trial1.json') as f:
    results = json.load(f)

# Compare cascade vs baselines
cascade_acc = results['cascade']['accuracy']
ensemble_acc = results['baselines']['always_ensemble']['accuracy']

print(f"Cascade: {cascade_acc:.3f}")
print(f"Ensemble: {ensemble_acc:.3f}")
print(f"Accuracy retained: {cascade_acc/ensemble_acc*100:.1f}%")
```

### **For Production:**

1. **Add Real LLM Integration:**
   - Edit `config.yaml` to use OpenAI/Anthropic/Groq
   - Add API keys to `.env` file
   - Modify strategies to use real LLM calls

2. **Deploy as API:**
   - Wrap router in Flask/FastAPI
   - Expose endpoint: `/query` → returns answer + routing decision

3. **Monitor Performance:**
   - Track routing decisions
   - Log cost savings
   - Analyze failure modes

---

## 💡 Quick Command Reference

```bash
# Quick demo (5 seconds)
python main.py demo

# Full experiment (1000 samples)
python main.py experiment --samples 1000 --name exp1

# Ablation study
python main.py ablation --samples 500 --name ablation1

# Just visualizations
python main.py visualize results/exp1.json

# Test difficulty estimator
python src/difficulty_estimator.py

# Test router
python src/prompt_router.py

# View help
python main.py --help
```

---

## 📚 File Locations

```
d:\project\prompt\PromptCascade\
├── results/
│   ├── demo.json           ← Experiment results
│   └── figures/            ← Visualizations
│       ├── pareto_frontier.png
│       ├── strategy_distribution.png
│       ├── accuracy_comparison.png
│       └── cost_efficiency.png
├── config.yaml             ← Configuration
├── main.py                 ← Entry point
└── src/                    ← Source code
```

---

## ✅ Success Checklist

- [x] Dependencies installed
- [x] Demo runs successfully
- [x] Results saved to `results/demo.json`
- [x] Visualizations generated in `results/figures/`
- [ ] Run full experiment (1000 samples)
- [ ] Run ablation study
- [ ] Analyze results
- [ ] Write research paper

---

## 🎉 You're Ready!

You've successfully:
1. ✅ Installed all dependencies
2. ✅ Run the demo
3. ✅ Generated results and visualizations
4. ✅ Understood the output

**Next:** Run a full experiment and analyze the results!

```bash
python main.py experiment --samples 1000 --name my_first_full_experiment
```

Good luck with your research! 🚀
