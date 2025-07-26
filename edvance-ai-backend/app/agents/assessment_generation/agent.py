# FILE: app/agents/assessment_generation/agent.py

import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.vertex import get_vertex_model
from app.services.vertex_rag_service import vertex_rag_service
from app.models.student import AssessmentConfig, Assessment, AssessmentQuestion
from app.core.language import SupportedLanguage, validate_language, create_language_prompt_prefix

logger = logging.getLogger(__name__)

class AssessmentGenerationAgent:
    """Agent for generating MCQ assessments using RAG documents."""
    
    def __init__(self):
        self.model = get_vertex_model()
        
    async def generate_assessment(
        self,
        config: AssessmentConfig,
        teacher_uid: str,
        language: str = "english"
    ) -> Assessment:
        """
        Generate a complete MCQ assessment based on configuration.
        
        Args:
            config: Assessment configuration
            teacher_uid: UID of the teacher requesting the assessment
            
        Returns:
            Assessment object with generated questions
        """
        try:
            # Validate and normalize language
            validated_language = validate_language(language)
            logger.info(f"Generating assessment for config {config.config_id} in {validated_language}")
            
            # Step 1: Retrieve relevant content from RAG
            relevant_content = await self._retrieve_relevant_content(
                teacher_uid=teacher_uid,
                subject=config.subject,
                grade_level=config.target_grade,
                topic=config.topic
            )
            
            if not relevant_content:
                logger.warning(f"No relevant content found for topic: {config.topic}")
                # Generate questions without RAG content (using general knowledge)
                questions = await self._generate_questions_without_rag(config, validated_language)
            else:
                # Generate questions using RAG content
                questions = await self._generate_questions_with_rag(config, relevant_content, validated_language)
            
            # Step 2: Create assessment object
            assessment_id = str(uuid.uuid4())
            
            assessment = Assessment(
                assessment_id=assessment_id,
                config_id=config.config_id,
                teacher_uid=teacher_uid,
                title=f"{config.subject} - {config.topic} (Grade {config.target_grade})",
                subject=config.subject,
                grade=config.target_grade,
                difficulty=config.difficulty_level,
                topic=config.topic,
                questions=questions,
                time_limit_minutes=config.time_limit_minutes
            )
            
            logger.info(f"Generated assessment {assessment_id} with {len(questions)} questions")
            return assessment
            
        except Exception as e:
            logger.error(f"Failed to generate assessment: {e}")
            raise
    
    async def _retrieve_relevant_content(
        self,
        teacher_uid: str,
        subject: str,
        grade_level: int,
        topic: str
    ) -> str:
        """Retrieve relevant content from RAG system."""
        try:
            # Create search query for RAG
            search_query = f"""
            Find educational content about {topic} for {subject} at grade {grade_level} level.
            Look for definitions, explanations, examples, and key concepts related to {topic}.
            """
            
            # Search in RAG system with filters
            search_filters = {
                "teacher_uid": teacher_uid,
                "subject": subject,
                "grade_level": grade_level
            }
            
            # Use vertex RAG service to search
            search_results = await vertex_rag_service.search_documents(
                query=search_query,
                filters=search_filters,
                max_results=5
            )
            
            # Combine search results into content
            relevant_content = ""
            for result in search_results:
                relevant_content += f"\n{result.get('content', '')}\n"
            
            return relevant_content.strip()
            
        except Exception as e:
            logger.error(f"Failed to retrieve RAG content: {e}")
            return ""
    
    async def _generate_questions_with_rag(
        self,
        config: AssessmentConfig,
        content: str,
        language: SupportedLanguage
    ) -> List[AssessmentQuestion]:
        """Generate questions using RAG content."""
        
        difficulty_descriptions = {
            "easy": "basic understanding and recall",
            "medium": "application and analysis", 
            "hard": "synthesis and evaluation"
        }
        
        # Create language-aware prompt
        language_prefix = create_language_prompt_prefix(language, "Educational assessment questions")
        
        prompt = f"""{language_prefix}

You are an expert educational assessment creator. Generate {config.question_count} multiple choice questions based on the provided educational content.

ASSESSMENT REQUIREMENTS:
- Subject: {config.subject}
- Topic: {config.topic}  
- Grade Level: {config.target_grade}
- Difficulty: {config.difficulty_level} ({difficulty_descriptions.get(config.difficulty_level, "standard")})
- Question Count: {config.question_count}

EDUCATIONAL CONTENT TO BASE QUESTIONS ON:
{content}

INSTRUCTIONS:
1. Create exactly {config.question_count} multiple choice questions
2. Each question should have exactly 4 options (A, B, C, D)
3. Questions should be appropriate for grade {config.target_grade} students
4. Difficulty should be {config.difficulty_level} level
5. Base questions on the provided educational content
6. Include clear explanations for correct answers
7. ALL content must be in the specified language

OUTPUT FORMAT - Return ONLY a JSON array like this:
[
  {{
    "question_text": "What is the main concept of...?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "The correct answer is A because...",
    "difficulty": "{config.difficulty_level}",
    "topic": "{config.topic}"
  }}
]

Generate exactly {config.question_count} questions following this format."""

        try:
            response = await self.model.generate_content_async(prompt)
            
            # Parse JSON response
            questions_data = self._parse_questions_response(response.text)
            
            # Convert to AssessmentQuestion objects
            questions = []
            for i, q_data in enumerate(questions_data):
                question = AssessmentQuestion(
                    question_id=str(uuid.uuid4()),
                    question_text=q_data.get("question_text", f"Question {i+1}"),
                    options=q_data.get("options", ["A", "B", "C", "D"]),
                    correct_answer=q_data.get("correct_answer", 0),
                    explanation=q_data.get("explanation", "No explanation provided"),
                    difficulty=q_data.get("difficulty", config.difficulty_level),
                    topic=q_data.get("topic", config.topic)
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate questions with RAG: {e}")
            # Fallback to generating without RAG
            return await self._generate_questions_without_rag(config, language)
    
    async def _generate_questions_without_rag(
        self,
        config: AssessmentConfig,
        language: SupportedLanguage
    ) -> List[AssessmentQuestion]:
        """Generate questions without RAG content (fallback)."""
        
        # Create language-aware prompt
        language_prefix = create_language_prompt_prefix(language, "Educational assessment questions")
        
        prompt = f"""{language_prefix}

You are an expert educational assessment creator. Generate {config.question_count} multiple choice questions for the given specifications.

ASSESSMENT REQUIREMENTS:
- Subject: {config.subject}
- Topic: {config.topic}
- Grade Level: {config.target_grade}
- Difficulty: {config.difficulty_level}
- Question Count: {config.question_count}

INSTRUCTIONS:
1. Create grade-appropriate questions for {config.subject} on the topic of {config.topic}
2. Each question should have exactly 4 options
3. Questions should be suitable for grade {config.target_grade} students
4. Difficulty should be {config.difficulty_level} level
5. Cover different aspects of the topic
6. ALL content must be in the specified language

OUTPUT FORMAT - Return ONLY a JSON array:
[
  {{
    "question_text": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Explanation for correct answer",
    "difficulty": "{config.difficulty_level}",
    "topic": "{config.topic}"
  }}
]

Generate exactly {config.question_count} questions."""

        try:
            response = await self.model.generate_content_async(prompt)
            
            # Parse JSON response
            questions_data = self._parse_questions_response(response.text)
            
            # Convert to AssessmentQuestion objects
            questions = []
            for i, q_data in enumerate(questions_data):
                question = AssessmentQuestion(
                    question_id=str(uuid.uuid4()),
                    question_text=q_data.get("question_text", f"Sample question {i+1} about {config.topic}"),
                    options=q_data.get("options", ["Option A", "Option B", "Option C", "Option D"]),
                    correct_answer=q_data.get("correct_answer", 0),
                    explanation=q_data.get("explanation", "Explanation not available"),
                    difficulty=q_data.get("difficulty", config.difficulty_level),
                    topic=q_data.get("topic", config.topic)
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate fallback questions: {e}")
            # Create basic sample questions as last resort
            return self._create_sample_questions(config)
    
    def _parse_questions_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI response and extract questions JSON."""
        try:
            # Clean up response text
            cleaned_text = response_text.strip()
            
            # Remove markdown formatting if present
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            # Find JSON array in response
            start_idx = cleaned_text.find('[')
            end_idx = cleaned_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = cleaned_text[start_idx:end_idx]
                questions_data = json.loads(json_text)
                
                if isinstance(questions_data, list):
                    return questions_data
            
            # If parsing fails, try to parse the entire cleaned text
            return json.loads(cleaned_text)
            
        except Exception as e:
            logger.error(f"Failed to parse questions response: {e}")
            logger.debug(f"Response text: {response_text}")
            return []
    
    def _create_sample_questions(self, config: AssessmentConfig) -> List[AssessmentQuestion]:
        """Create basic sample questions as fallback."""
        questions = []
        
        for i in range(min(config.question_count, 5)):  # Max 5 sample questions
            question = AssessmentQuestion(
                question_id=str(uuid.uuid4()),
                question_text=f"Sample {config.subject} question {i+1} about {config.topic}?",
                options=[f"Option A for question {i+1}", f"Option B for question {i+1}", 
                        f"Option C for question {i+1}", f"Option D for question {i+1}"],
                correct_answer=0,  # Always A for samples
                explanation=f"This is a sample question for {config.topic}",
                difficulty=config.difficulty_level,
                topic=config.topic
            )
            questions.append(question)
        
        return questions

# Global instance
assessment_generation_agent = AssessmentGenerationAgent()
