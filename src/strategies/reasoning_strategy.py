"""
Chain-of-Thought Reasoning Strategy
Prompts the model to show its reasoning steps.
"""

from strategies.base_strategy import BaseStrategy, StrategyResult
import logging

logger = logging.getLogger(__name__)


class ReasoningStrategy(BaseStrategy):
    """
    Chain-of-Thought (CoT) reasoning: Prompt model to think step-by-step.
    
    Cost multiplier: 2.5 (generates more tokens due to reasoning steps)
    Best for: Moderate difficulty questions requiring logical steps
    """
    
    def execute(self, query: str, **kwargs) -> StrategyResult:
        """
        Execute Chain-of-Thought reasoning.
        
        Args:
            query: Input question
            **kwargs: Additional parameters
            
        Returns:
            StrategyResult with reasoning steps
        """
        logger.info(f"Executing Reasoning Strategy on: {query[:50]}...")
        
        # Chain-of-Thought prompt
        prompt = f"""Question: {query}

Let's approach this step-by-step:
1) First, let's understand what is being asked
2) Then, let's identify the key information
3) Next, let's work through the solution logically
4) Finally, let's state our answer clearly

Please provide your reasoning and final answer:"""
        
        # Call LLM (allow more tokens for reasoning)
        answer, tokens, latency = self._call_llm(
            prompt,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1024),
            ground_truth=kwargs.get('ground_truth'),
            difficulty=kwargs.get('difficulty', 0.5)
        )
        
        # Extract reasoning steps and final answer
        reasoning_steps, final_answer, confidence = self._parse_reasoning(answer)
        
        return StrategyResult(
            answer=final_answer,
            confidence=confidence,
            tokens_used=tokens,
            latency=latency,
            strategy_name="reasoning",
            intermediate_steps=reasoning_steps,
            metadata={
                'prompt_type': 'chain_of_thought',
                'full_response': answer
            }
        )
    
    def _parse_reasoning(self, response: str) -> tuple:
        """
        Parse reasoning steps from response.
        
        Args:
            response: Full LLM response
            
        Returns:
            Tuple of (reasoning_steps, final_answer, confidence)
        """
        lines = response.strip().split('\n')
        reasoning_steps = []
        final_answer = response  # Default to full response
        
        # Try to identify reasoning steps and final answer
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Collect reasoning steps
            if any(marker in line_lower for marker in ['step', '1)', '2)', '3)', '4)', '-']):
                reasoning_steps.append(line.strip())
            
            # Try to find final answer
            if any(marker in line_lower for marker in ['answer:', 'final answer:', 'therefore', 'thus', 'so the answer']):
                final_answer = ' '.join(lines[i:])
                break
        
        # Estimate confidence based on reasoning quality
        confidence = self._estimate_confidence(reasoning_steps, final_answer)
        
        return reasoning_steps, final_answer.strip(), confidence
    
    def _estimate_confidence(self, reasoning_steps: list, final_answer: str) -> float:
        """Estimate confidence from reasoning quality"""
        confidence = 0.6  # Base confidence higher than direct
        
        # More reasoning steps = higher confidence
        if len(reasoning_steps) >= 3:
            confidence += 0.1
        if len(reasoning_steps) >= 5:
            confidence += 0.1
        
        # Clear logical flow increases confidence
        logical_words = ['therefore', 'thus', 'hence', 'because', 'since', 'so']
        logical_count = sum(1 for word in logical_words if word in final_answer.lower())
        confidence += min(logical_count * 0.05, 0.15)
        
        # Hedging decreases confidence
        hedging_words = ['maybe', 'possibly', 'might', 'could be', 'not sure', 'unclear']
        if any(word in final_answer.lower() for word in hedging_words):
            confidence -= 0.15
        
        return max(0.0, min(1.0, confidence))
    
    def get_cost_multiplier(self) -> float:
        """Reasoning uses ~2.5x tokens due to step-by-step explanation"""
        return 2.5
    
    def get_strategy_strength(self) -> float:
        """Chain-of-Thought: stronger than direct, good for moderate problems"""
        return 0.65
