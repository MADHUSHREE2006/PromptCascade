# 🌐 PromptCascade Frontend Guide

## ✅ Frontend is Running!

**URL:** http://127.0.0.1:5000

The Flask web application is currently running on your local machine.

---

## 🚀 How to Start the Frontend

### **Method 1: Using Python (Recommended)**

```bash
cd d:\project\prompt\PromptCascade
python frontend\app.py
```

**Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### **Method 2: Using Flask Command**

```bash
cd d:\project\prompt\PromptCascade\frontend
set FLASK_APP=app.py
flask run
```

**Stop the server:** Press `Ctrl+C` in the terminal

---

## 📱 Frontend Pages

The web interface has **5 main pages**:

### **1. Home Page** 
**URL:** http://127.0.0.1:5000/

**Features:**
- 📊 **Dashboard overview** with key statistics
- 📈 **Latest experiment results** summary
- 🎯 **Quick stats**: accuracy, cost, savings vs baselines
- 🚀 **Quick navigation** to all features

**What you'll see:**
- Cascade accuracy percentage
- Total cost comparison
- Savings vs ensemble approach
- Number of queries processed
- Expensive stage usage rate

---

### **2. Demo/Interactive Page** 
**URL:** http://127.0.0.1:5000/demo

**Features:**
- 🔍 **Try the routing live!** Type any question
- 📊 **Real-time difficulty estimation**
- 🎯 **See which strategy is selected**
- 📈 **Feature breakdown visualization**
- 💡 **Sample questions** to test

**How to use:**
1. Type a question in the input box
2. Click "Route Query"
3. See:
   - Selected strategy (Direct/Reasoning/Verification/Ensemble)
   - Difficulty score (0.0-1.0)
   - Confidence level
   - Cost multiplier
   - Feature analysis breakdown
   - Routing reasoning

**Example queries to try:**
- "What is 2+2?" → Direct (easy)
- "Explain binary search" → Reasoning (moderate)
- "Prove sqrt(2) is irrational" → Verification (hard)
- "Derive backpropagation algorithm" → Ensemble (very hard)

---

### **3. Experiment Runner** 
**URL:** http://127.0.0.1:5000/experiment

**Features:**
- 🧪 **Run experiments from the browser**
- 📝 **Configure sample size** (100-5000)
- 🏷️ **Name your experiments**
- ☑️ **Toggle baseline comparisons**
- 📡 **Live log streaming** (see progress in real-time)

**How to use:**
1. Enter experiment name (e.g., "web_exp_1")
2. Choose sample size (default: 200)
3. Toggle "Run Baselines" if needed
4. Click "Start Experiment"
5. Watch live log output
6. View results when complete

**Note:** Experiments run in the background. You can navigate to other pages while it runs.

---

### **4. Results Viewer** 
**URL:** http://127.0.0.1:5000/results

**Features:**
- 📊 **View all experiment results**
- 📁 **Select from past experiments** (dropdown)
- 📈 **Interactive comparison table**
- 🎨 **Visualizations embedded** in the page
- 📉 **Strategy distribution** charts
- 📊 **Per-strategy accuracy** breakdown

**What you'll see:**
1. **Comparison Table:**
   - Cascade vs all baselines
   - Accuracy, cost, tokens, efficiency
   - Expensive stage rate

2. **Strategy Distribution Chart:**
   - How queries were routed
   - Percentage per strategy

3. **Per-Strategy Accuracy:**
   - Success rate by strategy
   - Visual bar charts

4. **Embedded Figures:**
   - Pareto frontier
   - Accuracy comparison
   - Cost efficiency
   - Strategy distribution
   - Ablation study (if available)

**How to use:**
1. Select an experiment from the dropdown
2. View metrics table
3. Scroll down to see charts
4. Click on figures to view full size

---

### **5. API Endpoints** (for developers)

The frontend exposes these API endpoints:

#### **POST /api/route**
Route a single query through the cascade.

**Request:**
```json
{
  "query": "What is 2+2?",
  "hint_difficulty": null  // optional: 0.0-1.0
}
```

**Response:**
```json
{
  "strategy": "direct",
  "difficulty": 0.123,
  "category": "easy",
  "confidence": 0.987,
  "cost": "1×",
  "strength": 50,
  "color": "#10b981",
  "features": {
    "Query Length": 0.080,
    "Lexical Complexity": 0.267,
    ...
  },
  "reasoning": "Query is straightforward; direct prompting should suffice"
}
```

#### **POST /api/run_experiment**
Start a new experiment.

**Request:**
```json
{
  "samples": 200,
  "name": "web_exp_1",
  "baselines": true
}
```

**Response:**
```json
{
  "status": "started",
  "name": "web_exp_1"
}
```

#### **GET /api/experiment_log**
Server-Sent Events stream for live experiment logs.

---

## 🎨 Frontend Features

### **Real-Time Features:**
- ✅ **Live routing** - instant difficulty estimation
- ✅ **Live logs** - watch experiments run in real-time
- ✅ **Interactive charts** - hover for details
- ✅ **Responsive design** - works on all screen sizes

### **Visualization Features:**
- 📊 Bar charts for comparisons
- 📈 Pareto frontier plots
- 🎯 Strategy distribution pie charts
- 📉 Cost efficiency charts
- 🎨 Color-coded strategies

### **Data Features:**
- 💾 Select from past experiments
- 📥 Export functionality (planned)
- 📊 Detailed metrics tables
- 🔄 Auto-refresh results

