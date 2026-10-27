"""
PromptCascade Frontend — Flask Application
"""

import sys
import os
import json
import base64
import threading
import time

# Make src importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask, render_template, request, jsonify, Response
from difficulty_estimator import DifficultyEstimator
from prompt_router import PromptRouter, PromptStrategy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'promptcascade-2024'

# ── Shared components ────────────────────────────────────────────────────────
estimator = DifficultyEstimator()
router    = PromptRouter(estimator)

RESULTS_DIR  = os.path.join(os.path.dirname(__file__), '..', 'results')
FIGURES_DIR  = os.path.join(RESULTS_DIR, 'figures')
SRC_DIR      = os.path.join(os.path.dirname(__file__), '..', 'src')

# Streaming log lines for the experiment runner page
_experiment_log: list[str] = []
_experiment_running = False

# ── Strategy metadata ─────────────────────────────────────────────────────────
STRATEGY_META = {
    'direct':       {'label': 'Direct',       'cost': '1×',  'strength': 50,  'color': '#10b981'},
    'reasoning':    {'label': 'Reasoning',    'cost': '2.5×','strength': 65,  'color': '#3b82f6'},
    'verification': {'label': 'Verification', 'cost': '4×',  'strength': 80,  'color': '#f59e0b'},
    'ensemble':     {'label': 'Ensemble',     'cost': '6×',  'strength': 90,  'color': '#ef4444'},
}

# ── Helper: load latest result file ──────────────────────────────────────────
def _load_results(filename: str) -> dict:
    path = os.path.join(RESULTS_DIR, filename)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return {}


