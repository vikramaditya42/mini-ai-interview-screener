"""
Unit tests for ranking service.
"""
import pytest
from unittest.mock import AsyncMock, patch
from src.services.ranking_service import RankingService


@pytest.mark.unit
class TestRankingService:
    """Test suite for RankingService."""
    
    @pytest.mark.asyncio
    async def test_rank_candidates_success(self):
        """Test successful candidate ranking."""
        service = RankingService()
        
        # Mock evaluations with different scores
        mock_evaluations = [
            {"score": 3, "summary": "Basic", "improvement": "Add depth"},
            {"score": 5, "summary": "Excellent", "improvement": "None"},
            {"score": 4, "summary": "Good", "improvement": "Minor tweaks"}
        ]
        
        candidates = [
            {"id": "c1", "answer": "Answer 1"},
            {"id": "c2", "answer": "Answer 2"},
            {"id": "c3", "answer": "Answer 3"}
        ]
        
        call_index = [0]
        
        # Fix: Accept **kwargs in mock function
        async def mock_eval(*args, **kwargs):
            # Return evaluations in order
            result = mock_evaluations[call_index[0]]
            call_index[0] += 1
            return result
        
        with patch.object(
            service.gemini,
            'evaluate_answer',
            new_callable=AsyncMock,
            side_effect=mock_eval
        ):
            result = await service.rank_candidates(candidates)
        
        # Assertions
        assert result["total_candidates"] == 3
        assert "ranked_candidates" in result
        assert len(result["ranked_candidates"]) == 3
        
        # Check ranking order (highest score first)
        ranked = result["ranked_candidates"]
        assert ranked[0]["rank"] == 1
        assert ranked[0]["score"] == 5
        assert ranked[1]["rank"] == 2
        assert ranked[1]["score"] == 4
        assert ranked[2]["rank"] == 3
        assert ranked[2]["score"] == 3

    
    @pytest.mark.asyncio
    async def test_rank_single_candidate(self):
        """Test ranking with single candidate."""
        service = RankingService()
        
        with patch.object(
            service.gemini,
            'evaluate_answer',
            new_callable=AsyncMock,
            return_value={"score": 5, "summary": "Great", "improvement": "None"}
        ):
            result = await service.rank_candidates([
                {"id": "c1", "answer": "Excellent answer"}
            ])
        
        assert result["total_candidates"] == 1
        assert result["ranked_candidates"][0]["rank"] == 1
    
    def test_sort_and_rank(self):
        """Test sorting and ranking logic."""
        service = RankingService()
        
        candidates = [
            {"id": "c1", "score": 3, "summary": "OK", "improvement": "More"},
            {"id": "c2", "score": 5, "summary": "Great", "improvement": "None"},
            {"id": "c3", "score": 3, "summary": "OK", "improvement": "More"}
        ]
        
        ranked = service._sort_and_rank(candidates)
        
        # Check order: highest score first, then alphabetical by id for ties
        assert ranked[0]["score"] == 5
        assert ranked[0]["rank"] == 1
        assert ranked[1]["id"] == "c1"  # c1 before c3 (alphabetical)
        assert ranked[2]["id"] == "c3"
