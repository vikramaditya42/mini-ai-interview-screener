"""
Business logic for ranking candidates.
Evaluates multiple candidates and ranks them by score.
"""
import logging
import time
import asyncio
from typing import List, Dict, Any

from src.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class RankingService:
    """Service for ranking multiple candidates."""
    
    def __init__(self):
        """Initialize ranking service."""
        self.gemini = gemini_service
    
    async def rank_candidates(self, candidates: List[Dict[str, Any]]) -> Dict:
        """
        Evaluate and rank multiple candidates.
        
        Args:
            candidates: List of candidate objects with id, answer, and optional metadata
            
        Returns:
            Dict containing ranked candidates and metadata
        """
        start_time = time.time()
        
        logger.info(f"Starting evaluation of {len(candidates)} candidates")
        
        try:
            # Evaluate all candidates concurrently
            evaluation_tasks = [
                self._evaluate_single_candidate(candidate)
                for candidate in candidates
            ]
            
            evaluated_candidates = await asyncio.gather(*evaluation_tasks)
            
            # Sort by score (descending) and add rank
            ranked_candidates = self._sort_and_rank(evaluated_candidates)
            
            # Calculate total time
            evaluation_time_ms = int((time.time() - start_time) * 1000)
            
            response = {
                "ranked_candidates": ranked_candidates,
                "total_candidates": len(ranked_candidates),
                "evaluation_time_ms": evaluation_time_ms
            }
            
            logger.info(
                f"Ranking completed for {len(candidates)} candidates in {evaluation_time_ms}ms",
                extra={
                    "total_candidates": len(candidates),
                    "time_ms": evaluation_time_ms
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Ranking failed: {str(e)}", exc_info=True)
            raise
    
    async def _evaluate_single_candidate(self, candidate: Dict[str, Any]) -> Dict:
        """
        Evaluate a single candidate.
        
        Args:
            candidate: Dict with id, answer, and optional metadata
            
        Returns:
            Dict with evaluation results and candidate info
        """
        try:
            evaluation = await self.gemini.evaluate_answer(
                candidate_answer=candidate["answer"]
            )
            
            return {
                "id": candidate["id"],
                "score": evaluation["score"],
                "summary": evaluation["summary"],
                "improvement": evaluation["improvement"],
                "metadata": candidate.get("metadata")
            }
            
        except Exception as e:
            logger.error(
                f"Failed to evaluate candidate {candidate['id']}: {str(e)}",
                exc_info=True
            )
            # Return a default low score if evaluation fails
            return {
                "id": candidate["id"],
                "score": 1,
                "summary": "Evaluation failed",
                "improvement": "Unable to evaluate this response",
                "metadata": candidate.get("metadata")
            }
    
    def _sort_and_rank(self, evaluated_candidates: List[Dict]) -> List[Dict]:
        """
        Sort candidates by score and assign ranks.
        
        Args:
            evaluated_candidates: List of evaluated candidate dicts
            
        Returns:
            List of candidates sorted by score with rank assigned
        """
        # Sort by score (descending), then by id (for consistent tie-breaking)
        sorted_candidates = sorted(
            evaluated_candidates,
            key=lambda x: (-x["score"], x["id"])
        )
        
        # Assign ranks
        for rank, candidate in enumerate(sorted_candidates, start=1):
            candidate["rank"] = rank
        
        return sorted_candidates


# Create global instance
ranking_service = RankingService()
