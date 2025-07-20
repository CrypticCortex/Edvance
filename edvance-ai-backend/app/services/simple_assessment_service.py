# FILE: app/services/simple_assessment_service.py

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.firebase import db
from app.models.student import (
    AssessmentConfig, Assessment, AssessmentQuestion, 
    StudentAssessmentResult, LearningPath
)

logger = logging.getLogger(__name__)

class SimpleAssessmentService:
    """Simplified assessment service without AI generation for Phase 2 start."""
    
    def __init__(self):
        self.assessment_configs_collection = "assessment_configs"
        self.assessments_collection = "assessments"
        self.assessment_results_collection = "assessment_results"
        self.learning_paths_collection = "learning_paths"
    
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
        """Create a new assessment configuration."""
        
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
        
        logger.info(f"Created assessment config: {config_id}")
        return config
    
    async def get_assessment_config_by_id(
        self,
        config_id: str,
        teacher_uid: str
    ) -> Optional[AssessmentConfig]:
        """Get a single assessment config by ID and verify teacher ownership."""
        try:
            doc_ref = db.collection(self.assessment_configs_collection).document(config_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            config_data = doc.to_dict()
            if config_data.get("teacher_uid") != teacher_uid:
                return None  # Teacher doesn't own this config
                
            return AssessmentConfig(**config_data)
            
        except Exception as e:
            logger.error(f"Error getting assessment config {config_id}: {str(e)}")
            raise e
    
    async def get_teacher_assessment_configs(
        self, 
        teacher_uid: str,
        subject_filter: Optional[str] = None
    ) -> List[AssessmentConfig]:
        """Get all assessment configurations for a teacher."""
        
        try:
            # Simplified query to avoid composite index requirement
            query = (db.collection(self.assessment_configs_collection)
                    .where("teacher_uid", "==", teacher_uid))
            
            docs = query.get()
            
            configs = []
            for doc in docs:
                config_data = doc.to_dict()
                config = AssessmentConfig(**config_data)
                
                # Filter in memory to avoid index requirements
                if not config.is_active:
                    continue
                    
                if subject_filter and config.subject != subject_filter:
                    continue
                
                configs.append(config)
            
            # Sort by created_at in memory
            configs.sort(key=lambda x: x.created_at, reverse=True)
            
            return configs
            
        except Exception as e:
            logger.error(f"Failed to get assessment configs: {e}")
            return []
    
    async def create_sample_assessment(
        self, 
        config: AssessmentConfig
    ) -> Assessment:
        """Create a sample assessment with placeholder questions."""
        
        assessment_id = str(uuid.uuid4())
        
        # Create sample questions based on the configuration
        sample_questions = self._generate_sample_questions(
            config.subject, 
            config.target_grade, 
            config.topic,
            config.difficulty_level,
            config.question_count
        )
        
        assessment = Assessment(
            assessment_id=assessment_id,
            config_id=config.config_id,
            teacher_uid=config.teacher_uid,
            title=f"{config.topic} - {config.subject} Grade {config.target_grade}",
            subject=config.subject,
            grade=config.target_grade,
            difficulty=config.difficulty_level,
            topic=config.topic,
            questions=sample_questions,
            time_limit_minutes=config.time_limit_minutes
        )
        
        # Save to Firestore
        doc_ref = db.collection(self.assessments_collection).document(assessment_id)
        doc_ref.set(assessment.dict())
        
        logger.info(f"Created sample assessment: {assessment_id}")
        return assessment
    
    def _generate_sample_questions(
        self, 
        subject: str, 
        grade: int, 
        topic: str,
        difficulty: str,
        count: int
    ) -> List[AssessmentQuestion]:
        """Generate sample questions for demonstration."""
        
        questions = []
        
        # Sample question templates by subject
        print("Using Simple Question file still")
        templates = {
            "Mathematics": [
                {
                    "question": f"What is 2 + 3?",
                    "options": ["4", "5", "6", "7"],
                    "correct": 1,
                    "explanation": "2 + 3 = 5"
                },
                {
                    "question": f"What is 10 - 4?",
                    "options": ["5", "6", "7", "8"],
                    "correct": 1,
                    "explanation": "10 - 4 = 6"
                }
            ],
            "Science": [
                {
                    "question": f"What planet is closest to the Sun?",
                    "options": ["Venus", "Mercury", "Earth", "Mars"],
                    "correct": 1,
                    "explanation": "Mercury is the closest planet to the Sun"
                },
                {
                    "question": f"What gas do plants use for photosynthesis?",
                    "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
                    "correct": 2,
                    "explanation": "Plants use carbon dioxide for photosynthesis"
                }
            ],
            "English": [
                {
                    "question": f"What is a noun?",
                    "options": ["Action word", "Describing word", "Person, place, or thing", "Connecting word"],
                    "correct": 2,
                    "explanation": "A noun is a person, place, or thing"
                },
                {
                    "question": f"What is the past tense of 'run'?",
                    "options": ["Runs", "Running", "Ran", "Runned"],
                    "correct": 2,
                    "explanation": "The past tense of 'run' is 'ran'"
                }
            ]
        }
        
        # Get templates for the subject, or use generic ones
        subject_templates = templates.get(subject, templates["Mathematics"])
        
        # Generate the requested number of questions
        for i in range(min(count, len(subject_templates) * 3)):  # Repeat templates if needed
            template = subject_templates[i % len(subject_templates)]
            
            question = AssessmentQuestion(
                question_id=str(uuid.uuid4()),
                question_text=template["question"],
                options=template["options"],
                correct_answer=template["correct"],
                explanation=template["explanation"],
                difficulty=difficulty,
                topic=topic
            )
            questions.append(question)
        
        return questions[:count]  # Return exactly the requested count
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[Assessment]:
        """Get an assessment by ID."""
        
        try:
            doc_ref = db.collection(self.assessments_collection).document(assessment_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            return Assessment(**doc.to_dict())
            
        except Exception as e:
            logger.error(f"Failed to get assessment {assessment_id}: {e}")
            return None
    
    async def get_available_topics(
        self, 
        subject: str, 
        grade: int, 
        teacher_uid: str
    ) -> List[str]:
        """Get available topics based on uploaded documents (placeholder for now)."""
        
        # For now, return some sample topics based on subject and grade
        topic_templates = {
            "Mathematics": {
                "elementary": ["Addition", "Subtraction", "Multiplication", "Division", "Fractions"],
                "middle": ["Algebra", "Geometry", "Statistics", "Probability", "Equations"],
                "high": ["Calculus", "Trigonometry", "Advanced Algebra", "Statistics", "Geometry"]
            },
            "Science": {
                "elementary": ["Animals", "Plants", "Weather", "Solar System", "Matter"],
                "middle": ["Physics", "Chemistry", "Biology", "Earth Science", "Energy"],
                "high": ["Advanced Physics", "Organic Chemistry", "Biology", "Environmental Science", "Astronomy"]
            },
            "English": {
                "elementary": ["Reading", "Writing", "Grammar", "Vocabulary", "Spelling"],
                "middle": ["Literature", "Writing Skills", "Grammar", "Poetry", "Essays"],
                "high": ["Literature Analysis", "Creative Writing", "Research", "Critical Thinking", "Communication"]
            }
        }
        
        # Determine grade category
        if grade <= 5:
            category = "elementary"
        elif grade <= 8:
            category = "middle"
        else:
            category = "high"
        
        # Get topics for the subject and grade category
        subject_topics = topic_templates.get(subject, topic_templates["Mathematics"])
        topics = subject_topics.get(category, ["General Topics"])
        
        return topics

# Create singleton instance
simple_assessment_service = SimpleAssessmentService()
