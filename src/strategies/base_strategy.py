"""
Base Strategy Class
Defines interface for all prompting strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time
import random
import logging

logger = logging.getLogger(__name__)


@dataclass
class StrategyResult:
    """Container for strategy execution results"""
    answer: str
    confidence: float
    tokens_used: int
    latency: float  # seconds
    strategy_name: str
    metadata: Optional[Dict[str, Any]] = None
    intermediate_steps: Optional[list] = None


class BaseStrategy(ABC):
    """
    Abstract base class for prompting strategies.
    
    All strategies must implement:
    - execute(): Main execution method
    - get_cost_multiplier(): Relative cost of this strategy
    - get_strategy_strength(): Baseline success rate of this strategy (0.0-1.0)
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.)
        """
        self.llm_client = llm_client
        self.total_tokens = 0
        self.total_latency = 0.0
        self.num_calls = 0
    
    @abstractmethod
    def execute(self, query: str, **kwargs) -> StrategyResult:
        """
        Execute the prompting strategy on a query.
        
        Args:
            query: Input question/problem
            **kwargs: Additional strategy-specific parameters.
                      May include: ground_truth (str), difficulty (float)
            
        Returns:
            StrategyResult with answer and metadata
        """
        pass
    
    @abstractmethod
    def get_cost_multiplier(self) -> float:
        """Relative cost of this strategy (1.0 = baseline)."""
        pass
    
    @abstractmethod
    def get_strategy_strength(self) -> float:
        """
        Baseline effectiveness of this strategy (0.0-1.0).
        Higher = more likely to produce a correct answer on a given problem.
        """
        pass
    
    def _call_llm(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1024,
        ground_truth: Optional[str] = None,
        difficulty: float = 0.5
    ) -> tuple:
        """
        Call LLM and track metrics.
        
        Args:
            prompt: Prompt to send to LLM
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            ground_truth: Correct answer (used only by mock model in offline mode)
            difficulty: Problem difficulty 0.0-1.0 (used only by mock model)
            
        Returns:
            Tuple of (response_text, tokens_used, latency)
        """
        if self.llm_client is None:
            # Mock response for offline mode
            logger.debug("No LLM client provided. Using mock response.")
            return self._mock_llm_response(
                prompt, ground_truth=ground_truth, difficulty=difficulty
            )
        
        start_time = time.time()
        
        try:
            response = self.llm_client.chat.completions.create(
                model=getattr(self.llm_client, 'model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            latency = time.time() - start_time
            answer = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            self.total_tokens += tokens
            self.total_latency += latency
            self.num_calls += 1
            
            return answer, tokens, latency
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            latency = time.time() - start_time
            return f"Error: {str(e)}", 0, latency
    
    def _mock_llm_response(
        self, 
        prompt: str,
        ground_truth: Optional[str] = None,
        difficulty: float = 0.5
    ) -> tuple:
        """
        Generate a realistic mock LLM response for offline testing.
        
        Simulates a model whose chance of producing the correct answer depends
        on the strategy's strength and the problem's difficulty:
            success_prob = clamp(strategy_strength + 0.55 - 0.7 * difficulty, 0.05, 0.99)
        
        When successful, returns the ground_truth answer (so evaluation can match it).
        When unsuccessful, returns a wrong plausible-looking answer so the evaluator
        correctly counts it as incorrect.
        
        Args:
            prompt: Input prompt
            ground_truth: The correct answer (used to simulate success/failure)
            difficulty: Problem difficulty (0.0 easy -> 1.0 very hard)
            
        Returns:
            Tuple of (mock_response, estimated_tokens, mock_latency)
        """
        # Simulate latency (no actual sleep — keeps experiments fast)
        mock_latency = random.uniform(0.5, 2.0)
        
        # Estimate tokens (rough approximation: input + output)
        estimated_tokens = max(len(prompt.split()) * 2, 20)
        
        # --- Probabilistic success model ---
        strength = self.get_strategy_strength()
        success_prob = strength + 0.55 - (0.7 * difficulty)
        success_prob = max(0.05, min(0.99, success_prob))
        
        if ground_truth is not None and random.random() < success_prob:
            # Model "knows" the answer — return it verbatim
            mock_response = str(ground_truth)
        else:
            # Model fails — return a wrong but plausible-looking answer.
            # For numeric ground truth, return a different number.
            # For text ground truth, return a generic incorrect response.
            gt_str = str(ground_truth) if ground_truth is not None else ""
            gt_stripped = gt_str.strip()
            
            # Try numeric perturbation first
            try:
                gt_num = float(gt_stripped)
                # Return a different numeric value (off by a random amount)
                wrong_num = gt_num + random.choice([-7, -3, 2, 5, 11, 13])
                if wrong_num == gt_num:
                    wrong_num = gt_num + 1
                # Preserve integer formatting if original was an int-like string
                if '.' not in gt_stripped and 'e' not in gt_stripped.lower():
                    mock_response = str(int(wrong_num))
                else:
                    mock_response = str(wrong_num)
            except (ValueError, TypeError):
                # Non-numeric: return a plausible but incorrect textual answer
                wrong_pool = [
                    "I am not sure of the exact answer.",
                    "The answer is unclear from the given information.",
                    "This cannot be determined with certainty.",
                    "Based on my analysis, the answer is unknown.",
                    "I cannot provide a definitive answer to this question.",
                ]
                mock_response = random.choice(wrong_pool)
        
        self.total_tokens += estimated_tokens
        self.total_latency += mock_latency
        self.num_calls += 1
        
        return mock_response, estimated_tokens, mock_latency
    
    def get_statistics(self) -> Dict[str, float]:
        """Get strategy execution statistics"""
        return {
            'total_tokens': self.total_tokens,
            'total_latency': self.total_latency,
            'num_calls': self.num_calls,
            'avg_tokens_per_call': self.total_tokens / max(self.num_calls, 1),
            'avg_latency_per_call': self.total_latency / max(self.num_calls, 1)
        }
    
    def reset_statistics(self):
        """Reset execution statistics"""
        self.total_tokens = 0
        self.total_latency = 0.0
        self.num_calls = 0
