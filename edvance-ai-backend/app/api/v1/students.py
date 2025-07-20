# FILE: app/api/v1/students.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from typing import Dict, Any, List, Optional
import logging

from app.models.student import StudentProfile, StudentBatchUploadResponse
from app.core.auth import get_current_user
from app.services.student_service import student_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload-csv", response_model=StudentBatchUploadResponse, tags=["Student Management"])
async def upload_students_csv(
    file: UploadFile = File(..., description="CSV file with student data"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StudentBatchUploadResponse:
    """
    Upload students from CSV file.
    
    CSV format should include columns:
    - first_name: Student's first name
    - last_name: Student's last name  
    - grade: Grade level (1-12)
    - password: Default password (min 6 characters)
    
    All students will be assigned to all subjects that the teacher handles.
    If a student already exists (same name + grade), their profile will be updated.
    
    Args:
        file: CSV file with student data
        current_user: The authenticated teacher
        
    Returns:
        StudentBatchUploadResponse with upload results and summary
        
    Raises:
        HTTPException: If CSV format is invalid or upload fails
    """
    teacher_uid = current_user["uid"]
    
    # TODO: Get teacher's subjects from their profile
    # For now, using a placeholder - this should be retrieved from teacher profile
    teacher_subjects = ["Mathematics", "Science", "English"]  # Placeholder
    
    try:
        logger.info(f"Processing student CSV upload for teacher {teacher_uid}")
        
        result = await student_service.upload_students_csv(
            file=file,
            teacher_uid=teacher_uid,
            teacher_subjects=teacher_subjects
        )
        
        logger.info(f"CSV upload completed: {result.upload_summary}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Student CSV upload failed for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload students: {str(e)}"
        )

@router.get("/", response_model=List[StudentProfile], tags=["Student Management"])
async def get_my_students(
    grade: Optional[int] = Query(None, ge=1, le=12, description="Filter by grade level"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[StudentProfile]:
    """
    Get all students managed by the current teacher.
    
    Args:
        grade: Optional filter by grade level
        subject: Optional filter by subject enrollment
        current_user: The authenticated teacher
        
    Returns:
        List of StudentProfile objects
        
    Raises:
        HTTPException: If retrieval fails
    """
    teacher_uid = current_user["uid"]
    
    try:
        logger.info(f"Retrieving students for teacher {teacher_uid}")
        
        students = await student_service.get_teacher_students(
            teacher_uid=teacher_uid,
            grade_filter=grade,
            subject_filter=subject
        )
        
        logger.info(f"Retrieved {len(students)} students for teacher {teacher_uid}")
        return students
        
    except Exception as e:
        logger.error(f"Failed to retrieve students for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve students: {str(e)}"
        )

@router.get("/{student_id}", response_model=StudentProfile, tags=["Student Management"])
async def get_student_details(
    student_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StudentProfile:
    """
    Get detailed information about a specific student.
    
    Args:
        student_id: The student's unique identifier
        current_user: The authenticated teacher
        
    Returns:
        StudentProfile with detailed information
        
    Raises:
        HTTPException: If student not found or access denied
    """
    teacher_uid = current_user["uid"]
    
    try:
        student = await student_service.get_student_by_id(student_id)
        
        # Verify the student belongs to this teacher
        if student.teacher_uid != teacher_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Student does not belong to this teacher"
            )
        
        return student
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get student {student_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve student: {str(e)}"
        )

@router.put("/{student_id}/subjects", tags=["Student Management"])
async def update_student_subjects(
    student_id: str,
    subjects: List[str],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Update the subjects a student is enrolled in.
    
    Args:
        student_id: The student's unique identifier
        subjects: List of subject names to enroll the student in
        current_user: The authenticated teacher
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If student not found or access denied
    """
    teacher_uid = current_user["uid"]
    
    try:
        # Verify the student belongs to this teacher
        student = await student_service.get_student_by_id(student_id)
        if student.teacher_uid != teacher_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Student does not belong to this teacher"
            )
        
        await student_service.update_student_subjects(student_id, subjects)
        
        logger.info(f"Updated subjects for student {student_id}: {subjects}")
        return {"message": f"Successfully updated subjects for {student.first_name} {student.last_name}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update subjects for student {student_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update student subjects: {str(e)}"
        )

@router.delete("/{student_id}", tags=["Student Management"])
async def deactivate_student(
    student_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Deactivate a student profile (soft delete).
    
    Args:
        student_id: The student's unique identifier
        current_user: The authenticated teacher
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If student not found or access denied
    """
    teacher_uid = current_user["uid"]
    
    try:
        # Verify the student belongs to this teacher
        student = await student_service.get_student_by_id(student_id)
        if student.teacher_uid != teacher_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Student does not belong to this teacher"
            )
        
        await student_service.deactivate_student(student_id)
        
        logger.info(f"Deactivated student {student_id}")
        return {"message": f"Successfully deactivated {student.first_name} {student.last_name}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate student {student_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate student: {str(e)}"
        )

@router.get("/stats/summary", tags=["Student Management"])
async def get_student_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get summary statistics for the teacher's students.
    
    Args:
        current_user: The authenticated teacher
        
    Returns:
        Dictionary with student statistics
    """
    teacher_uid = current_user["uid"]
    
    try:
        students = await student_service.get_teacher_students(teacher_uid)
        
        # Calculate statistics
        total_students = len(students)
        grade_distribution = {}
        subject_enrollment = {}
        
        for student in students:
            # Grade distribution
            grade = student.grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
            
            # Subject enrollment
            for subject in student.subjects:
                subject_enrollment[subject] = subject_enrollment.get(subject, 0) + 1
        
        return {
            "total_students": total_students,
            "grade_distribution": grade_distribution,
            "subject_enrollment": subject_enrollment,
            "active_students": len([s for s in students if s.is_active])
        }
        
    except Exception as e:
        logger.error(f"Failed to get student summary for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student summary: {str(e)}"
        )
