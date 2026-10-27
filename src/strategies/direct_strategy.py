"""
Direct Prompting Strategy
Simplest strategy - directly ask the question without additional scaffolding.
"""

from strategies.base_strategy import BaseStrategy, StrategyResult
import logging

logger = logging.getLogger(__name__)


class DirectStrategy(BaseStrategy):
    """
    Direct prompting: Ask the question directly without reasoning scaffolding.
    
    Cost multiplier: 1.0 (baseline)
    Best for: Easy, straightforward questions
    """
    
    def execute(self, query: str, **kwargs) -> StrategyResult:
        """
        Execute direct prompting.
        
        Args:
            query: Input question
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            StrategyResult
        """
        logger.info(f"Executing Direct Strategy on: {query[:50]}...")
        
        # Simple prompt
        prompt = f"Question: {query}\n\nAnswer:"
        
        # Call LLM
        answer, tokens, latency = self._call_llm(
            prompt,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 512),
            ground_truth=kwargs.get('ground_truth'),
            difficulty=kwargs.get('difficulty', 0.5)
        )
        
        # Estimate confidence (simple heuristic)
        confidence = self._estimate_confidence(answer)
        
        return StrategyResult(
            answer=answer.strip(),
            confidence=confidence,
            tokens_used=tokens,
            latency=latency,
            strategy_name="direct",
            metadata={
                'prompt_type': 'direct'
            }
        )
    
    def _estimate_confidence(self, answer: str) -> float:
        """Estimate confidence from answer characteristics"""
        # Simple heuristics
        confidence = 0.5
        
        # Longer answers may indicate more thought
        if len(answer) > 100:
            confidence += 0.1
        
        # Presence of hedging language decreases confidence
        hedging_words = ['maybe', 'possibly', 'might', 'could be', 'not sure']
        if any(word in answer.lower() for word in hedging_words):
            confidence -= 0.2
        
        # Definitive language increases confidence
        definitive_words = ['definitely', 'certainly', 'clearly', 'obviously']
        if any(word in answer.lower() for word in definitive_words):
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def get_cost_multiplier(self) -> float:
        """Direct prompting is the baseline"""
        return 1.0
    
    def get_strategy_strength(self) -> float:
        """Direct prompting: weakest strategy, best for easy problems"""
        return 0.50
