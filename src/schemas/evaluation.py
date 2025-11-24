"""
Pydantic schemas for evaluation endpoints.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class EvaluationRequest(BaseModel):
    """Request schema for answer evaluation."""
    
    candidate_answer: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The candidate's answer to evaluate"
    )
    question: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional: The interview question that was asked"
    )
    context: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional: Additional context for evaluation"
    )
    
    @field_validator('candidate_answer')
    @classmethod
    def validate_answer_not_empty(cls, v: str) -> str:
        """Ensure answer is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("candidate_answer cannot be empty or whitespace")
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "candidate_answer": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
                    "question": "What is Python?",
                    "context": "Technical screening for junior developer position"
                }
            ]
        }
    }


class EvaluationMetadata(BaseModel):
    """Metadata for evaluation response."""
    
    model: str = Field(..., description="AI model used for evaluation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EvaluationResponse(BaseModel):
    """Response schema for answer evaluation."""
    
    score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Score from 1 to 5"
    )
    summary: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="One-line summary of the answer"
    )
    improvement: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="One improvement suggestion"
    )
    evaluation_time_ms: int = Field(
        ...,
        ge=0,
        description="Time taken for evaluation in milliseconds"
    )
    metadata: EvaluationMetadata
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "score": 4,
                    "summary": "Good explanation covering key aspects of Python",
                    "improvement": "Could mention specific use cases or popular frameworks",
                    "evaluation_time_ms": 850,
                    "metadata": {
                        "model": "gemini-2.5-flash",
                        "timestamp": "2025-11-24T16:15:00Z"
                    }
                }
            ]
        }
    }
