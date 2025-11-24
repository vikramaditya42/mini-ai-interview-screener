"""
Service for interacting with Google Gemini API.
Handles AI model calls and response parsing.
"""
import logging
import json
import re
from typing import Dict, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for Google Gemini API interactions."""
    
    def __init__(self):
        """Initialize Gemini API client."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
        
        # Configure the Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": 0.3,  # Lower temperature for more consistent scoring
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        logger.info(f"Gemini service initialized with model: {settings.GEMINI_MODEL}")
    
    async def evaluate_answer(
        self, 
        candidate_answer: str,
        question: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict:
        """
        Evaluate a candidate's answer using Gemini AI.
        
        Args:
            candidate_answer: The candidate's answer text
            question: Optional question that was asked
            context: Optional additional context
            
        Returns:
            Dict with score, summary, and improvement
            
        Raises:
            Exception: If API call fails or response parsing fails
        """
        try:
            prompt = self._build_evaluation_prompt(candidate_answer, question, context)
            
            logger.info("Sending evaluation request to Gemini API")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            # Extract text from response
            response_text = response.text
            logger.debug(f"Received response: {response_text[:200]}...")
            
            # Parse the JSON response
            evaluation = self._parse_evaluation_response(response_text)
            
            logger.info(
                f"Evaluation completed successfully",
                extra={"score": evaluation.get("score")}
            )
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error during Gemini API call: {str(e)}", exc_info=True)
            raise Exception(f"Failed to evaluate answer: {str(e)}")
    
    def _build_evaluation_prompt(
        self,
        answer: str,
        question: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Build the evaluation prompt for Gemini.
        
        Args:
            answer: Candidate's answer
            question: Optional question
            context: Optional context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "You are an expert technical interviewer evaluating candidate responses.",
            "Your task is to provide a fair, objective assessment.\n"
        ]
        
        if context:
            prompt_parts.append(f"Context: {context}\n")
        
        if question:
            prompt_parts.append(f"Question Asked: {question}\n")
        
        prompt_parts.extend([
            f"Candidate's Answer: \"{answer}\"\n",
            "Evaluate this answer and provide your assessment in STRICT JSON format.\n",
            "Scoring Guide:",
            "- 5: Exceptional - comprehensive, accurate, well-structured with depth",
            "- 4: Good - correct understanding with minor gaps, solid explanation",
            "- 3: Adequate - shows basic understanding but lacks depth or has minor errors",
            "- 2: Weak - significant gaps in understanding or multiple errors",
            "- 1: Poor - incorrect, irrelevant, or completely missing the point\n",
            "Return ONLY a valid JSON object with this EXACT structure (no markdown, no code blocks, no additional text):",
            "{",
            '  "score": <integer 1-5>,',
            '  "summary": "<one concise sentence summarizing the answer quality>",',
            '  "improvement": "<one specific, actionable suggestion for improvement>"',
            "}"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_evaluation_response(self, response_text: str) -> Dict:
        """
        Parse Gemini's response and extract evaluation data.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            Dict with score, summary, and improvement
            
        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Remove markdown code blocks if present
            cleaned_text = re.sub(r'``````', '', response_text)
            cleaned_text = cleaned_text.strip()
            
            # Try to find JSON object in the response
            json_match = re.search(r'\{[^}]+\}', cleaned_text, re.DOTALL)
            if json_match:
                cleaned_text = json_match.group(0)
            
            # Parse JSON
            evaluation = json.loads(cleaned_text)
            
            # Validate required fields
            required_fields = ["score", "summary", "improvement"]
            for field in required_fields:
                if field not in evaluation:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate score range
            score = evaluation["score"]
            if not isinstance(score, int) or score < 1 or score > 5:
                raise ValueError(f"Invalid score value: {score}. Must be integer 1-5")
            
            # Validate string fields
            if not isinstance(evaluation["summary"], str) or not evaluation["summary"].strip():
                raise ValueError("Summary must be a non-empty string")
            
            if not isinstance(evaluation["improvement"], str) or not evaluation["improvement"].strip():
                raise ValueError("Improvement must be a non-empty string")
            
            return {
                "score": score,
                "summary": evaluation["summary"].strip(),
                "improvement": evaluation["improvement"].strip()
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_text}")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing evaluation response: {str(e)}")
            raise ValueError(f"Failed to parse evaluation: {str(e)}")


# Create global instance
gemini_service = GeminiService()
