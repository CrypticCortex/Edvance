# FILE: app/agents/question_stub_agent.py

import logging
from typing import List, Dict, Any, Optional
import uuid

from app.models.rag_models import (
    RAGResult, 
    QuestionGenerationRequest, 
    EnhancedAssessmentQuestion,
    GeneratedQuestionContext
)

logger = logging.getLogger(__name__)

class QuestionStubAgent:
    """Stub question generator for when AI dependencies aren't available."""
    
    def __init__(self):
        self.is_ai_enabled = False
        logger.warning("Using question stub agent - AI generation not available")
    
    async def generate_questions(
        self,
        request: QuestionGenerationRequest
    ) -> List[EnhancedAssessmentQuestion]:
        """Generate simple template questions as fallback."""
        
        logger.info(f"Stub agent: would generate {request.question_count} questions for {request.subject}")
        
        questions = []
        
        # Create simple template questions based on subject
        templates = self._get_templates(request.subject, request.grade_level)
        
        for i in range(min(request.question_count, len(templates))):
            template = templates[i % len(templates)]
            
            question = EnhancedAssessmentQuestion(
                question_id=f"stub_{uuid.uuid4()}_{i}",
                question_text=template["question"],
                options=template["options"],
                correct_answer=template["correct"],
                explanation=template["explanation"],
                difficulty=request.difficulty_level,
                topic=request.topic,
                context=GeneratedQuestionContext(
                    source_chunks=[],
                    confidence_score=0.5,  # Low confidence for stub
                    generation_metadata={
                        "model": "stub",
                        "method": "template",
                        "ai_enabled": False
                    }
                ),
                bloom_taxonomy_level="Remember",
                learning_objectives=[f"Basic {request.topic} understanding"]
            )
            questions.append(question)
        
        return questions
    
    def _get_templates(self, subject: str, grade_level: int) -> List[Dict[str, Any]]:
        """Get simple question templates by subject."""
        
        print("Still using Simple")
        templates = {
            "Mathematics": [
                {
                    "question": "What is 2 + 3?",
                    "options": ["4", "5", "6", "7"],
                    "correct": 1,
                    "explanation": "2 + 3 = 5"
                },
                {
                    "question": "What is 10 - 4?",
                    "options": ["5", "6", "7", "8"],
                    "correct": 1,
                    "explanation": "10 - 4 = 6"
                }
            ],
            "Science": [
                {
                    "question": "What planet is closest to the Sun?",
                    "options": ["Venus", "Mercury", "Earth", "Mars"],
                    "correct": 1,
                    "explanation": "Mercury is the closest planet to the Sun"
                }
            ],
            "English": [
                {
                    "question": "What is a noun?",
                    "options": ["Action word", "Describing word", "Person, place, or thing", "Connecting word"],
                    "correct": 2,
                    "explanation": "A noun is a person, place, or thing"
                }
            ]
        }
        
        return templates.get(subject, templates["Mathematics"])
