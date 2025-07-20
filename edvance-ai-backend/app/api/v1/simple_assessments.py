# FILE: app/api/v1/simple_assessments.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
from typing import Dict, Any, List, Optional
import logging

from app.models.student import AssessmentConfig, Assessment
from app.core.auth import get_current_user
from app.services.enhanced_assessment_service import enhanced_assessment_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ====================================================================
# Assessment Configuration Endpoints
# ====================================================================

@router.post("/configs", response_model=AssessmentConfig, tags=["Assessment Configuration"])
async def create_assessment_config(
    config_data: Dict[str, Any] = Body(..., description="Assessment configuration data"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AssessmentConfig:
    """
    Create a new assessment configuration.
    
    Args:
        config_data: Assessment configuration including name, subject, grade, difficulty, topic
        current_user: Authenticated teacher
        
    Returns:
        Created AssessmentConfig
    """
    teacher_uid = current_user["uid"]
    
    try:
        # Validate required fields
        required_fields = ["name", "subject", "target_grade", "difficulty_level", "topic"]
        for field in required_fields:
            if field not in config_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Validate difficulty level
        if config_data["difficulty_level"] not in ["easy", "medium", "hard"]:
            raise HTTPException(
                status_code=400,
                detail="Difficulty level must be 'easy', 'medium', or 'hard'"
            )
        
        # Validate grade
        if not (1 <= config_data["target_grade"] <= 12):
            raise HTTPException(
                status_code=400,
                detail="Target grade must be between 1 and 12"
            )
        
        config = await enhanced_assessment_service.create_assessment_config(
            name=config_data["name"],
            subject=config_data["subject"],
            target_grade=config_data["target_grade"],
            difficulty_level=config_data["difficulty_level"],
            topic=config_data["topic"],
            teacher_uid=teacher_uid,
            question_count=config_data.get("question_count", 10),
            time_limit_minutes=config_data.get("time_limit_minutes", 30)
        )
        
        logger.info(f"Created assessment config {config.config_id} for teacher {teacher_uid}")
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create assessment config for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment configuration: {str(e)}"
        )

@router.get("/configs", response_model=List[AssessmentConfig], tags=["Assessment Configuration"])
async def get_my_assessment_configs(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[AssessmentConfig]:
    """
    Get all assessment configurations for the current teacher.
    
    Args:
        subject: Optional subject filter
        current_user: Authenticated teacher
        
    Returns:
        List of AssessmentConfig objects
    """
    teacher_uid = current_user["uid"]
    
    try:
        configs = await enhanced_assessment_service.get_teacher_assessment_configs(
            teacher_uid=teacher_uid,
            subject_filter=subject
        )
        
        logger.info(f"Retrieved {len(configs)} assessment configs for teacher {teacher_uid}")
        return configs
        
    except Exception as e:
        logger.error(f"Failed to get assessment configs for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment configurations: {str(e)}"
        )

# ====================================================================
# Assessment Generation Endpoints
# ====================================================================

@router.post("/configs/{config_id}/generate", response_model=Assessment, tags=["Assessment Generation"])
async def generate_assessment_from_config(
    config_id: str = Path(..., description="Assessment configuration ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Assessment:
    """
    Generate a sample assessment from a configuration.
    
    Args:
        config_id: The assessment configuration ID
        current_user: Authenticated teacher
        
    Returns:
        Generated Assessment with sample questions
    """
    teacher_uid = current_user["uid"]
    
    try:
        # Get the configuration by ID directly
        config = await enhanced_assessment_service.get_assessment_config_by_id(
            config_id=config_id,
            teacher_uid=teacher_uid
        )
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="Assessment configuration not found"
            )
        
        # Generate the assessment using RAG and AI
        assessment = await enhanced_assessment_service.create_rag_assessment(config)
        
        logger.info(f"Generated assessment {assessment.assessment_id} from config {config_id}")
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate assessment from config {config_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate assessment: {str(e)}"
        )

@router.get("/assessments/{assessment_id}", response_model=Assessment, tags=["Assessment Management"])
async def get_assessment(
    assessment_id: str = Path(..., description="Assessment ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Assessment:
    """
    Get a specific assessment by ID.
    
    Args:
        assessment_id: The assessment ID
        current_user: Authenticated teacher
        
    Returns:
        Assessment object
    """
    teacher_uid = current_user["uid"]
    
    try:
        assessment = await enhanced_assessment_service.get_assessment_by_id(assessment_id)
        
        if not assessment:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )
        
        # Verify the assessment belongs to this teacher
        if assessment.teacher_uid != teacher_uid:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Assessment does not belong to this teacher"
            )
        
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get assessment {assessment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment: {str(e)}"
        )

# ====================================================================
# Helper Endpoints
# ====================================================================

@router.get("/topics/{subject}/{grade}", response_model=List[str], tags=["Assessment Helpers"])
async def get_available_topics(
    subject: str = Path(..., description="Subject name"),
    grade: int = Path(..., ge=1, le=12, description="Grade level"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[str]:
    """
    Get available topics for a subject and grade.
    
    Args:
        subject: Subject name
        grade: Grade level (1-12)
        current_user: Authenticated teacher
        
    Returns:
        List of available topic names
    """
    teacher_uid = current_user["uid"]
    
    try:
        topics = await enhanced_assessment_service.get_available_topics(
            subject=subject,
            grade=grade,
            teacher_uid=teacher_uid
        )
        
        return topics
        
    except Exception as e:
        logger.error(f"Failed to get topics for {subject} grade {grade}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available topics: {str(e)}"
        )

@router.get("/summary", tags=["Assessment Management"])
async def get_assessment_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get summary of teacher's assessments and configurations.
    
    Args:
        current_user: Authenticated teacher
        
    Returns:
        Summary statistics
    """
    teacher_uid = current_user["uid"]
    
    try:
        configs = await enhanced_assessment_service.get_teacher_assessment_configs(teacher_uid)
        
        # Calculate statistics
        total_configs = len(configs)
        subjects = list(set(config.subject for config in configs))
        difficulty_distribution = {}
        
        for config in configs:
            difficulty = config.difficulty_level
            difficulty_distribution[difficulty] = difficulty_distribution.get(difficulty, 0) + 1
        
        return {
            "total_configurations": total_configs,
            "unique_subjects": subjects,
            "difficulty_distribution": difficulty_distribution,
            "recent_configs": [
                {
                    "config_id": config.config_id,
                    "name": config.name,
                    "subject": config.subject,
                    "grade": config.target_grade,
                    "created_at": config.created_at
                }
                for config in configs[:5]  # Most recent 5
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get assessment summary for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessment summary: {str(e)}"
        )
