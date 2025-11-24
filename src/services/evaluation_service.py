"""
Business logic for answer evaluation.
Orchestrates Gemini API calls and response formatting.
"""
import logging
import time
from typing import Dict
from datetime import datetime

from src.services.gemini_service import gemini_service
from src.core.config import settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating candidate answers."""
    
    def __init__(self):
        """Initialize evaluation service."""
        self.gemini = gemini_service
    
    async def evaluate_answer(
        self,
        candidate_answer: str,
        question: str = None,
        context: str = None
    ) -> Dict:
        """
        Evaluate a candidate's answer.
        
        Args:
            candidate_answer: The answer to evaluate
            question: Optional question that was asked
            context: Optional evaluation context
            
        Returns:
            Dict containing evaluation results with metadata
        """
        start_time = time.time()
        
        logger.info("Starting answer evaluation")
        
        try:
            # Call Gemini API for evaluation
            evaluation_result = await self.gemini.evaluate_answer(
                candidate_answer=candidate_answer,
                question=question,
                context=context
            )
            
            # Calculate evaluation time
            evaluation_time_ms = int((time.time() - start_time) * 1000)
            
            # Build response with metadata
            response = {
                "score": evaluation_result["score"],
                "summary": evaluation_result["summary"],
                "improvement": evaluation_result["improvement"],
                "evaluation_time_ms": evaluation_time_ms,
                "metadata": {
                    "model": settings.GEMINI_MODEL,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
            
            logger.info(
                f"Evaluation completed in {evaluation_time_ms}ms",
                extra={
                    "score": response["score"],
                    "time_ms": evaluation_time_ms
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
            raise


# Create global instance
evaluation_service = EvaluationService()
