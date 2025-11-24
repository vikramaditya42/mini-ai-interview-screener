"""
Pytest configuration and shared fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
import os

# Set test environment variables before importing app
os.environ["GEMINI_API_KEY"] = "test_api_key_123"
os.environ["DEBUG"] = "True"
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000"  # High limit for tests

from src.main import app
from src.services.gemini_service import GeminiService


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    return {
        "score": 4,
        "summary": "Good explanation with clear understanding",
        "improvement": "Could include more specific examples"
    }


@pytest.fixture
def sample_evaluation_request():
    """Sample evaluation request data."""
    return {
        "candidate_answer": "Python is a high-level, interpreted programming language known for its readability and versatility.",
        "question": "What is Python?",
        "context": "Junior developer interview"
    }


@pytest.fixture
def sample_ranking_request():
    """Sample ranking request data."""
    return {
        "candidates": [
            {
                "id": "candidate_1",
                "answer": "Python is a programming language."
            },
            {
                "id": "candidate_2",
                "answer": "Python is a high-level, interpreted, object-oriented programming language with dynamic semantics."
            },
            {
                "id": "candidate_3",
                "answer": "Python is used for web development."
            }
        ]
    }


@pytest.fixture
def mock_gemini_service(monkeypatch, mock_gemini_response):
    """Mock the Gemini service for testing."""
    async def mock_evaluate(*args, **kwargs):
        return mock_gemini_response
    
    mock_service = Mock(spec=GeminiService)
    mock_service.evaluate_answer = AsyncMock(side_effect=mock_evaluate)
    
    return mock_service