---

## 🛠️ Troubleshooting

### **Problem: Port 5000 already in use**

**Solution:**
```bash
# Option 1: Use different port
python frontend\app.py --port 5001

# Option 2: Kill existing process
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

### **Problem: Templates not found**

**Solution:**
```bash
# Make sure you're in the project root
cd d:\project\prompt\PromptCascade
python frontend\app.py
```

### **Problem: Import errors**

**Solution:**
```bash
# Install dependencies
pip install flask
pip install -r requirements.txt
```

### **Problem: No results showing**

**Solution:**
```bash
# Run at least one experiment first
python main.py demo

# Then reload the web page
```

### **Problem: Figures not displaying**

**Solution:**
```bash
# Make sure figures exist
dir results\figures

# If missing, regenerate
python main.py demo
```

---

## 📱 Mobile/Responsive

The frontend is **fully responsive** and works on:
- 💻 Desktop browsers (Chrome, Firefox, Edge, Safari)
- 📱 Mobile devices (responsive design)
- 📲 Tablets (optimized layout)

---

## 🎯 Quick Start Workflow

### **1. Start the Server**
```bash
python frontend\app.py
```

### **2. Open in Browser**
Navigate to: http://127.0.0.1:5000

### **3. Try the Demo**
1. Go to **Demo** page
2. Type: "Explain recursion in programming"
3. Click "Route Query"
4. See strategy selection: **Reasoning (2.5×)**

### **4. Run an Experiment**
1. Go to **Experiment** page
2. Name: "test_exp_1"
3. Samples: 200
4. Click "Start Experiment"
5. Watch live logs

### **5. View Results**
1. Go to **Results** page
2. Select "test_exp_1.json"
3. View metrics and charts

---

## 🔧 Configuration

### **Change Port**

Edit `frontend/app.py`, line at the end:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001, threaded=True)  # Changed from 5000
```

### **Change Theme**

Edit `frontend/templates/base.html` CSS variables:
```css
:root {
  --accent: #4f8ef7;      /* Primary color */
  --accent2: #667eea;     /* Secondary color */
  --bg: #0f1419;          /* Background */
  --surface: #1a1f27;     /* Card background */
}
```

### **Add Custom Routes**

Edit `frontend/app.py`:
```python
@app.route('/my-page')
def my_page():
    return render_template('my_page.html')
```

---

## 📊 Understanding the UI

### **Color Coding:**
- 🟢 **Green (Direct)** - Easy queries, 1× cost
- 🔵 **Blue (Reasoning)** - Moderate queries, 2.5× cost
- 🟡 **Orange (Verification)** - Hard queries, 4× cost
- 🔴 **Red (Ensemble)** - Very hard queries, 6× cost

### **Difficulty Scale:**
- 0.0-0.3: Easy
- 0.3-0.6: Moderate
- 0.6-0.85: Hard
- 0.85-1.0: Very Hard

### **Metrics Explained:**
- **Accuracy:** % correct answers
- **Cost:** Normalized cost units (lower = better)
- **Tokens:** Total tokens consumed
- **Cost Efficiency:** Accuracy per cost unit (higher = better)
- **Exp. Stage Rate:** % queries using expensive strategies

---

## 🚀 Advanced Usage

### **Programmatic API Calls**

```python
import requests

# Route a query
response = requests.post('http://127.0.0.1:5000/api/route', json={
    'query': 'What is 2+2?'
})
result = response.json()
print(f"Strategy: {result['strategy']}")
print(f"Difficulty: {result['difficulty']}")

# Start an experiment
response = requests.post('http://127.0.0.1:5000/api/run_experiment', json={
    'samples': 200,
    'name': 'api_test',
    'baselines': True
})
print(response.json())
```

### **Embed in Other Applications**

```html
<!-- Embed demo iframe -->
<iframe src="http://127.0.0.1:5000/demo" 
        width="800" height="600" 
        frameborder="0">
</iframe>
```

---

## 📝 Development

### **Project Structure:**
```
frontend/
├── app.py                 # Flask application
├── requirements.txt       # Dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── home.html         # Home page
│   ├── demo.html         # Interactive demo
│   ├── experiment.html   # Experiment runner
│   └── results.html      # Results viewer
└── static/               # Static assets
    ├── css/              # Stylesheets
    └── js/               # JavaScript
```

### **Tech Stack:**
- **Backend:** Flask 3.0+
- **Frontend:** HTML5, CSS3, JavaScript
- **Charts:** Chart.js (embedded)
- **Styling:** Custom CSS with CSS variables
- **API:** RESTful + Server-Sent Events (SSE)

---

## 🎉 Summary

**Frontend is now running at:** http://127.0.0.1:5000

**Key Pages:**
1. 🏠 Home - Dashboard overview
2. 🎮 Demo - Interactive routing
3. 🧪 Experiment - Run experiments
4. 📊 Results - View results
5. 🔌 API - Developer endpoints

**Next Steps:**
1. ✅ Open http://127.0.0.1:5000 in your browser
2. ✅ Try the Demo page with sample queries
3. ✅ Run an experiment from the web UI
4. ✅ View results and visualizations

**To Stop:**
```bash
# Press Ctrl+C in the terminal where it's running
```

---

**Need help?** Check the troubleshooting section or run:
```bash
python frontend\app.py --help
```

**Enjoy exploring PromptCascade! 🚀**
