# FILE: app/agents/vertex_question_agent.py

import logging
from typing import List, Dict, Any, Optional
import json
import asyncio
import uuid

from vertexai.generative_models import GenerativeModel
from app.core.vertex import get_vertex_model
from app.models.rag_models import (
    RAGResult, 
    QuestionGenerationRequest, 
    EnhancedAssessmentQuestion,
    GeneratedQuestionContext
)

logger = logging.getLogger(__name__)

class VertexQuestionAgent:
    """AI Agent for generating assessment questions using Vertex AI Gemini."""
    
    def __init__(self):
        self.model_name = "gemini-2.5-pro"
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Vertex AI Gemini model."""
        try:
            self.model = get_vertex_model(self.model_name)
            logger.info(f"Initialized Vertex AI question agent with {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI model: {str(e)}")
            self.model = None
    
    async def generate_questions(
        self,
        request: QuestionGenerationRequest
    ) -> List[EnhancedAssessmentQuestion]:
        """Generate assessment questions from RAG context using Gemini."""
        
        if not self.model:
            logger.error("Vertex AI model not initialized, cannot generate questions")
            return []
        
        try:
            logger.info(f"Generating {request.question_count} questions for {request.subject} grade {request.grade_level}")
            
            # Prepare context from RAG results
            context_text = self._prepare_context(request.context_chunks)
            
            # Generate questions in batches
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
                    context_chunks=request.context_chunks
                )
                
                all_questions.extend(batch_questions)
                
                # Small delay between batches
                if i + batch_size < request.question_count:
                    await asyncio.sleep(1)
            
            logger.info(f"Generated {len(all_questions)} questions successfully")
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
            similarity = result.similarity_score
            
            context_part = f"""
Context {i} (from {source}, similarity: {similarity:.2f}):
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
        context_chunks: List[RAGResult]
    ) -> List[EnhancedAssessmentQuestion]:
        """Generate a batch of questions using Gemini."""
        
        try:
            # Create the prompt
            prompt = self._create_question_prompt(
                context_text, subject, grade_level, topic, difficulty, count
            )
            
            # Generate response using Vertex AI Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse the response
            questions = self._parse_gemini_response(
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
        count: int
    ) -> str:
        """Create the prompt for Gemini question generation."""
        
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
        
        # Check if we have meaningful context
        has_context = context_text and context_text != "No specific context available."
        
        if has_context:
            context_instruction = f"""CONTEXT MATERIAL (USE THIS AS YOUR SOURCE):
{context_text}

CRITICAL REQUIREMENTS:
1. Questions MUST be based on the provided context material
2. Reference specific concepts, examples, or information from the context
3. Use age-appropriate vocabulary for grade {grade_level}
4. Ensure one clearly correct answer
5. Make distractors plausible but clearly wrong based on the context
6. Include educational explanations that reference the source material"""
        else:
            context_instruction = f"""CONTENT GENERATION:
Since no specific context material is provided, generate questions based on standard curriculum content for {subject} at grade {grade_level} level, focusing on the topic: {topic}.

CRITICAL REQUIREMENTS:
1. Questions should align with standard curriculum for {subject} grade {grade_level}
2. Focus specifically on the topic: {topic}
3. Use age-appropriate vocabulary for grade {grade_level}
4. Ensure one clearly correct answer
5. Make distractors plausible but clearly wrong
6. Include educational explanations that help students learn"""
        
        prompt = f"""You are an expert educational assessment designer. Create {count} high-quality multiple-choice questions.

REQUIREMENTS:
- Subject: {subject}
- Grade Level: {grade_level}
- Topic: {topic}
- Difficulty: {difficulty}
- Question Type: Multiple choice with 4 options

DIFFICULTY GUIDANCE:
{difficulty_guidance.get(difficulty, difficulty_guidance["medium"])}

BLOOM'S TAXONOMY TARGET:
{bloom_levels.get(difficulty, bloom_levels["medium"])}

{context_instruction}

OUTPUT FORMAT:
Return EXACTLY {count} questions in this JSON format:

```json
[
  {{
    "question_text": "Educational question appropriate for the specified grade and topic",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Clear explanation that helps students understand the concept",
    "bloom_level": "Remember/Understand/Apply/Analyze/Evaluate/Create",
    "learning_objectives": ["What students learn from this question"],
    "context_reference": "Source reference or curriculum standard if applicable"
  }}
]
```

Generate {count} high-quality educational question(s) now:"""

        return prompt
    
    def _parse_gemini_response(
        self,
        response_text: str,
        context_chunks: List[RAGResult],
        difficulty: str,
        topic: str
    ) -> List[EnhancedAssessmentQuestion]:
        """Parse the Gemini response into question objects."""
        
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
                        question_id=f"vertex_{uuid.uuid4()}_{i}",
                        question_text=q_data["question_text"],
                        options=q_data["options"],
                        correct_answer=q_data["correct_answer"],
                        explanation=q_data["explanation"],
                        difficulty=difficulty,
                        topic=topic,
                        context=GeneratedQuestionContext(
                            source_chunks=[chunk.chunk.chunk_id for chunk in context_chunks],
                            confidence_score=0.90,  # High confidence for Vertex AI
                            generation_metadata={
                                "model": self.model_name,
                                "method": "vertex_ai_rag",
                                "context_sources": len(context_chunks),
                                "context_reference": q_data.get("context_reference", "")
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
            logger.error(f"Failed to parse Gemini response: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}...")
        
        return questions
    
    async def validate_question_quality(
        self,
        question: EnhancedAssessmentQuestion,
        context_chunks: List[RAGResult]
    ) -> Dict[str, Any]:
        """Validate the quality of a generated question."""
        
        quality_score = 0.0
        issues = []
        
        # Check if question references context
        question_lower = question.question_text.lower()
        context_match = False
        
        for chunk in context_chunks:
            chunk_words = set(chunk.chunk.content.lower().split())
            question_words = set(question_lower.split())
            
            # Check for word overlap
            overlap = len(chunk_words.intersection(question_words))
            if overlap >= 3:  # At least 3 words in common
                context_match = True
                break
        
        if context_match:
            quality_score += 0.4
        else:
            issues.append("Question may not be sufficiently based on provided context")
        
        # Check answer options uniqueness
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
        if len(question.explanation) > 20:
            quality_score += 0.2
        else:
            issues.append("Explanation too short")
        
        return {
            "quality_score": quality_score,
            "issues": issues,
            "is_acceptable": quality_score >= 0.8 and len(issues) <= 1,
            "context_based": context_match
        }
