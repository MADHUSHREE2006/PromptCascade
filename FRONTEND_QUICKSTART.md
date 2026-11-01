# ⚡ Frontend Quick Start

## 🚀 Start Server

```bash
cd d:\project\prompt\PromptCascade
python frontend\app.py
```

**Server will start at:** http://127.0.0.1:5000

---

## 📱 Pages Overview

| Page | URL | What It Does |
|------|-----|--------------|
| **Home** | http://127.0.0.1:5000/ | Dashboard with stats |
| **Demo** | http://127.0.0.1:5000/demo | Try live routing |
| **Experiment** | http://127.0.0.1:5000/experiment | Run experiments |
| **Results** | http://127.0.0.1:5000/results | View past results |

---

## 🎮 Try the Demo

1. Go to: http://127.0.0.1:5000/demo
2. Type: **"Explain recursion in programming"**
3. Click **"Route Query"**
4. See: Strategy = **Reasoning (2.5×)**

### Sample Queries to Try:

```
Easy (Direct):
  "What is 2+2?"
  "What is the capital of France?"
  
Moderate (Reasoning):
  "Explain binary search"
  "How does recursion work?"
  
Hard (Verification):
  "Prove sqrt(2) is irrational"
  "Derive the quadratic formula"
  
Very Hard (Ensemble):
  "Implement backpropagation algorithm"
  "Solve the traveling salesman problem"
```

---

## 🧪 Run Experiment from Web

1. Go to: http://127.0.0.1:5000/experiment
2. **Name:** my_web_exp
3. **Samples:** 200
4. **Baselines:** ✓ (checked)
5. Click **"Start Experiment"**
6. Watch live logs streaming
7. When done, go to Results page

---

## 📊 View Results

1. Go to: http://127.0.0.1:5000/results
2. Select experiment from dropdown
3. See:
   - Comparison table (Cascade vs Baselines)
   - Strategy distribution chart
   - Per-strategy accuracy
   - Embedded visualizations

---

## 🛑 Stop Server

Press **Ctrl+C** in the terminal where server is running

---

## 🎨 Features

- ✅ **Real-time routing** - Instant difficulty estimation
- ✅ **Live logs** - Watch experiments run
- ✅ **Interactive charts** - Hover for details
- ✅ **Responsive design** - Works on mobile
- ✅ **Color-coded strategies** - Easy visual understanding

---

## 🌈 Color Guide

- 🟢 **Green** = Direct (1× cost, Easy)
- 🔵 **Blue** = Reasoning (2.5× cost, Moderate)
- 🟡 **Orange** = Verification (4× cost, Hard)
- 🔴 **Red** = Ensemble (6× cost, Very Hard)

---

## 🔌 API (for developers)

### Route a query:
```bash
curl -X POST http://127.0.0.1:5000/api/route \
  -H "Content-Type: application/json" \
  -d '{"query":"What is 2+2?"}'
```

### Start experiment:
```bash
curl -X POST http://127.0.0.1:5000/api/run_experiment \
  -H "Content-Type: application/json" \
  -d '{"samples":200,"name":"api_test","baselines":true}'
```

---

## 🐛 Quick Fixes

### Port already in use?
```bash
# Use different port
# Edit frontend/app.py, change port=5000 to port=5001
```

### No results showing?
```bash
# Run an experiment first
python main.py demo
# Then refresh the web page
```

### Server not starting?
```bash
# Install Flask
pip install flask

# Check if Python is in PATH
python --version
```

---

## 💡 Pro Tips

1. **Run demo first** - Generates sample results to view
2. **Try sample queries** - Understand routing behavior
3. **Use small samples** - Start with 100-200 samples
4. **Watch live logs** - Experiment page shows real-time progress
5. **Bookmark pages** - Save URLs for quick access

---

## 🎯 5-Minute Quickstart

```bash
# 1. Start server (terminal 1)
cd d:\project\prompt\PromptCascade
python frontend\app.py

# 2. Generate sample data (terminal 2)
cd d:\project\prompt\PromptCascade
python main.py demo

# 3. Open browser
# Go to: http://127.0.0.1:5000

# 4. Explore pages
#    - Home: See dashboard
#    - Demo: Try routing
#    - Results: View demo results

# 5. Run web experiment
#    - Go to Experiment page
#    - Click "Start Experiment"
#    - View results when done
```

---

## ✅ Checklist

- [x] Server started: `python frontend\app.py`
- [x] Browser opened: http://127.0.0.1:5000
- [ ] Tried Demo page
- [ ] Run experiment from web UI
- [ ] Viewed results
- [ ] Tested API endpoints

---

**Current Status:** 🟢 Server Running at http://127.0.0.1:5000

**Need Help?** See `FRONTEND_GUIDE.md` for detailed documentation.
