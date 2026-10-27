#!/usr/bin/env python3
"""
Simple smoke test to verify routing works across all strategies.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from difficulty_estimator import DifficultyEstimator
from prompt_router import PromptRouter

def main():
    """Verify that different strategies can be reached."""
    
    estimator = DifficultyEstimator()
    router = PromptRouter(difficulty_estimator=estimator)
    
    test_queries = [
        ("What is 2+2?", "DIRECT"),
        ("Explain how gravity works.", "REASONING"),
        ("Compare and contrast classical and quantum mechanics, analyzing their philosophical implications.", "VERIFICATION or ENSEMBLE"),
        ("Synthesize a comprehensive analysis incorporating multiple advanced mathematical theorems.", "ENSEMBLE"),
    ]
    
    print("Routing Smoke Test")
    print("=" * 70)
    
    strategies_seen = set()
    
    for query, expected_range in test_queries:
        difficulty_score, _ = estimator.estimate_difficulty(query)
        decision = router.route(query)
        strategy = decision.strategy.value.upper()
        strategies_seen.add(strategy)
        
        print(f"\nQuery: {query[:60]}...")
        print(f"  Difficulty: {difficulty_score:.3f}")
        print(f"  Strategy: {strategy}")
        print(f"  Expected: {expected_range}")
    
    print("\n" + "=" * 70)
    print(f"Strategies used: {sorted(strategies_seen)}")
    print(f"Total unique strategies: {len(strategies_seen)}/4")
    
    if len(strategies_seen) >= 3:
        print("✓ SUCCESS: Multiple strategies are being used")
        return True
    else:
        print("✗ FAILED: Too few strategies used (all routing to same strategy?)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
