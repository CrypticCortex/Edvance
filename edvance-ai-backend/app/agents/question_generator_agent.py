# FILE: app/agents/question_generator_agent.py

import logging
from typing import List, Dict, Any, Optional
import json
import asyncio

try:
    from langchain.agents import AgentType, initialize_agent
    from langchain.tools import Tool
    from langchain.schema import HumanMessage, SystemMessage
    from langchain_google_vertexai import ChatVertexAI
    from langchain.prompts import PromptTemplate
    from langchain.output_parsers import PydanticOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback imports will be handled in initialization
    LANGCHAIN_AVAILABLE = False
    ChatVertexAI = None
    HumanMessage = None

from app.models.rag_models import (
    RAGResult, 
    QuestionGenerationRequest, 
    EnhancedAssessmentQuestion,
    GeneratedQuestionContext
)
from app.models.student import AssessmentQuestion
from app.core.config import settings
from app.core.language import SupportedLanguage, validate_language, create_language_prompt_prefix

logger = logging.getLogger(__name__)

class QuestionGeneratorAgent:
    """AI Agent for generating assessment questions from RAG context."""
    
    def __init__(self):
        self.settings = settings
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM for question generation."""
        try:
            if not LANGCHAIN_AVAILABLE:
                logger.warning("LangChain not available, question generation will be limited")
                self.llm = None
                return
                
            # Initialize Vertex AI LLM
            self.llm = ChatVertexAI(
                model_name="gemini-2.5-pro",
                project=self.settings.google_cloud_project or self.settings.firebase_project_id,
                location=self.settings.google_cloud_location,
                temperature=0.3,  # Lower temperature for more consistent questions
                max_output_tokens=2048
            )
            logger.info("Initialized Vertex AI LLM for question generation")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI LLM: {str(e)}")
            # Could add fallback to other LLMs here
            self.llm = None
    
    async def generate_questions(
        self,
        request: QuestionGenerationRequest
    ) -> List[EnhancedAssessmentQuestion]:
        """Generate assessment questions from RAG context."""
        
        if not self.llm or not LANGCHAIN_AVAILABLE:
            logger.error("LLM not initialized or LangChain not available, cannot generate questions")
            return []
        
        try:
            # Prepare context from RAG results
            context_text = self._prepare_context(request.context_chunks)
            
            # Generate questions in batches if needed
            all_questions = []
            batch_size = min(3, request.question_count)  # Generate 3 at a time max
            
            for i in range(0, request.question_count, batch_size):
                remaining = min(batch_size, request.question_count - i)
                
                batch_questions = await self._generate_question_batch(
                    context_text=context_text,
                    subject=request.subject,
                    grade_level=request.grade_level,
                    topic=request.topic,
                    difficulty=request.difficulty_level,
                    count=remaining,
                    context_chunks=request.context_chunks,
                    language=request.language
                )
                
                all_questions.extend(batch_questions)
                
                # Small delay between batches to avoid rate limits
                if i + batch_size < request.question_count:
                    await asyncio.sleep(1)
            
            logger.info(f"Generated {len(all_questions)} questions for {request.subject} grade {request.grade_level}")
            return all_questions[:request.question_count]  # Ensure exact count
            
        except Exception as e:
            logger.error(f"Question generation failed: {str(e)}")
            return []
    
    def _prepare_context(self, context_chunks: List[RAGResult]) -> str:
        """Prepare context text from RAG results."""
        
        if not context_chunks:
            return "No specific context available."
        
        context_parts = []
        for i, result in enumerate(context_chunks, 1):
            chunk_text = result.chunk.content.strip()
            source = result.document_metadata.get("filename", "Unknown source")
            
            context_part = f"""
Context {i} (from {source}):
{chunk_text}
            """.strip()
            context_parts.append(context_part)
        
        return "\\n\\n".join(context_parts)
    
    async def _generate_question_batch(
        self,
        context_text: str,
        subject: str,
        grade_level: int,
        topic: str,
        difficulty: str,
        count: int,
        context_chunks: List[RAGResult],
        language: str = "english"
    ) -> List[EnhancedAssessmentQuestion]:
        """Generate a batch of questions."""
        
        try:
            # Create the prompt
            prompt = self._create_question_prompt(
                context_text, subject, grade_level, topic, difficulty, count, language
            )
            
            # Get response from LLM
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse the response
            questions = self._parse_llm_response(
                response_text, context_chunks, difficulty, topic
            )
            
            return questions
            
        except Exception as e:
            logger.error(f"Batch question generation failed: {str(e)}")
            return []
    
    def _create_question_prompt(
        self,
        context_text: str,
        subject: str,
        grade_level: int,
        topic: str,
        difficulty: str,
        count: int,
        language: str = "english"
    ) -> str:
        """Create the prompt for question generation."""
        
        difficulty_guidance = {
            "easy": "Create simple, direct questions that test basic recall and understanding. Use simple vocabulary appropriate for the grade level.",
            "medium": "Create questions that require some analysis or application of concepts. Include one-step problem solving.",
            "hard": "Create challenging questions that require analysis, synthesis, or multi-step reasoning. Test deeper understanding."
        }
        
        bloom_levels = {
            "easy": "Remember, Understand",
            "medium": "Apply, Analyze", 
            "hard": "Evaluate, Create"
        }
        
        # Validate and create language-aware prompt
        validated_language = validate_language(language)
        language_prefix = create_language_prompt_prefix(validated_language, "Educational assessment questions")
        
        prompt = f"""{language_prefix}

