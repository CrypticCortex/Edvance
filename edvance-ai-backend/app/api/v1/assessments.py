# FILE: app/api/v1/assessments.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
from typing import Dict, Any, List, Optional
import logging

from app.models.student import AssessmentConfig, Assessment
from app.core.auth import get_current_user
from app.services.assessment_service import assessment_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ====================================================================
# Assessment Configuration Endpoints
# ====================================================================

@router.post("/configs", response_model=AssessmentConfig, tags=["Assessment Configuration"])
async def create_assessment_config(
    name: str = Body(..., description="Name for the assessment configuration"),
    subject: str = Body(..., description="Subject for the assessment"),
    target_grade: int = Body(..., ge=1, le=12, description="Target grade level"),
    difficulty_level: str = Body(..., pattern="^(easy|medium|hard)$", description="Difficulty level"),
    topic: str = Body(..., description="Specific topic to assess"),
    question_count: int = Body(10, ge=5, le=20, description="Number of questions"),
    time_limit_minutes: int = Body(30, ge=10, le=120, description="Time limit in minutes"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AssessmentConfig:
    """
    Create a new assessment configuration.
    
    This configuration will be used to generate assessments with specific parameters.
    Teachers can create multiple configurations for different topics and reuse them.
    
    Args:
        name: Descriptive name for the configuration
        subject: Subject category (should match teacher's subjects)
        target_grade: Grade level for the assessment (1-12)
        difficulty_level: Difficulty (easy, medium, hard)
        topic: Specific topic to assess
        question_count: Number of MCQ questions (5-20)
        time_limit_minutes: Time limit for students (10-120 minutes)
        current_user: Authenticated teacher
        
    Returns:
        AssessmentConfig object with generated ID
        
    Raises:
        HTTPException: If creation fails
    """
    teacher_uid = current_user["uid"]
    
    try:
        logger.info(f"Creating assessment config for teacher {teacher_uid}: {subject} - {topic}")
        
        config = await assessment_service.create_assessment_config(
            teacher_uid=teacher_uid,
            name=name,
            subject=subject,
            target_grade=target_grade,
            difficulty_level=difficulty_level,
            topic=topic,
            question_count=question_count,
            time_limit_minutes=time_limit_minutes
        )
        
        logger.info(f"Created assessment config {config.config_id}")
        return config
        
    except Exception as e:
        logger.error(f"Assessment config creation failed: {str(e)}")
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
    Get all assessment configurations created by the current teacher.
    
    Args:
        subject: Optional filter by subject
        current_user: Authenticated teacher
        
    Returns:
        List of AssessmentConfig objects
    """
    teacher_uid = current_user["uid"]
    
    try:
        configs = await assessment_service.get_teacher_assessment_configs(
            teacher_uid=teacher_uid,
            subject_filter=subject
        )
        
        logger.info(f"Retrieved {len(configs)} assessment configs for teacher {teacher_uid}")
        return configs
        
    except Exception as e:
        logger.error(f"Failed to retrieve assessment configs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment configurations: {str(e)}"
        )

@router.get("/configs/{config_id}", response_model=AssessmentConfig, tags=["Assessment Configuration"])
async def get_assessment_config(
    config_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AssessmentConfig:
    """Get a specific assessment configuration."""
    teacher_uid = current_user["uid"]
    
    try:
        config = await assessment_service.get_assessment_config(config_id)
        
        # Verify ownership
        if config.teacher_uid != teacher_uid:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get assessment config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment configuration: {str(e)}"
        )

@router.put("/configs/{config_id}", response_model=AssessmentConfig, tags=["Assessment Configuration"])
async def update_assessment_config(
    config_id: str,
    name: Optional[str] = Body(None),
    subject: Optional[str] = Body(None),
    target_grade: Optional[int] = Body(None, ge=1, le=12),
    difficulty_level: Optional[str] = Body(None, pattern="^(easy|medium|hard)$"),
    topic: Optional[str] = Body(None),
    question_count: Optional[int] = Body(None, ge=5, le=20),
    time_limit_minutes: Optional[int] = Body(None, ge=10, le=120),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AssessmentConfig:
    """Update an assessment configuration."""
    teacher_uid = current_user["uid"]
    
    try:
        update_fields = {
            "name": name,
            "subject": subject,
            "target_grade": target_grade,
            "difficulty_level": difficulty_level,
            "topic": topic,
            "question_count": question_count,
            "time_limit_minutes": time_limit_minutes
        }
        
        config = await assessment_service.update_assessment_config(
            config_id=config_id,
            teacher_uid=teacher_uid,
            **update_fields
        )
        
        logger.info(f"Updated assessment config {config_id}")
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update assessment config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update assessment configuration: {str(e)}"
        )

@router.delete("/configs/{config_id}", tags=["Assessment Configuration"])
async def deactivate_assessment_config(
    config_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Deactivate an assessment configuration."""
    teacher_uid = current_user["uid"]
    
    try:
        await assessment_service.deactivate_assessment_config(config_id, teacher_uid)
        
        return {"message": f"Assessment configuration {config_id} deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate assessment config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate assessment configuration: {str(e)}"
        )

# ====================================================================
# Assessment Generation Endpoints
# ====================================================================

@router.post("/generate/{config_id}", response_model=Assessment, tags=["Assessment Generation"])
async def generate_assessment(
    config_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Assessment:
    """
    Generate a new MCQ assessment from a configuration.
    
    This will use AI to create questions based on:
    - Uploaded documents (RAG system)
    - Configuration parameters (difficulty, grade, topic)
    - Subject-specific knowledge
    
    Args:
        config_id: ID of the assessment configuration to use
        current_user: Authenticated teacher
        
    Returns:
        Assessment object with generated questions
        
    Raises:
        HTTPException: If generation fails or config not found
    """
    teacher_uid = current_user["uid"]
    
    try:
        logger.info(f"Generating assessment from config {config_id} for teacher {teacher_uid}")
        
        assessment = await assessment_service.generate_assessment_from_config(
            config_id=config_id,
            teacher_uid=teacher_uid
        )
        
        logger.info(f"Generated assessment {assessment.assessment_id} with {len(assessment.questions)} questions")
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assessment generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate assessment: {str(e)}"
        )

@router.get("/", response_model=List[Assessment], tags=["Assessment Management"])
async def get_my_assessments(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Assessment]:
    """
    Get all assessments created by the current teacher.
    
    Args:
        subject: Optional filter by subject
        current_user: Authenticated teacher
        
    Returns:
        List of Assessment objects
    """
    teacher_uid = current_user["uid"]
    
    try:
        assessments = await assessment_service.get_teacher_assessments(
            teacher_uid=teacher_uid,
            subject_filter=subject
        )
        
        logger.info(f"Retrieved {len(assessments)} assessments for teacher {teacher_uid}")
        return assessments
        
    except Exception as e:
        logger.error(f"Failed to retrieve assessments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessments: {str(e)}"
        )

@router.get("/{assessment_id}", response_model=Assessment, tags=["Assessment Management"])
async def get_assessment(
    assessment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Assessment:
    """Get a specific assessment with all questions."""
    teacher_uid = current_user["uid"]
    
    try:
        assessment = await assessment_service.get_assessment(assessment_id)
        
        # Verify ownership
        if assessment.teacher_uid != teacher_uid:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment: {str(e)}"
        )

@router.delete("/{assessment_id}", tags=["Assessment Management"])
async def deactivate_assessment(
    assessment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Deactivate an assessment (soft delete)."""
    teacher_uid = current_user["uid"]
    
    try:
        await assessment_service.deactivate_assessment(assessment_id, teacher_uid)
        
        return {"message": f"Assessment {assessment_id} deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate assessment: {str(e)}"
        )

# ====================================================================
# Helper Endpoints
# ====================================================================

@router.get("/topics/{subject}/{grade}", response_model=List[str], tags=["Assessment Helpers"])
async def get_available_topics(
    subject: str,
    grade: int = Path(..., ge=1, le=12, description="Grade level"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[str]:
    """
    Get available topics for a subject and grade based on uploaded documents.
    
    Args:
        subject: Subject name
        grade: Grade level (1-12)
        current_user: Authenticated teacher
        
    Returns:
        List of available topic names
    """
    teacher_uid = current_user["uid"]
    
    try:
        topics = await assessment_service.get_available_topics_for_subject(
            teacher_uid=teacher_uid,
            subject=subject,
            grade_level=grade
        )
        
        return topics
        
    except Exception as e:
        logger.error(f"Failed to get available topics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve topics: {str(e)}"
        )
