# FILE: app/api/v1/student_dashboard.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.models.student import StudentProfile, Assessment
from app.core.auth import get_current_student
from app.services.student_service import student_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/profile", response_model=StudentProfile, tags=["Student Dashboard"])
async def get_my_profile(
    current_student: Dict[str, Any] = Depends(get_current_student)
) -> StudentProfile:
    """
    Get the current student's profile information.
    
    Returns:
        StudentProfile: The student's profile data
        
    Raises:
        HTTPException: If student data cannot be retrieved
    """
    try:
        # Return the student data as a profile
        return StudentProfile(
            doc_id=current_student["doc_id"],
            student_id=current_student.get("student_id", ""),
            first_name=current_student.get("first_name", ""),
            last_name=current_student.get("last_name", ""),
            grade=current_student.get("grade", 1),
            subjects=current_student.get("subjects", []),
            current_learning_paths=current_student.get("current_learning_paths", {}),
            performance_metrics=current_student.get("performance_metrics", {}),
            created_at=current_student.get("created_at"),
            last_login=current_student.get("last_login")
        )
        
    except Exception as e:
        logger.error(f"Error getting student profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving profile: {str(e)}"
        )

@router.get("/assessments", response_model=List[Assessment], tags=["Student Dashboard"])
async def get_my_assessments(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    status_filter: Optional[str] = Query(None, description="Filter by status (available, completed, in_progress)"),
    current_student: Dict[str, Any] = Depends(get_current_student)
) -> List[Assessment]:
    """
    Get assessments for the current student.
    
    Args:
        subject: Optional subject filter
        status_filter: Optional status filter
        current_student: The authenticated student
        
    Returns:
        List[Assessment]: List of assessments for the student
        
    Raises:
        HTTPException: If assessments cannot be retrieved
    """
    try:
        student_id = current_student.get("student_id")
        student_subjects = current_student.get("subjects", [])
        
        # For now, return demo assessments that match the student's subjects
        demo_assessments = [
            Assessment(
                assessment_id="math_001",
                title="Basic Algebra Assessment",
                description="Test your understanding of basic algebraic concepts",
                subject="Mathematics",
                difficulty="beginner",
                estimated_duration=30,
                total_questions=20,
                status="available",
                created_at=datetime.utcnow().isoformat(),
                topics=["algebra", "equations", "variables"]
            ),
            Assessment(
                assessment_id="sci_001", 
                title="Introduction to Physics",
                description="Fundamental physics concepts and principles",
                subject="Science",
                difficulty="intermediate",
                estimated_duration=45,
                total_questions=25,
                status="available",
                created_at=datetime.utcnow().isoformat(),
                topics=["mechanics", "forces", "motion"]
            ),
            Assessment(
                assessment_id="eng_001",
                title="Reading Comprehension",
                description="Test your reading and comprehension skills",
                subject="English",
                difficulty="beginner",
                estimated_duration=40,
                total_questions=15,
                status="completed",
                score=85,
                completed_at=datetime.utcnow().isoformat(),
                created_at=datetime.utcnow().isoformat(),
                topics=["reading", "comprehension", "analysis"]
            )
        ]
        
        # Filter by student's subjects
        filtered_assessments = [
            assessment for assessment in demo_assessments
            if assessment.subject in student_subjects or not student_subjects
        ]
        
        # Apply subject filter if provided
        if subject:
            filtered_assessments = [
                assessment for assessment in filtered_assessments
                if assessment.subject.lower() == subject.lower()
            ]
            
        # Apply status filter if provided
        if status_filter:
            filtered_assessments = [
                assessment for assessment in filtered_assessments
                if assessment.status == status_filter
            ]
        
        logger.info(f"Retrieved {len(filtered_assessments)} assessments for student {student_id}")
        return filtered_assessments
        
    except Exception as e:
        logger.error(f"Error getting student assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving assessments: {str(e)}"
        )

@router.get("/assessments/{assessment_id}", response_model=Assessment, tags=["Student Dashboard"])
async def get_my_assessment(
    assessment_id: str,
    current_student: Dict[str, Any] = Depends(get_current_student)
) -> Assessment:
    """
    Get a specific assessment for the current student.
    
    Args:
        assessment_id: The ID of the assessment
        current_student: The authenticated student
        
    Returns:
        Assessment: The requested assessment
        
    Raises:
        HTTPException: If assessment cannot be found
    """
    try:
        # For now, return a demo assessment
        demo_assessment = Assessment(
            assessment_id=assessment_id,
            title="Sample Assessment",
            description="This is a sample assessment for demonstration",
            subject="General",
            difficulty="intermediate",
            estimated_duration=30,
            total_questions=20,
            status="available",
            created_at=datetime.utcnow().isoformat(),
            topics=["general", "sample"]
        )
        
        logger.info(f"Retrieved assessment {assessment_id} for student {current_student.get('student_id')}")
        return demo_assessment
        
    except Exception as e:
        logger.error(f"Error getting assessment {assessment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving assessment: {str(e)}"
        )

