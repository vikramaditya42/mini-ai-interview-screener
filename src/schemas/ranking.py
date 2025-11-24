"""
Pydantic schemas for candidate ranking endpoints.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any


class CandidateInput(BaseModel):
    """Input schema for a single candidate."""
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique identifier for the candidate"
    )
    answer: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The candidate's answer"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata about the candidate"
    )
    
    @field_validator('answer')
    @classmethod
    def validate_answer_not_empty(cls, v: str) -> str:
        """Ensure answer is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("answer cannot be empty or whitespace")
        return v.strip()


class RankingRequest(BaseModel):
    """Request schema for ranking candidates."""
    
    candidates: List[CandidateInput] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of candidates to rank (max 50)"
    )
    
    @field_validator('candidates')
    @classmethod
    def validate_unique_ids(cls, v: List[CandidateInput]) -> List[CandidateInput]:
        """Ensure all candidate IDs are unique."""
        ids = [candidate.id for candidate in v]
        if len(ids) != len(set(ids)):
            raise ValueError("All candidate IDs must be unique")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "candidates": [
                        {
                            "id": "candidate_1",
                            "answer": "Python is a high-level programming language.",
                            "metadata": {"name": "John Doe"}
                        },
                        {
                            "id": "candidate_2",
                            "answer": "Python is an interpreted, object-oriented language with dynamic semantics."
                        }
                    ]
                }
            ]
        }
    }


class RankedCandidate(BaseModel):
    """Schema for a ranked candidate with evaluation."""
    
    id: str
    score: int = Field(ge=1, le=5)
    summary: str
    improvement: str
    rank: int = Field(ge=1, description="Rank position (1 is highest)")
    metadata: Optional[Dict[str, Any]] = None


class RankingResponse(BaseModel):
    """Response schema for candidate ranking."""
    
    ranked_candidates: List[RankedCandidate] = Field(
        ...,
        description="Candidates sorted by score (highest first)"
    )
    total_candidates: int = Field(..., ge=0)
    evaluation_time_ms: int = Field(..., ge=0)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ranked_candidates": [
                        {
                            "id": "candidate_2",
                            "score": 5,
                            "summary": "Comprehensive answer with technical details",
                            "improvement": "Could add practical examples",
                            "rank": 1,
                            "metadata": None
                        },
                        {
                            "id": "candidate_1",
                            "score": 3,
                            "summary": "Basic definition provided",
                            "improvement": "Needs more depth and technical accuracy",
                            "rank": 2,
                            "metadata": {"name": "John Doe"}
                        }
                    ],
                    "total_candidates": 2,
                    "evaluation_time_ms": 1750
                }
            ]
        }
    }