def _list_result_files() -> list[str]:
    if not os.path.exists(RESULTS_DIR):
        return []
    return sorted(
        [f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')],
        reverse=True
    )


def _figure_as_b64(name: str) -> str | None:
    path = os.path.join(FIGURES_DIR, name)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

# ── Pages ─────────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    result_files = _list_result_files()
    latest = _load_results(result_files[0]) if result_files else {}
    cascade = latest.get('cascade', {})
    baselines = latest.get('baselines', {})

    stats = {
        'cascade_accuracy':  round(cascade.get('accuracy', 0) * 100, 1),
        'cascade_cost':      cascade.get('total_cost', 0),
        'num_queries':       cascade.get('num_queries', 0),
        'exp_stage_rate':    round(cascade.get('expensive_stage_rate', 0) * 100, 1),
        'vs_ensemble_saving': 0,
        'vs_direct_gain':     0,
    }

    if baselines:
        ens_cost = baselines.get('always_ensemble', {}).get('total_cost', 0)
        dir_acc  = baselines.get('always_direct',   {}).get('accuracy',   0)
        if ens_cost:
            stats['vs_ensemble_saving'] = round(
                (1 - stats['cascade_cost'] / ens_cost) * 100, 1)
        if dir_acc:
            stats['vs_direct_gain'] = round(
                (cascade.get('accuracy', 0) - dir_acc) * 100, 1)

    return render_template('home.html', stats=stats)


@app.route('/demo')
def demo():
    return render_template('demo.html', strategy_meta=STRATEGY_META)


@app.route('/api/route', methods=['POST'])
def api_route():
    data  = request.get_json(force=True)
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Empty query'}), 400

    # Optional hint_difficulty lets the demo page pass a pre-labelled
    # difficulty for curated sample questions, bypassing the heuristic.
    hint = data.get('hint_difficulty')
    metadata = {'ground_truth_difficulty': float(hint)} if hint is not None else None

    difficulty, features = estimator.estimate_difficulty(
        query, metadata=metadata, return_features=True)
    category   = estimator.categorize_difficulty(difficulty)
    confidence = estimator.get_confidence(difficulty, features)

    decision = router.route(query, metadata=metadata, return_features=False)
    strategy  = decision.strategy.value

    feature_scores = {
        'Query Length':         round(min(features.query_length / 50.0, 1.0), 3),
        'Lexical Complexity':   round(features.lexical_complexity, 3),
        'Syntactic Depth':      round(features.syntactic_depth / 10.0, 3),
        'Numerical Complexity': round(features.numerical_complexity, 3),
        'Domain Specificity':   round(features.domain_specificity, 3),
        'Keyword Density':      round(features.keyword_density, 3),
        'Question Complexity':  round(features.question_complexity, 3),
    }

    return jsonify({
        'strategy':      strategy,
        'difficulty':    round(difficulty, 3),
        'category':      category,
        'confidence':    round(confidence, 3),
        'cost':          STRATEGY_META[strategy]['cost'],
        'strength':      STRATEGY_META[strategy]['strength'],
        'color':         STRATEGY_META[strategy]['color'],
        'features':      feature_scores,
        'reasoning':     decision.reasoning,
    })


@app.route('/experiment')
def experiment():
    result_files = _list_result_files()
    return render_template('experiment.html', result_files=result_files,
                           is_running=_experiment_running)


@app.route('/api/run_experiment', methods=['POST'])
def api_run_experiment():
    global _experiment_running, _experiment_log
    if _experiment_running:
        return jsonify({'error': 'An experiment is already running'}), 409

    data     = request.get_json(force=True)
    samples  = int(data.get('samples', 200))
    name     = data.get('name', 'ui_experiment').strip() or 'ui_experiment'
    baselines = data.get('baselines', True)

    _experiment_log = []
    _experiment_running = True

    def run():
        global _experiment_running
        try:
            import subprocess
            cmd = [sys.executable, 'main.py', 'experiment',
                   '--samples', str(samples),
                   '--name', name]
            if not baselines:
                cmd.append('--no-baselines')

            root = os.path.join(os.path.dirname(__file__), '..')
            proc = subprocess.Popen(
                cmd, cwd=root,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in proc.stdout:
                _experiment_log.append(line.rstrip())
            proc.wait()
            _experiment_log.append('__DONE__')
        except Exception as e:
            _experiment_log.append(f'ERROR: {e}')
            _experiment_log.append('__DONE__')
        finally:
            _experiment_running = False

    threading.Thread(target=run, daemon=True).start()
    return jsonify({'status': 'started', 'name': name})


@app.route('/api/experiment_log')
def api_experiment_log():
    """Server-Sent Events stream for live experiment log."""
    def generate():
        sent = 0
        while True:
            while sent < len(_experiment_log):
                line = _experiment_log[sent]
                yield f"data: {json.dumps(line)}\n\n"
                sent += 1
            if not _experiment_running and sent >= len(_experiment_log):
                break
            time.sleep(0.2)
    return Response(generate(), mimetype='text/event-stream')


@app.route('/results')
def results():
    result_files = _list_result_files()
    selected     = request.args.get('file', result_files[0] if result_files else '')
    data         = _load_results(selected) if selected else {}

    cascade   = data.get('cascade', {})
    baselines = data.get('baselines', {})

    # Build comparison table rows
    rows = []
    if cascade:
        rows.append({
            'name': 'Cascade (Ours)', 'highlight': True,
            'accuracy':  round(cascade.get('accuracy',   0) * 100, 1),
            'cost':      round(cascade.get('total_cost', 0), 1),
            'tokens':    cascade.get('total_tokens', 0),
            'eff':       round(cascade.get('cost_efficiency', 0), 4),
            'exp_rate':  round(cascade.get('expensive_stage_rate', 0) * 100, 1),
        })
    for bname, m in baselines.items():
        rows.append({
            'name':     bname.replace('always_', 'Always-').title(),
            'highlight': False,
            'accuracy':  round(m.get('accuracy',   0) * 100, 1),
            'cost':      round(m.get('total_cost', 0), 1),
            'tokens':    m.get('total_tokens', 0),
            'eff':       round(m.get('cost_efficiency', 0), 4),
            'exp_rate':  '—',
        })

    # Strategy distribution
    dist = cascade.get('strategy_distribution', {})
    dist_data = [
        {'name': k, 'pct': round(v * 100, 1),
         'color': STRATEGY_META.get(k, {}).get('color', '#888')}
        for k, v in dist.items()
    ]

    # Per-strategy accuracy
    strat_acc = cascade.get('strategy_accuracy', {})
    acc_data = [
        {'name': k, 'acc': round(v * 100, 1),
         'color': STRATEGY_META.get(k, {}).get('color', '#888')}
        for k, v in strat_acc.items()
    ]

    # Figures
    figure_names = [
        'pareto_frontier.png', 'accuracy_comparison.png',
        'cost_efficiency.png', 'strategy_distribution.png',
        'ablation_study.png',
    ]
    figures = {}
    for fn in figure_names:
        b64 = _figure_as_b64(fn)
        if b64:
            figures[fn] = b64

    return render_template('results.html',
                           result_files=result_files,
                           selected=selected,
                           rows=rows,
                           dist_data=json.dumps(dist_data),
                           acc_data=json.dumps(acc_data),
                           cascade=cascade,
                           figures=figures,
                           experiment_id=data.get('experiment_id', selected))


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
