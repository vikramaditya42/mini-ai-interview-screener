"""
API routes for answer evaluation.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.evaluation import EvaluationRequest, EvaluationResponse
from src.services.evaluation_service import evaluation_service
from src.middleware.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluate-answer", tags=["Evaluation"])


@router.post(
    "",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate a candidate's answer",
    description="Evaluates a candidate's answer using AI and returns a score (1-5), summary, and improvement suggestion.",
    dependencies=[Depends(rate_limiter)]
)
async def evaluate_answer(request: EvaluationRequest) -> EvaluationResponse:
    """
    Evaluate a candidate's answer.
    
    - **candidate_answer**: The answer text to evaluate (required)
    - **question**: Optional interview question context
    - **context**: Optional additional context for evaluation
    
    Returns evaluation with score, summary, improvement suggestion, and metadata.
    """
    try:
        logger.info("Received evaluation request")
        
        # Call evaluation service
        result = await evaluation_service.evaluate_answer(
            candidate_answer=request.candidate_answer,
            question=request.question,
            context=request.context
        )
        
        return EvaluationResponse(**result)
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate answer. Please try again."
        )
