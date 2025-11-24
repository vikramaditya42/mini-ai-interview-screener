"""
Integration tests for /evaluate-answer endpoint.
"""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
class TestEvaluateEndpoint:
    """Test suite for evaluation endpoint."""
    
    def test_evaluate_answer_success(self, client, sample_evaluation_request, mock_gemini_response):
        """Test successful evaluation request."""
        with patch(
            'src.services.gemini_service.gemini_service.evaluate_answer',
            new_callable=AsyncMock,
            return_value=mock_gemini_response
        ):
            response = client.post(
                "/api/v1/evaluate-answer",
                json=sample_evaluation_request
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "score" in data
        assert "summary" in data
        assert "improvement" in data
        assert "evaluation_time_ms" in data
        assert "metadata" in data
        
        assert 1 <= data["score"] <= 5
        assert isinstance(data["summary"], str)
        assert isinstance(data["improvement"], str)
        assert data["metadata"]["model"] == "gemini-2.5-flash"
    
    def test_evaluate_answer_minimal_request(self, client, mock_gemini_response):
        """Test evaluation with only required fields."""
        with patch(
            'src.services.gemini_service.gemini_service.evaluate_answer',
            new_callable=AsyncMock,
            return_value=mock_gemini_response
        ):
            response = client.post(
                "/api/v1/evaluate-answer",
                json={"candidate_answer": "Python is great"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
    
    def test_evaluate_answer_empty_string(self, client):
        """Test validation for empty answer."""
        response = client.post(
            "/api/v1/evaluate-answer",
            json={"candidate_answer": ""}
        )
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_evaluate_answer_whitespace_only(self, client):
        """Test validation for whitespace-only answer."""
        response = client.post(
            "/api/v1/evaluate-answer",
            json={"candidate_answer": "   "}
        )
        
        assert response.status_code == 422
    
    def test_evaluate_answer_missing_field(self, client):
        """Test validation for missing required field."""
        response = client.post(
            "/api/v1/evaluate-answer",
            json={"question": "What is Python?"}
        )
        
        assert response.status_code == 422
    
    def test_evaluate_answer_too_long(self, client):
        """Test validation for answer exceeding max length."""
        long_answer = "a" * 6000  # Exceeds 5000 char limit
        
        response = client.post(
            "/api/v1/evaluate-answer",
            json={"candidate_answer": long_answer}
        )
        
        assert response.status_code == 422


@pytest.mark.integration
class TestEvaluateEndpointErrorHandling:
    """Test error handling for evaluation endpoint."""
    
    def test_evaluate_answer_api_error(self, client, sample_evaluation_request):
        """Test handling of API errors."""
        with patch(
            'src.services.gemini_service.gemini_service.evaluate_answer',
            new_callable=AsyncMock,
            side_effect=Exception("API Error")
        ):
            response = client.post(
                "/api/v1/evaluate-answer",
                json=sample_evaluation_request
            )
        
        assert response.status_code == 500
        assert "detail" in response.json()