You are an expert educational assessment designer. Create {count} high-quality multiple-choice questions based on the provided context.

REQUIREMENTS:
- Subject: {subject}
- Grade Level: {grade_level}
- Topic: {topic}
- Difficulty: {difficulty}
- Question Type: Multiple choice with 4 options

DIFFICULTY GUIDANCE:
{difficulty_guidance.get(difficulty, difficulty_guidance["medium"])}

BLOOM'S TAXONOMY LEVEL:
Target cognitive levels: {bloom_levels.get(difficulty, bloom_levels["medium"])}

CONTEXT MATERIAL:
{context_text}

FORMATTING REQUIREMENTS:
Return EXACTLY {count} questions in JSON format as follows:

```json
[
  {{
    "question_text": "Clear, specific question based on the context",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Clear explanation of why the answer is correct",
    "bloom_level": "Remember/Understand/Apply/Analyze/Evaluate/Create",
    "learning_objectives": ["What students should learn from this question"]
  }}
]
```

QUALITY STANDARDS:
1. Questions MUST be based on the provided context
2. Use age-appropriate vocabulary for grade {grade_level}
3. Ensure one clearly correct answer
4. Make distractors plausible but clearly wrong
5. Include educational explanations
6. Avoid trick questions or ambiguous wording
7. Test important concepts, not trivial details
8. ALL content must be in the specified language

Generate {count} question(s) now:"""

        return prompt
    
    def _parse_llm_response(
        self,
        response_text: str,
        context_chunks: List[RAGResult],
        difficulty: str,
        topic: str
    ) -> List[EnhancedAssessmentQuestion]:
        """Parse the LLM response into question objects."""
        
        questions = []
        
        try:
            # Extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON array found in response")
            
            json_str = response_text[json_start:json_end]
            parsed_questions = json.loads(json_str)
            
            # Convert to EnhancedAssessmentQuestion objects
            for i, q_data in enumerate(parsed_questions):
                try:
                    question = EnhancedAssessmentQuestion(
                        question_id=f"gen_{hash(q_data['question_text'])}_{i}",
                        question_text=q_data["question_text"],
                        options=q_data["options"],
                        correct_answer=q_data["correct_answer"],
                        explanation=q_data["explanation"],
                        difficulty=difficulty,
                        topic=topic,
                        context=GeneratedQuestionContext(
                            source_chunks=[chunk.chunk.chunk_id for chunk in context_chunks],
                            confidence_score=0.85,  # Default confidence
                            generation_metadata={
                                "model": "gemini-2.5-pro",
                                "bloom_level": q_data.get("bloom_level", ""),
                                "context_sources": len(context_chunks)
                            }
                        ),
                        bloom_taxonomy_level=q_data.get("bloom_level", ""),
                        learning_objectives=q_data.get("learning_objectives", [])
                    )
                    questions.append(question)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse question {i}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}...")
        
        return questions
    
    def _convert_to_assessment_question(
        self,
        enhanced_question: EnhancedAssessmentQuestion
    ) -> AssessmentQuestion:
        """Convert enhanced question to standard assessment question."""
        
        return AssessmentQuestion(
            question_id=enhanced_question.question_id,
            question_text=enhanced_question.question_text,
            options=enhanced_question.options,
            correct_answer=enhanced_question.correct_answer,
            explanation=enhanced_question.explanation,
            difficulty=enhanced_question.difficulty,
            topic=enhanced_question.topic
        )
    
    async def validate_question_quality(
        self,
        question: EnhancedAssessmentQuestion,
        context_chunks: List[RAGResult]
    ) -> Dict[str, Any]:
        """Validate the quality of a generated question."""
        
        quality_score = 0.0
        issues = []
        
        # Check if question is based on context
        question_lower = question.question_text.lower()
        context_match = False
        
        for chunk in context_chunks:
            if any(word in chunk.chunk.content.lower() for word in question_lower.split() if len(word) > 3):
                context_match = True
                break
        
        if context_match:
            quality_score += 0.3
        else:
            issues.append("Question may not be based on provided context")
        
        # Check answer options
        if len(set(question.options)) == len(question.options):
            quality_score += 0.2
        else:
            issues.append("Duplicate answer options found")
        
        # Check correct answer index
        if 0 <= question.correct_answer < len(question.options):
            quality_score += 0.2
        else:
            issues.append("Invalid correct answer index")
        
        # Check explanation quality
        if len(question.explanation) > 10:
            quality_score += 0.15
        else:
            issues.append("Explanation too short")
        
        # Check question length (not too short or too long)
        if 10 <= len(question.question_text) <= 200:
            quality_score += 0.15
        else:
            issues.append("Question length inappropriate")
        
        return {
            "quality_score": quality_score,
            "issues": issues,
            "is_acceptable": quality_score >= 0.7 and len(issues) <= 1
        }
