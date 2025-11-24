"""
API routes for candidate ranking.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.ranking import RankingRequest, RankingResponse
from src.services.ranking_service import ranking_service
from src.middleware.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rank-candidates", tags=["Ranking"])


@router.post(
    "",
    response_model=RankingResponse,
    status_code=status.HTTP_200_OK,
    summary="Rank multiple candidates",
    description="Evaluates multiple candidates and returns them ranked by score (highest to lowest).",
    dependencies=[Depends(rate_limiter)]
)
async def rank_candidates(request: RankingRequest) -> RankingResponse:
    """
    Rank multiple candidates based on their answers.
    
    - **candidates**: List of candidates with id and answer (max 50)
    
    Returns candidates sorted by score with evaluation details for each.
    """
    try:
        logger.info(f"Received ranking request for {len(request.candidates)} candidates")
        
        # Convert Pydantic models to dicts for service layer
        candidates_data = [
            {
                "id": candidate.id,
                "answer": candidate.answer,
                "metadata": candidate.metadata
            }
            for candidate in request.candidates
        ]
        
        # Call ranking service
        result = await ranking_service.rank_candidates(candidates_data)
        
        return RankingResponse(**result)
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ranking error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rank candidates. Please try again."
        )
