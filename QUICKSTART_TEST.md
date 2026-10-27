# Quick Start: Verify Routing Works

## 30-Second Test

```bash
cd PromptCascade
python test_routing_simple.py
```

Expected:
```
✓ SUCCESS: Multiple strategies are being used
```

If you see this, **routing is working** ✅

---

## 2-Minute Web Demo

```bash
cd frontend
python app.py
```

Open http://localhost:5000

Try these queries:

1. **"What is 2+2?"** → Should show **DIRECT** strategy
2. **"Explain how photosynthesis works"** → Should show **REASONING** strategy  
3. **"Compare and contrast democracy and autocracy with philosophical analysis"** → Should show **VERIFICATION** or **ENSEMBLE** strategy

If you see **different strategies** for these queries, **the web demo works** ✅

---

## What to Look For

In the web demo response, you should see:

```json
{
  "strategy": "REASONING",           // ← Different for each query
  "difficulty_score": 0.355,         // ← Higher for complex queries
  "reasoning": "Query requires..."   // ← Explanation of routing decision
}
```

---

## Troubleshooting

### If everything routes to DIRECT:

1. Check you're in the right directory: `PromptCascade/`
2. Verify the fix was applied:
   ```bash
   grep "0.60" src/difficulty_estimator.py
   ```
   Should find: `'keyword_density': 0.60,`

3. If not found, the fix wasn't applied. Check you're using the updated file.

### If test fails:

Check you have dependencies:
```bash
pip install -r requirements.txt  # or frontend/requirements.txt
```

---

## Success Criteria

✅ Test script passes  
✅ Web demo shows different strategies  
✅ Difficulty scores vary (low for simple, high for complex)  
✅ All 4 strategies reachable: DIRECT, REASONING, VERIFICATION, ENSEMBLE

**If all above pass**: You're ready for your defense! 🎓
