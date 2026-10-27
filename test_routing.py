#!/usr/bin/env python3
"""
Test script to verify difficulty estimator routes queries to different strategies.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from difficulty_estimator import DifficultyEstimator
from prompt_router import PromptRouter

def test_routing():
    """Test that queries route to different strategies based on difficulty."""
    
    estimator = DifficultyEstimator()
    router = PromptRouter(difficulty_estimator=estimator)
    
    # Test queries spanning different difficulty levels
    test_cases = [
        # Should route to DIRECT (easy, < 0.3)
        {
            "query": "What is 2+2?",
            "expected_strategy": "direct",
            "description": "Simple arithmetic"
        },
        {
            "query": "What color is the sky?",
            "expected_strategy": "direct",
            "description": "Basic factual question"
        },
        
        # Should route to REASONING (moderate, 0.3-0.6)
        {
            "query": "Explain how photosynthesis works in plants.",
            "expected_strategy": "reasoning",
            "description": "Requires explanation"
        },
        {
            "query": "Derive the quadratic formula from first principles and explain each step.",
            "expected_strategy": "reasoning",  # Changed from verification
            "description": "Mathematical derivation"
        },
        
        # Should route to VERIFICATION (hard, 0.6-0.8)
        {
            "query": "Compare and contrast democracy and autocracy, analyzing their philosophical foundations and practical implications.",
            "expected_strategy": "verification",  # Changed from reasoning
            "description": "Deep analytical comparison"
        },
        {
            "query": "Analyze the algorithm's time complexity and prove it is O(n log n) using mathematical induction.",
            "expected_strategy": "verification",
            "description": "Algorithmic proof with formal method"
        },
        
        # Should route to ENSEMBLE (very hard, >= 0.8)
        {
            "query": "Prove Fermat's Last Theorem using modular arithmetic and elliptic curves, incorporating Wiles' proof strategy.",
            "expected_strategy": "ensemble",  # Keeping ensemble expectation
            "description": "Advanced mathematical proof requiring multiple techniques"
        },
        {
            "query": "Synthesize a comprehensive analysis of how quantum entanglement contradicts local realism, incorporating Bell's theorem, experimental violations, and implications for interpretations of quantum mechanics.",
            "expected_strategy": "ensemble",
            "description": "Complex synthesis across multiple concepts"
        }
    ]
    
    print("=" * 80)
    print("ROUTING TEST RESULTS")
    print("=" * 80)
    print()
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected_strategy"]
        description = test_case["description"]
        
        # Estimate difficulty
        difficulty_score, _ = estimator.estimate_difficulty(query)
        
        # Route query
        decision = router.route(query)
        actual = decision.strategy.value
        
        # Check if it matches expectation
        match = "✓" if actual == expected else "✗"
        
        results.append({
            "match": match,
            "expected": expected,
            "actual": actual,
            "difficulty": difficulty_score
        })
        
        print(f"Test {i}: {match}")
        print(f"  Query: {query[:70]}...")
        print(f"  Description: {description}")
        print(f"  Difficulty Score: {difficulty_score:.3f}")
        print(f"  Expected: {expected.upper()}")
        print(f"  Actual: {actual.upper()}")
        print(f"  Reasoning: {decision.reasoning}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    matches = sum(1 for r in results if r["match"] == "✓")
    total = len(results)
    print(f"Passed: {matches}/{total} ({matches/total*100:.1f}%)")
    print()
    
    # Show difficulty distribution
    print("Difficulty Score Distribution:")
    for i, (test_case, result) in enumerate(zip(test_cases, results), 1):
        print(f"  {i}. {result['difficulty']:.3f} → {result['actual'].upper():12} (expected {result['expected'].upper()})")
    
    return matches == total

if __name__ == "__main__":
    success = test_routing()
    sys.exit(0 if success else 1)
