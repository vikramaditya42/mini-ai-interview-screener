"""
Integration tests for /rank-candidates endpoint.
"""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
class TestRankingEndpoint:
    """Test suite for ranking endpoint."""
    
    def test_rank_candidates_success(self, client, sample_ranking_request):
        """Test successful ranking request."""
        # Mock different scores for each candidate
        mock_responses = [
            {"score": 2, "summary": "Basic answer", "improvement": "Add more detail"},
            {"score": 5, "summary": "Excellent answer", "improvement": "None needed"},
            {"score": 3, "summary": "Decent answer", "improvement": "Explain more"}
        ]
        
        call_count = [0]
        
        async def mock_evaluate(*args, **kwargs):
            response = mock_responses[call_count[0]]
            call_count[0] += 1
            return response
        
        with patch(
            'src.services.gemini_service.gemini_service.evaluate_answer',
            new_callable=AsyncMock,
            side_effect=mock_evaluate
        ):
            response = client.post(
                "/api/v1/rank-candidates",
                json=sample_ranking_request
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ranked_candidates" in data
        assert "total_candidates" in data
        assert "evaluation_time_ms" in data
        
        assert data["total_candidates"] == 3
        
        # Check ranking order
        ranked = data["ranked_candidates"]
        assert len(ranked) == 3
        
        # First candidate should have highest score
        assert ranked[0]["rank"] == 1
        assert ranked[0]["score"] >= ranked[1]["score"]
        
        # Each candidate has required fields
        for candidate in ranked:
            assert "id" in candidate
            assert "score" in candidate
            assert "summary" in candidate
            assert "improvement" in candidate
            assert "rank" in candidate
    
    def test_rank_single_candidate(self, client, mock_gemini_response):
        """Test ranking with single candidate."""
        with patch(
            'src.services.gemini_service.gemini_service.evaluate_answer',
            new_callable=AsyncMock,
            return_value=mock_gemini_response
        ):
            response = client.post(
                "/api/v1/rank-candidates",
                json={
                    "candidates": [
                        {"id": "c1", "answer": "Great answer"}
                    ]
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_candidates"] == 1
        assert data["ranked_candidates"][0]["rank"] == 1
    
    def test_rank_candidates_with_metadata(self, client, mock_gemini_response):
        """Test ranking preserves candidate metadata."""
        with patch(
            'src.services.gemini_service.gemini_service.evaluate_answer',
            new_callable=AsyncMock,
            return_value=mock_gemini_response
        ):
            response = client.post(
                "/api/v1/rank-candidates",
                json={
                    "candidates": [
                        {
                            "id": "c1",
                            "answer": "Answer",
                            "metadata": {"name": "John Doe", "email": "john@example.com"}
                        }
                    ]
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ranked_candidates"][0]["metadata"]["name"] == "John Doe"
    
    def test_rank_candidates_empty_list(self, client):
        """Test validation for empty candidates list."""
        response = client.post(
            "/api/v1/rank-candidates",
            json={"candidates": []}
        )
        
        assert response.status_code == 422
    
    def test_rank_candidates_duplicate_ids(self, client):
        """Test validation for duplicate candidate IDs."""
        response = client.post(
            "/api/v1/rank-candidates",
            json={
                "candidates": [
                    {"id": "c1", "answer": "Answer 1"},
                    {"id": "c1", "answer": "Answer 2"}
                ]
            }
        )
        
        assert response.status_code == 422
    
    def test_rank_candidates_exceeds_max(self, client):
        """Test validation for too many candidates."""
        candidates = [
            {"id": f"c{i}", "answer": f"Answer {i}"}
            for i in range(51)  # Exceeds max of 50
        ]
        
        response = client.post(
            "/api/v1/rank-candidates",
            json={"candidates": candidates}
        )
        
        assert response.status_code == 422
