# FILE: app/services/assessment_service.py

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import HTTPException
from app.core.firebase import db
from app.models.student import (
    AssessmentConfig, Assessment, AssessmentQuestion, 
    StudentAssessmentResult, LearningPath
)
from app.services.vertex_rag_service import vertex_rag_service
# Import assessment agent when needed to avoid initialization issues

logger = logging.getLogger(__name__)

class AssessmentService:
    """Service for managing assessment configurations and generation."""
    
    def __init__(self):
        self.assessment_configs_collection = "assessment_configs"
        self.assessments_collection = "assessments"
        self.assessment_results_collection = "assessment_results"
        
    async def create_assessment_config(
        self,
        teacher_uid: str,
        name: str,
        subject: str,
        target_grade: int,
        difficulty_level: str,
        topic: str,
        question_count: int = 10,
        time_limit_minutes: int = 30
    ) -> AssessmentConfig:
        """
        Create a new assessment configuration.
        
        Args:
            teacher_uid: UID of the teacher creating the config
            name: Name for the assessment configuration
            subject: Subject for the assessment
            target_grade: Target grade level (1-12)
            difficulty_level: Difficulty level (easy, medium, hard)
            topic: Specific topic to assess
            question_count: Number of questions (5-20)
            time_limit_minutes: Time limit in minutes (10-120)
            
        Returns:
            AssessmentConfig object
        """
        try:
            config_id = str(uuid.uuid4())
            
            config = AssessmentConfig(
                config_id=config_id,
                teacher_uid=teacher_uid,
                name=name,
                subject=subject,
                target_grade=target_grade,
                difficulty_level=difficulty_level,
                topic=topic,
                question_count=question_count,
                time_limit_minutes=time_limit_minutes
            )
            
            # Save to Firestore
            doc_ref = db.collection(self.assessment_configs_collection).document(config_id)
            doc_ref.set(config.dict())
            
            logger.info(f"Created assessment config {config_id} for teacher {teacher_uid}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to create assessment config: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create assessment configuration: {str(e)}"
            )
    
    async def get_teacher_assessment_configs(
        self,
        teacher_uid: str,
        subject_filter: Optional[str] = None
    ) -> List[AssessmentConfig]:
        """Get all assessment configurations for a teacher."""
        try:
            query = db.collection(self.assessment_configs_collection).where("teacher_uid", "==", teacher_uid)
            
            if subject_filter:
                query = query.where("subject", "==", subject_filter)
            
            docs = query.where("is_active", "==", True).order_by("created_at", direction="DESCENDING").get()
            
            configs = []
            for doc in docs:
                config_data = doc.to_dict()
                configs.append(AssessmentConfig(**config_data))
            
            return configs
            
        except Exception as e:
            logger.error(f"Failed to get assessment configs: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve assessment configurations: {str(e)}"
            )
    
    async def get_assessment_config(self, config_id: str) -> AssessmentConfig:
        """Get a specific assessment configuration."""
        try:
            doc_ref = db.collection(self.assessment_configs_collection).document(config_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Assessment configuration not found")
            
            return AssessmentConfig(**doc.to_dict())
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get assessment config: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve assessment configuration: {str(e)}"
            )
    
    async def update_assessment_config(
        self,
        config_id: str,
        teacher_uid: str,
        **update_fields
    ) -> AssessmentConfig:
        """Update an assessment configuration."""
        try:
            # Verify ownership
            config = await self.get_assessment_config(config_id)
            if config.teacher_uid != teacher_uid:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Update fields
            update_data = {k: v for k, v in update_fields.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            
            doc_ref = db.collection(self.assessment_configs_collection).document(config_id)
            doc_ref.update(update_data)
            
            # Return updated config
            return await self.get_assessment_config(config_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update assessment config: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update assessment configuration: {str(e)}"
            )
    
    async def deactivate_assessment_config(self, config_id: str, teacher_uid: str) -> None:
        """Deactivate an assessment configuration."""
        try:
            # Verify ownership
            config = await self.get_assessment_config(config_id)
            if config.teacher_uid != teacher_uid:
                raise HTTPException(status_code=403, detail="Access denied")
            
            doc_ref = db.collection(self.assessment_configs_collection).document(config_id)
            doc_ref.update({
                "is_active": False,
                "updated_at": datetime.utcnow()
            })
            
            logger.info(f"Deactivated assessment config {config_id}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to deactivate assessment config: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to deactivate assessment configuration: {str(e)}"
            )
    
    async def get_available_topics_for_subject(
        self,
        teacher_uid: str,
        subject: str,
        grade_level: int
    ) -> List[str]:
        """
        Get available topics from uploaded documents for a subject and grade.
        This will query the RAG system to find what topics are available.
        """
        try:
            # Query documents collection to find available topics
            query = (db.collection("documents")
                    .where("teacher_uid", "==", teacher_uid)
                    .where("subject", "==", subject)
                    .where("grade_level", "==", grade_level)
                    .where("indexing_status", "==", "completed"))
            
            docs = query.get()
            
            # For now, we'll extract topics from filenames and content
            # Later, this could use AI to analyze document content for topics
            topics = set()
            
            for doc in docs:
                doc_data = doc.to_dict()
                filename = doc_data.get("filename", "")
                
                # Extract potential topics from filename
                # Remove file extension and split by common delimiters
                topic_parts = filename.replace(".pdf", "").replace(".txt", "").replace(".doc", "")
                topic_parts = topic_parts.replace("_", " ").replace("-", " ")
                
                # Add as potential topic
                if len(topic_parts.strip()) > 0:
                    topics.add(topic_parts.strip().title())
            
            # Add some common topics if none found
            if not topics:
                default_topics = {
                    "Mathematics": ["Addition", "Subtraction", "Multiplication", "Division", "Fractions", "Geometry"],
                    "Science": ["Plants", "Animals", "Weather", "Space", "Matter", "Energy"],
                    "English": ["Reading Comprehension", "Grammar", "Vocabulary", "Writing", "Literature"],
                    "History": ["Ancient Civilizations", "World Wars", "American History", "Geography"],
                    "Geography": ["Countries", "Continents", "Climate", "Natural Resources"]
                }
                
                if subject in default_topics:
                    topics.update(default_topics[subject])
            
            return sorted(list(topics))
            
        except Exception as e:
            logger.error(f"Failed to get available topics: {e}")
            # Return empty list on error rather than failing
            return []
    
    async def generate_assessment_from_config(
        self,
        config_id: str,
        teacher_uid: str,
        language: str = "english"
    ) -> Assessment:
        """
        Generate a new assessment from a configuration.
        
        Args:
            config_id: ID of the assessment configuration
            teacher_uid: UID of the teacher requesting generation
            
        Returns:
            Assessment object with generated questions
        """
        try:
            # Get the configuration
            config = await self.get_assessment_config(config_id)
            
            # Verify ownership
            if config.teacher_uid != teacher_uid:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Import agent when needed to avoid initialization issues
            from app.agents.assessment_generation.agent import assessment_generation_agent
            
            # Generate assessment using AI agent
            assessment = await assessment_generation_agent.generate_assessment(
                config=config,
                teacher_uid=teacher_uid,
                language=language
            )
            
            # Save assessment to database
            await self._save_assessment(assessment)
            
            logger.info(f"Generated and saved assessment {assessment.assessment_id}")
            return assessment
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to generate assessment: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate assessment: {str(e)}"
            )
    
    async def _save_assessment(self, assessment: Assessment) -> None:
        """Save assessment to Firestore."""
        try:
            doc_ref = db.collection(self.assessments_collection).document(assessment.assessment_id)
            doc_ref.set(assessment.dict())
            
        except Exception as e:
            logger.error(f"Failed to save assessment: {e}")
            raise
    
    async def get_teacher_assessments(
        self,
        teacher_uid: str,
        subject_filter: Optional[str] = None,
        active_only: bool = True
    ) -> List[Assessment]:
        """Get all assessments created by a teacher."""
        try:
            query = db.collection(self.assessments_collection).where("teacher_uid", "==", teacher_uid)
            
            if subject_filter:
                query = query.where("subject", "==", subject_filter)
            
            if active_only:
                query = query.where("is_active", "==", True)
            
            docs = query.order_by("created_at", direction="DESCENDING").get()
            
            assessments = []
            for doc in docs:
                assessment_data = doc.to_dict()
                assessments.append(Assessment(**assessment_data))
            
            return assessments
            
        except Exception as e:
            logger.error(f"Failed to get teacher assessments: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve assessments: {str(e)}"
            )
    
    async def get_assessment(self, assessment_id: str) -> Assessment:
        """Get a specific assessment by ID."""
        try:
            doc_ref = db.collection(self.assessments_collection).document(assessment_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Assessment not found")
            
            return Assessment(**doc.to_dict())
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get assessment: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve assessment: {str(e)}"
            )
    
    async def deactivate_assessment(self, assessment_id: str, teacher_uid: str) -> None:
        """Deactivate an assessment."""
        try:
            # Verify ownership
            assessment = await self.get_assessment(assessment_id)
            if assessment.teacher_uid != teacher_uid:
                raise HTTPException(status_code=403, detail="Access denied")
            
            doc_ref = db.collection(self.assessments_collection).document(assessment_id)
            doc_ref.update({
                "is_active": False,
                "updated_at": datetime.utcnow()
            })
            
            logger.info(f"Deactivated assessment {assessment_id}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to deactivate assessment: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to deactivate assessment: {str(e)}"
            )

# Create singleton instance
assessment_service = AssessmentService()
