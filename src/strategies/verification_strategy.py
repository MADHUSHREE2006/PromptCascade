"""
Reasoning + Verification Strategy
Generates reasoning, then verifies the answer.
"""

from strategies.base_strategy import BaseStrategy, StrategyResult
import logging

logger = logging.getLogger(__name__)


class VerificationStrategy(BaseStrategy):
    """
    Reasoning + Verification: Generate answer with reasoning, then verify it.
    
    Cost multiplier: 4.0 (two LLM calls: reasoning + verification)
    Best for: Hard questions where accuracy is critical
    """
    
    def execute(self, query: str, **kwargs) -> StrategyResult:
        """
        Execute reasoning + verification strategy.
        
        Args:
            query: Input question
            **kwargs: Additional parameters
            
        Returns:
            StrategyResult with verification
        """
        logger.info(f"Executing Verification Strategy on: {query[:50]}...")
        
        # Step 1: Generate initial answer with reasoning
        reasoning_prompt = f"""Question: {query}

Please solve this step-by-step and provide your answer:"""
        
        initial_answer, tokens1, latency1 = self._call_llm(
            reasoning_prompt,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1024),
            ground_truth=kwargs.get('ground_truth'),
            difficulty=kwargs.get('difficulty', 0.5)
        )
        
        # Step 2: Verify the answer
        verification_prompt = f"""Original Question: {query}

Proposed Answer:
{initial_answer}

Please verify this answer by:
1) Checking if it directly addresses the question
2) Identifying any logical errors or inconsistencies
3) Confirming the reasoning is sound
4) Stating whether the answer is correct or needs revision

Verification:"""
        
        verification_response, tokens2, latency2 = self._call_llm(
            verification_prompt,
            temperature=kwargs.get('temperature', 0.3),  # Lower temp for verification
            max_tokens=kwargs.get('max_tokens', 512),
            ground_truth=kwargs.get('ground_truth'),
            difficulty=kwargs.get('difficulty', 0.5)
        )
        
        # Analyze verification
        is_verified, confidence, final_answer = self._analyze_verification(
            initial_answer,
            verification_response
        )
        
        total_tokens = tokens1 + tokens2
        total_latency = latency1 + latency2
        
        return StrategyResult(
            answer=final_answer,
            confidence=confidence,
            tokens_used=total_tokens,
            latency=total_latency,
            strategy_name="verification",
            intermediate_steps=[
                f"Initial Answer: {initial_answer[:200]}...",
                f"Verification: {verification_response[:200]}..."
            ],
            metadata={
                'prompt_type': 'reasoning_with_verification',
                'is_verified': is_verified,
                'initial_answer': initial_answer,
                'verification': verification_response
            }
        )
    
    def _analyze_verification(
        self, 
        initial_answer: str, 
        verification: str
    ) -> tuple:
        """
        Analyze verification response.
        
        Args:
            initial_answer: Initial answer
            verification: Verification response
            
        Returns:
            Tuple of (is_verified, confidence, final_answer)
        """
        verification_lower = verification.lower()
        
        # Check for verification signals
        positive_signals = [
            'correct', 'accurate', 'sound', 'valid', 'verified',
            'checks out', 'confirmed', 'looks good'
        ]
        negative_signals = [
            'incorrect', 'wrong', 'error', 'mistake', 'flawed',
            'invalid', 'needs revision', 'not quite'
        ]
        
        positive_count = sum(1 for signal in positive_signals if signal in verification_lower)
        negative_count = sum(1 for signal in negative_signals if signal in verification_lower)
        
        # Determine if verified
        is_verified = positive_count > negative_count
        
        # Estimate confidence
        if is_verified:
            confidence = 0.75 + min(positive_count * 0.05, 0.2)
        else:
            confidence = 0.4 - min(negative_count * 0.05, 0.2)
        
        # Use initial answer as final (in production, might revise if not verified)
        final_answer = initial_answer
        
        return is_verified, max(0.0, min(1.0, confidence)), final_answer
    
    def get_cost_multiplier(self) -> float:
        """Verification requires two LLM calls"""
        return 4.0
    
    def get_strategy_strength(self) -> float:
        """Reasoning + verification: strong, good for hard problems"""
        return 0.80
