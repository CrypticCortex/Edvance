# FILE: app/services/enhanced_assessment_service.py

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.services.rag_service import RAGService
from app.agents.vertex_question_agent import VertexQuestionAgent
from app.services.simple_assessment_service import SimpleAssessmentService
from app.models.student import AssessmentConfig, Assessment, AssessmentQuestion
from app.models.rag_models import QuestionGenerationRequest
from app.core.firebase import db

logger = logging.getLogger(__name__)

class EnhancedAssessmentService:
    """Enhanced assessment service with RAG and AI question generation."""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.question_agent = VertexQuestionAgent()
        self.simple_service = SimpleAssessmentService()  # Fallback for non-RAG operations
        self.assessments_collection = "assessments"
    
    async def create_rag_assessment(
        self, 
        config: AssessmentConfig,
        force_rag: bool = True
    ) -> Assessment:
        """Create an assessment using RAG and AI generation."""
        
        try:
            logger.info(f"Creating RAG assessment for config {config.config_id}")
            
            # Step 1: Retrieve relevant context using RAG
            rag_results = await self.rag_service.retrieve_context_for_assessment(
                subject=config.subject,
                grade_level=config.target_grade,
                topic=config.topic,
                teacher_uid=config.teacher_uid,
                max_chunks=5
            )
            
            # Step 2: Generate questions using AI agent (with or without RAG context)
            generation_request = QuestionGenerationRequest(
                context_chunks=rag_results if rag_results else [],  # Empty list if no context
                subject=config.subject,
                grade_level=config.target_grade,
                topic=config.topic,
                difficulty_level=config.difficulty_level,
                question_count=config.question_count,
                question_type="multiple_choice"
            )
            
            # Use AI generation even without RAG context
            if rag_results and len(rag_results) >= 2:
                logger.info(f"Using RAG-enhanced AI generation with {len(rag_results)} context chunks")
            else:
                logger.info(f"Using AI generation without RAG context for {config.topic}")
            
            enhanced_questions = await self.question_agent.generate_questions(generation_request)
            
            # Step 3: Convert to standard AssessmentQuestion format
            assessment_questions = []
            for enhanced_q in enhanced_questions:
                standard_q = AssessmentQuestion(
                    question_id=enhanced_q.question_id,
                    question_text=enhanced_q.question_text,
                    options=enhanced_q.options,
                    correct_answer=enhanced_q.correct_answer,
                    explanation=enhanced_q.explanation,
                    difficulty=enhanced_q.difficulty,
                    topic=enhanced_q.topic
                )
                assessment_questions.append(standard_q)
            
            # Step 4: Fill remaining questions with simple generation if needed
            if len(assessment_questions) < config.question_count:
                logger.info(f"Generated {len(assessment_questions)}/{config.question_count} questions, filling remainder with simple generation")
                
                remaining_count = config.question_count - len(assessment_questions)
                simple_questions = await self._generate_simple_questions(
                    config, remaining_count, len(assessment_questions)
                )
                assessment_questions.extend(simple_questions)
            
            # Step 6: Create Assessment object
            assessment_id = str(uuid.uuid4())
            assessment = Assessment(
                assessment_id=assessment_id,
                config_id=config.config_id,
                teacher_uid=config.teacher_uid,  # Add missing teacher_uid
                title=f"{config.topic} - {config.subject} Grade {config.target_grade}",
                subject=config.subject,
                grade=config.target_grade,
                difficulty=config.difficulty_level,
                topic=config.topic,
                questions=assessment_questions[:config.question_count],  # Ensure exact count
                time_limit_minutes=config.time_limit_minutes
            )
            
            # Step 7: Save to Firestore with RAG metadata
            await self._save_rag_assessment(assessment, rag_results, enhanced_questions)
            
            logger.info(f"Created RAG assessment: {assessment_id} with {len(assessment.questions)} questions")
            return assessment
            
        except Exception as e:
            logger.error(f"RAG assessment creation failed: {str(e)}")
            # Fallback to simple assessment
            logger.info("Falling back to simple assessment generation due to error")
            return await self.simple_service.create_sample_assessment(config)
    
    async def _generate_simple_questions(
        self,
        config: AssessmentConfig,
        count: int,
        start_index: int = 0
    ) -> List[AssessmentQuestion]:
        """Generate simple questions when RAG doesn't provide enough."""
        
        # Use the simple service's question generation
        simple_questions = await self.simple_service._generate_sample_questions(
            subject=config.subject,
            grade=config.target_grade,
            topic=config.topic,
            difficulty=config.difficulty_level,
            count=count
        )
        
        # Update question IDs to avoid conflicts
        for i, question in enumerate(simple_questions):
            question.question_id = f"simple_{start_index + i}_{question.question_id}"
        
        return simple_questions
    
    async def _save_rag_assessment(
        self,
        assessment: Assessment,
        rag_results: List,
        enhanced_questions: List
    ) -> None:
        """Save assessment with RAG metadata."""
        
        try:
            # Prepare assessment data
            assessment_data = assessment.dict()
            
            # Add RAG metadata
            assessment_data["generation_method"] = "rag_enhanced"
            assessment_data["rag_metadata"] = {
                "context_chunks_used": len(rag_results),
                "ai_generated_questions": len(enhanced_questions),
                "context_sources": [
                    {
                        "chunk_id": result.chunk.chunk_id,
                        "document_id": result.chunk.document_id,
                        "similarity_score": result.similarity_score,
                        "source_file": result.document_metadata.get("filename", "Unknown")
                    }
                    for result in rag_results
                ],
                "generation_timestamp": datetime.utcnow().isoformat()
            }
            
            # Save to Firestore
            doc_ref = db.collection(self.assessments_collection).document(assessment.assessment_id)
            doc_ref.set(assessment_data)
            
            logger.info(f"Saved RAG assessment with metadata: {assessment.assessment_id}")
            
        except Exception as e:
            logger.error(f"Failed to save RAG assessment: {str(e)}")
            raise e
    
    async def get_assessment_with_metadata(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment with RAG metadata."""
        
        try:
            doc_ref = db.collection(self.assessments_collection).document(assessment_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get assessment with metadata {assessment_id}: {str(e)}")
            return None
    
    async def get_teacher_rag_statistics(self, teacher_uid: str) -> Dict[str, Any]:
        """Get RAG usage statistics for a teacher."""
        
        try:
            # Get teacher's assessments
            assessments_ref = db.collection(self.assessments_collection)
            # Note: This would require getting configs first to find teacher's assessments
            # For now, return basic stats
            
            content_stats = await self.rag_service.get_teacher_content_stats(teacher_uid)
            
            return {
                "content_statistics": content_stats,
                "rag_enabled": True,
                "total_documents": content_stats.get("total_documents", 0),
                "total_chunks": content_stats.get("total_chunks", 0),
                "subjects_covered": content_stats.get("subjects", []),
                "grade_levels_covered": content_stats.get("grade_levels", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get RAG statistics for {teacher_uid}: {str(e)}")
            return {
                "content_statistics": {},
                "rag_enabled": False,
                "error": str(e)
            }
    
    async def search_teacher_content(
        self,
        teacher_uid: str,
        search_query: str,
        subject_filter: Optional[str] = None,
        grade_filter: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search teacher's uploaded content."""
        
        try:
            results = await self.rag_service.search_documents_by_content(
                search_text=search_query,
                teacher_uid=teacher_uid,
                subject_filter=subject_filter,
                grade_filter=grade_filter,
                max_results=10
            )
            
            context_summary = await self.rag_service.get_context_summary(results)
            
            return {
                "search_query": search_query,
                "results_found": len(results),
                "summary": context_summary,
                "results": [
                    {
                        "chunk_id": r.chunk.chunk_id,
                        "content_preview": r.chunk.content[:200] + "..." if len(r.chunk.content) > 200 else r.chunk.content,
                        "similarity_score": round(r.similarity_score, 3),
                        "source_document": r.document_metadata.get("filename", "Unknown"),
                        "subject": r.chunk.metadata.get("subject", ""),
                        "grade_level": r.chunk.metadata.get("grade_level", 0)
                    }
                    for r in results
                ]
            }
            
        except Exception as e:
            logger.error(f"Content search failed for {teacher_uid}: {str(e)}")
            return {
                "search_query": search_query,
                "results_found": 0,
                "error": str(e),
                "results": []
            }
    
    # Delegate methods to simple service for backwards compatibility
    async def create_assessment_config(
        self, 
        name: str,
        subject: str,
        target_grade: int,
        difficulty_level: str,
        topic: str,
        teacher_uid: str,
        question_count: int = 10,
        time_limit_minutes: int = 30
    ) -> AssessmentConfig:
        """Create assessment config (delegates to simple service)."""
        return await self.simple_service.create_assessment_config(
            name=name,
            subject=subject,
            target_grade=target_grade,
            difficulty_level=difficulty_level,
            topic=topic,
            teacher_uid=teacher_uid,
            question_count=question_count,
            time_limit_minutes=time_limit_minutes
        )
    
    async def get_teacher_assessment_configs(
        self, 
        teacher_uid: str,
        subject_filter: Optional[str] = None
    ) -> List[AssessmentConfig]:
        """Get teacher assessment configs (delegates to simple service)."""
        return await self.simple_service.get_teacher_assessment_configs(
            teacher_uid=teacher_uid,
            subject_filter=subject_filter
        )
    
    async def get_assessment_config_by_id(
        self,
        config_id: str,
        teacher_uid: str
    ) -> Optional[AssessmentConfig]:
        """Get assessment config by ID (delegates to simple service)."""
        return await self.simple_service.get_assessment_config_by_id(
            config_id=config_id,
            teacher_uid=teacher_uid
        )
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[Assessment]:
        """Get assessment by ID."""
        try:
            doc_ref = db.collection(self.assessments_collection).document(assessment_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                # Remove RAG metadata for standard response
                if "rag_metadata" in data:
                    del data["rag_metadata"]
                if "generation_method" in data:
                    del data["generation_method"]
                    
                return Assessment(**data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get assessment {assessment_id}: {str(e)}")
            return None

    async def get_available_topics(
        self, 
        subject: str, 
        grade: int, 
        teacher_uid: str
    ) -> List[str]:
        """Delegate to simple service for topics."""
        return await self.simple_service.get_available_topics(
            subject=subject,
            grade=grade,
            teacher_uid=teacher_uid
        )

# Global instance
enhanced_assessment_service = EnhancedAssessmentService()
