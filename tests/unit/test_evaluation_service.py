"""
Unit tests for evaluation service.
"""
import pytest
from unittest.mock import AsyncMock, patch
from src.services.evaluation_service import EvaluationService


@pytest.mark.unit
class TestEvaluationService:
    """Test suite for EvaluationService."""
    
    @pytest.mark.asyncio
    async def test_evaluate_answer_success(self, mock_gemini_response):
        """Test successful answer evaluation."""
        service = EvaluationService()
        
        # Mock the Gemini service
        with patch.object(
            service.gemini,
            'evaluate_answer',
            new_callable=AsyncMock,
            return_value=mock_gemini_response
        ):
            result = await service.evaluate_answer(
                candidate_answer="Python is a programming language"
            )
        
        # Assertions
        assert result["score"] == 4
        assert "summary" in result
        assert "improvement" in result
        assert "evaluation_time_ms" in result
        assert "metadata" in result
        assert result["metadata"]["model"] == "gemini-2.5-flash"
    
    @pytest.mark.asyncio
    async def test_evaluate_answer_with_context(self, mock_gemini_response):
        """Test evaluation with question and context."""
        service = EvaluationService()
        
        with patch.object(
            service.gemini,
            'evaluate_answer',
            new_callable=AsyncMock,
            return_value=mock_gemini_response
        ):
            result = await service.evaluate_answer(
                candidate_answer="Python is versatile",
                question="What is Python?",
                context="Senior developer interview"
            )
        
        assert "score" in result
        assert result["evaluation_time_ms"] >= 0
    
    @pytest.mark.asyncio
    async def test_evaluate_answer_failure(self):
        """Test evaluation failure handling."""
        service = EvaluationService()
        
        with patch.object(
            service.gemini,
            'evaluate_answer',
            new_callable=AsyncMock,
            side_effect=Exception("API Error")
        ):
            with pytest.raises(Exception):
                await service.evaluate_answer(
                    candidate_answer="Test answer"
                )


@pytest.mark.unit
class TestGeminiServicePromptBuilding:
    """Test Gemini service prompt building."""
    
    def test_build_evaluation_prompt_basic(self):
        """Test basic prompt building."""
        from src.services.gemini_service import GeminiService
        
        service = GeminiService()
        prompt = service._build_evaluation_prompt("Python is great")
        
        assert "Python is great" in prompt
        assert "score" in prompt.lower()
        assert "summary" in prompt.lower()
        assert "improvement" in prompt.lower()
    
    def test_build_evaluation_prompt_with_context(self):
        """Test prompt with question and context."""
        from src.services.gemini_service import GeminiService
        
        service = GeminiService()
        prompt = service._build_evaluation_prompt(
            answer="Python is great",
            question="What is Python?",
            context="Technical interview"
        )
        
        assert "Python is great" in prompt
        assert "What is Python?" in prompt
        assert "Technical interview" in prompt