@router.get("/subjects", response_model=List[str], tags=["Student Dashboard"])
async def get_my_subjects(
    current_student: Dict[str, Any] = Depends(get_current_student)
) -> List[str]:
    """
    Get available subjects for the current student.
    
    Args:
        current_student: The authenticated student
        
    Returns:
        List[str]: List of subjects
    """
    try:
        subjects = current_student.get("subjects", ["Mathematics", "Science", "English"])
        logger.info(f"Retrieved {len(subjects)} subjects for student {current_student.get('student_id')}")
        return subjects
        
    except Exception as e:
        logger.error(f"Error getting student subjects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving subjects: {str(e)}"
        )

@router.get("/progress", response_model=Dict[str, Any], tags=["Student Dashboard"])
async def get_my_progress(
    current_student: Dict[str, Any] = Depends(get_current_student)
) -> Dict[str, Any]:
    """
    Get progress data for the current student.
    
    Args:
        current_student: The authenticated student
        
    Returns:
        Dict[str, Any]: Progress data including scores, completion rates, etc.
    """
    try:
        # Return demo progress data
        progress_data = {
            "overall_progress": 75,
            "subjects": {
                "Mathematics": {
                    "progress": 80,
                    "assessments_completed": 5,
                    "average_score": 85
                },
                "Science": {
                    "progress": 70,
                    "assessments_completed": 3,
                    "average_score": 78
                },
                "English": {
                    "progress": 75,
                    "assessments_completed": 4,
                    "average_score": 82
                }
            },
            "recent_activity": [
                {
                    "type": "assessment_completed",
                    "title": "Algebra Basics",
                    "score": 85,
                    "date": datetime.utcnow().isoformat()
                }
            ]
        }
        
        logger.info(f"Retrieved progress data for student {current_student.get('student_id')}")
        return progress_data
        
    except Exception as e:
        logger.error(f"Error getting student progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving progress: {str(e)}"
        )

@router.get("/learning-paths", response_model=List[Dict[str, Any]], tags=["Student Dashboard"])
async def get_my_learning_paths(
    current_student: Dict[str, Any] = Depends(get_current_student)
) -> List[Dict[str, Any]]:
    """
    Get learning paths for the current student.
    
    Args:
        current_student: The authenticated student
        
    Returns:
        List[Dict[str, Any]]: List of learning paths
    """
    try:
        # Return demo learning paths
        learning_paths = [
            {
                "id": "path_math_001",
                "title": "Algebra Fundamentals",
                "subject": "Mathematics",
                "progress": 60,
                "total_steps": 10,
                "completed_steps": 6,
                "estimated_duration": "2 weeks",
                "difficulty": "beginner"
            },
            {
                "id": "path_sci_001",
                "title": "Physics Basics",
                "subject": "Science", 
                "progress": 40,
                "total_steps": 8,
                "completed_steps": 3,
                "estimated_duration": "3 weeks",
                "difficulty": "intermediate"
            }
        ]
        
        logger.info(f"Retrieved {len(learning_paths)} learning paths for student {current_student.get('student_id')}")
        return learning_paths
        
    except Exception as e:
        logger.error(f"Error getting student learning paths: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving learning paths: {str(e)}"
        )

@router.get("/insights", response_model=Dict[str, Any], tags=["Student Dashboard"])
async def get_my_insights(
    current_student: Dict[str, Any] = Depends(get_current_student)
) -> Dict[str, Any]:
    """
    Get personalized insights for the current student.
    
    Args:
        current_student: The authenticated student
        
    Returns:
        Dict[str, Any]: Insights and recommendations
    """
    try:
        # Return demo insights
        insights = {
            "strengths": ["Problem solving", "Logical thinking"],
            "improvement_areas": ["Reading comprehension", "Writing skills"],
            "recommendations": [
                "Focus on algebra practice for the next week",
                "Complete the reading comprehension exercises",
                "Review physics formulas before the next assessment"
            ],
            "study_streak": 5,
            "weekly_goal_progress": 80,
            "next_milestone": "Complete 3 more assessments to unlock advanced topics"
        }
        
        logger.info(f"Retrieved insights for student {current_student.get('student_id')}")
        return insights
        
    except Exception as e:
        logger.error(f"Error getting student insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving insights: {str(e)}"
        )
