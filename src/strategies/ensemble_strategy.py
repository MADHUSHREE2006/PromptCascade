"""
Ensemble Strategy with Verification
Generates multiple candidate answers and uses a verifier to select the best one.
"""

from strategies.base_strategy import BaseStrategy, StrategyResult
from typing import List, Optional
import random
import logging

logger = logging.getLogger(__name__)


class EnsembleStrategy(BaseStrategy):
    """
    Multiple Candidates + Verifier: Generate multiple answers, then verify and select best.
    
    Cost multiplier: 6.0 (N candidates + verifier call)
    Best for: Very hard questions requiring highest accuracy
    """
    
    def __init__(self, llm_client=None, num_candidates: int = 3):
        """
        Args:
            llm_client: LLM client
            num_candidates: Number of candidate answers to generate
        """
        super().__init__(llm_client)
        self.num_candidates = num_candidates
    
    def execute(self, query: str, **kwargs) -> StrategyResult:
        """
        Execute ensemble strategy with verification.
        
        Args:
            query: Input question
            **kwargs: Additional parameters
            
        Returns:
            StrategyResult with best verified answer
        """
        logger.info(
            f"Executing Ensemble Strategy with {self.num_candidates} candidates on: {query[:50]}..."
        )
        
        # Step 1: Generate multiple candidate answers
        candidates = []
        total_tokens = 0
        total_latency = 0.0
        
        for i in range(self.num_candidates):
            # Vary temperature slightly for diversity
            temp = kwargs.get('temperature', 0.7) + (i * 0.1 - 0.1)
            temp = max(0.3, min(temp, 1.0))
            
            candidate_prompt = f"""Question: {query}

Please provide a detailed answer with reasoning:"""
            
            answer, tokens, latency = self._call_llm(
                candidate_prompt,
                temperature=temp,
                max_tokens=kwargs.get('max_tokens', 1024),
                ground_truth=kwargs.get('ground_truth'),
                difficulty=kwargs.get('difficulty', 0.5)
            )
            
            candidates.append({
                'answer': answer,
                'candidate_id': i,
                'temperature': temp
            })
            
            total_tokens += tokens
            total_latency += latency
        
        # Step 2: Use verifier to select best answer
        best_answer, verification, confidence = self._verify_and_select(
            query, candidates, 
            ground_truth=kwargs.get('ground_truth'),
            difficulty=kwargs.get('difficulty', 0.5)
        )
        
        # Verifier call
        verifier_tokens, verifier_latency = 0, 0.0
        if verification:  # If we actually called the verifier
            # Estimate verifier cost
            verifier_tokens = len(verification.split()) * 2
            verifier_latency = 1.0
            total_tokens += verifier_tokens
            total_latency += verifier_latency
        
        return StrategyResult(
            answer=best_answer,
            confidence=confidence,
            tokens_used=total_tokens,
            latency=total_latency,
            strategy_name="ensemble",
            intermediate_steps=[
                f"Candidate {i+1}: {c['answer'][:100]}..." 
                for i, c in enumerate(candidates)
            ],
            metadata={
                'prompt_type': 'ensemble_with_verification',
                'num_candidates': self.num_candidates,
                'all_candidates': candidates,
                'verification': verification
            }
        )
    
    def _verify_and_select(
        self, 
        query: str, 
        candidates: List[dict],
        ground_truth: Optional[str] = None,
        difficulty: float = 0.5
    ) -> tuple:
        """
        Verify candidates and select the best answer.
        
        In offline (mock) mode, models the ensemble benefit realistically:
        each candidate is independently correct/wrong, and the verifier picks
        a correct candidate if one exists (with high probability), otherwise
        picks a wrong one. This gives ensembles a higher effective success
        rate than a single attempt.
        
        Args:
            query: Original question
            candidates: List of candidate answer dicts
            ground_truth: Correct answer (for offline selection)
            difficulty: Problem difficulty
            
        Returns:
            Tuple of (best_answer, verification_response, confidence)
        """
        # Create verification prompt for token/cost accounting
        candidates_text = "\n\n".join([
            f"Candidate {i+1}:\n{c['answer']}"
            for i, c in enumerate(candidates)
        ])
        
        verification_prompt = f"""Original Question: {query}

Here are {len(candidates)} candidate answers:

{candidates_text}

Please analyze each candidate and select the best answer by considering:
1) Correctness and accuracy
2) Completeness of the answer
3) Quality of reasoning
4) Clarity of explanation

Which candidate is best and why? Provide the number of the best candidate and your reasoning:"""
        
        verification, tokens, latency = self._call_llm(
            verification_prompt,
            temperature=0.3,
            max_tokens=512,
            ground_truth=ground_truth,
            difficulty=difficulty
        )
        
        # --- Realistic ensemble selection (offline mode) ---
        if ground_truth is not None and self.llm_client is None:
            gt_norm = str(ground_truth).strip().lower()
            # Find which candidates are correct (match ground truth)
            correct_indices = [
                i for i, c in enumerate(candidates)
                if str(c['answer']).strip().lower() == gt_norm
            ]
            # Verifier correctly identifies a right answer if one exists
            # (with small probability of failure on very hard problems)
            verifier_fails = (random.random() < difficulty * 0.15)
            if correct_indices and not verifier_fails:
                best_idx = random.choice(correct_indices)
                confidence = 0.85
            else:
                # No correct candidate (or verifier failed): pick any
                best_idx = 0
                confidence = 0.55
        else:
            # Real LLM mode: parse verification to find best candidate
            best_idx, confidence = self._parse_verification(verification, len(candidates))
        
        best_answer = candidates[best_idx]['answer']
        
        return best_answer, verification, confidence
    
    def _parse_verification(self, verification: str, num_candidates: int) -> tuple:
        """
        Parse verification response to find best candidate.
        
        Args:
            verification: Verification response
            num_candidates: Number of candidates
            
        Returns:
            Tuple of (best_candidate_idx, confidence)
        """
        verification_lower = verification.lower()
        
        # Look for candidate number
        for i in range(num_candidates):
            patterns = [
                f'candidate {i+1}',
                f'answer {i+1}',
                f'option {i+1}',
                f'#{i+1}',
                f'({i+1})'
            ]
            
            # Find first mention
            positions = []
            for pattern in patterns:
                pos = verification_lower.find(pattern)
                if pos != -1:
                    positions.append((pos, i))
            
            if positions:
                # Use earliest mention
                positions.sort()
                best_idx = positions[0][1]
                
                # Estimate confidence
                confidence = 0.8  # High confidence due to ensemble
                
                # Increase confidence if verification is strongly positive
                strong_words = ['clearly', 'definitely', 'obviously', 'best', 'superior']
                if any(word in verification_lower for word in strong_words):
                    confidence += 0.1
                
                return best_idx, min(1.0, confidence)
        
        # Default to first candidate if parsing fails
        logger.warning("Could not parse verification response. Using first candidate.")
        return 0, 0.6
    
    def get_cost_multiplier(self) -> float:
        """Ensemble with verification is most expensive"""
        return 6.0
    
    def get_strategy_strength(self) -> float:
        """Ensemble: strongest single-attempt strength, plus ensemble benefit"""
        return 0.90
