# FILE: app/services/student_service.py

import logging
import uuid
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import UploadFile, HTTPException
from app.core.firebase import db
from app.models.student import (
    StudentProfile, StudentCSVRow, StudentBatchUploadResponse,
    AssessmentConfig, Assessment, StudentAssessmentResult, LearningPath
)

logger = logging.getLogger(__name__)

class StudentService:
    """Service for managing student profiles and related operations."""
    
    def __init__(self):
        self.students_collection = "students"
        self.assessments_collection = "assessments"
        self.assessment_configs_collection = "assessment_configs"
        self.assessment_results_collection = "assessment_results"
        self.learning_paths_collection = "learning_paths"
    
    async def upload_students_csv(
        self, 
        file: UploadFile, 
        teacher_uid: str,
        teacher_subjects: List[str]
    ) -> StudentBatchUploadResponse:
        """
        Upload students from CSV file and create profiles.
        
        Args:
            file: CSV file with student data
            teacher_uid: UID of the teacher uploading students
            teacher_subjects: List of subjects the teacher handles
            
        Returns:
            StudentBatchUploadResponse with upload results
        """
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        try:
            # Read CSV content
            content = await file.read()
            csv_content = content.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Validate CSV headers
            required_headers = {'first_name', 'last_name', 'grade', 'password'}
            if not required_headers.issubset(set(csv_reader.fieldnames)):
                raise HTTPException(
                    status_code=400, 
                    detail=f"CSV must contain headers: {required_headers}. Found: {csv_reader.fieldnames}"
                )
            
            students_created = 0
            students_updated = 0
            students_failed = 0
            failed_students = []
            created_student_ids = []
            total_students = 0
            
            # Process each row
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header row
                total_students += 1
                
                try:
                    # Validate row data
                    student_data = StudentCSVRow(**row)
                    
                    # Check if student already exists (by name and grade)
                    existing_student = await self._find_existing_student(
                        teacher_uid, 
                        student_data.first_name, 
                        student_data.last_name, 
                        student_data.grade
                    )
                    
                    if existing_student:
                        # Update existing student
                        await self._update_student_profile(
                            existing_student['student_id'],
                            student_data,
                            teacher_subjects
                        )
                        students_updated += 1
                        logger.info(f"Updated existing student: {student_data.first_name} {student_data.last_name}")
                    else:
                        # Create new student profile
                        student_id = await self._create_student_profile(
                            student_data, 
                            teacher_uid, 
                            teacher_subjects
                        )
                        students_created += 1
                        created_student_ids.append(student_id)
                        logger.info(f"Created new student: {student_data.first_name} {student_data.last_name}")
                
                except Exception as e:
                    students_failed += 1
                    failed_students.append({
                        "row": row_num,
                        "data": row,
                        "error": str(e)
                    })
                    logger.error(f"Failed to process row {row_num}: {e}")
            
            # Generate summary message
            summary = f"Processed {total_students} students: {students_created} created, {students_updated} updated, {students_failed} failed"
            
            return StudentBatchUploadResponse(
                total_students=total_students,
                students_created=students_created,
                students_updated=students_updated,
                students_failed=students_failed,
                failed_students=failed_students,
                created_student_ids=created_student_ids,
                upload_summary=summary
            )
            
        except Exception as e:
            logger.error(f"Failed to process student CSV: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process CSV file: {str(e)}"
            )
    
    async def _find_existing_student(
        self, 
        teacher_uid: str, 
        first_name: str, 
        last_name: str, 
        grade: int
    ) -> Optional[Dict[str, Any]]:
        """Find existing student by name and grade."""
        try:
            query = (db.collection(self.students_collection)
                    .where("teacher_uid", "==", teacher_uid)
                    .where("first_name", "==", first_name)
                    .where("last_name", "==", last_name)
                    .where("grade", "==", grade))
            
            docs = query.get()
            if docs:
                return docs[0].to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error finding existing student: {e}")
            return None
    
    async def _create_student_profile(
        self, 
        student_data: StudentCSVRow, 
        teacher_uid: str,
        teacher_subjects: List[str]
    ) -> str:
        """Create a new student profile."""
        student_id = str(uuid.uuid4())
        
        profile = StudentProfile(
            student_id=student_id,
            teacher_uid=teacher_uid,
            first_name=student_data.first_name,
            last_name=student_data.last_name,
            grade=student_data.grade,
            default_password=student_data.password,
            subjects=teacher_subjects.copy()  # Assign all teacher's subjects
        )
        
        # Save to Firestore
        doc_ref = db.collection(self.students_collection).document(student_id)
        doc_ref.set(profile.dict())
        
        return student_id
    
    async def _update_student_profile(
        self, 
        student_id: str, 
        student_data: StudentCSVRow,
        teacher_subjects: List[str]
    ) -> None:
        """Update existing student profile."""
        update_data = {
            "first_name": student_data.first_name,
            "last_name": student_data.last_name,
            "grade": student_data.grade,
            "default_password": student_data.password,
            "subjects": teacher_subjects,
            "updated_at": datetime.utcnow()
        }
        
        doc_ref = db.collection(self.students_collection).document(student_id)
        doc_ref.update(update_data)
    
    async def get_teacher_students(
        self, 
        teacher_uid: str,
        grade_filter: Optional[int] = None,
        subject_filter: Optional[str] = None
    ) -> List[StudentProfile]:
        """Get all students for a teacher with optional filters."""
        try:
            query = db.collection(self.students_collection).where("teacher_uid", "==", teacher_uid)
            
            if grade_filter:
                query = query.where("grade", "==", grade_filter)
            
            docs = query.get()
            students = []
            
            for doc in docs:
                student_data = doc.to_dict()
                
                # Filter by subject if specified
                if subject_filter and subject_filter not in student_data.get('subjects', []):
                    continue
                
                students.append(StudentProfile(**student_data))
            
            # Sort by grade, then by last name
            students.sort(key=lambda s: (s.grade, s.last_name, s.first_name))
            
            return students
            
        except Exception as e:
            logger.error(f"Failed to get teacher students: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve students: {str(e)}"
            )
    
    async def get_student_by_id(self, student_id: str) -> StudentProfile:
        """Get a student profile by ID."""
        try:
            doc_ref = db.collection(self.students_collection).document(student_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Student not found")
            
            return StudentProfile(**doc.to_dict())
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get student: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve student: {str(e)}"
            )
    
    async def update_student_subjects(
        self, 
        student_id: str, 
        subjects: List[str]
    ) -> None:
        """Update a student's enrolled subjects."""
        try:
            doc_ref = db.collection(self.students_collection).document(student_id)
            doc_ref.update({
                "subjects": subjects,
                "updated_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Failed to update student subjects: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update student: {str(e)}"
            )
    
    async def deactivate_student(self, student_id: str) -> None:
        """Deactivate a student profile."""
        try:
            doc_ref = db.collection(self.students_collection).document(student_id)
            doc_ref.update({
                "is_active": False,
                "updated_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Failed to deactivate student: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to deactivate student: {str(e)}"
            )
    
    # ====================================================================
    # Student Assessment Methods
    # ====================================================================
    
    async def get_student_assessments(
        self,
        student_uid: str,
        teacher_uid: str,
        student_grade: int,
        student_subjects: List[str],
        subject_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[Assessment]:
        """
        Get all assessments available to a specific student.
        
        Args:
            student_uid: Student's unique identifier
            teacher_uid: Teacher's unique identifier
            student_grade: Student's grade level
            student_subjects: List of subjects student is enrolled in
            subject_filter: Optional subject filter
            status_filter: Optional status filter ('active', 'completed', 'all')
            
        Returns:
            List of Assessment objects available to the student
        """
        try:
            # Build query for assessments created by the student's teacher
            query = (db.collection(self.assessments_collection)
                    .where("teacher_uid", "==", teacher_uid)
                    .where("is_active", "==", True))
            
            # Get all assessments
            docs = query.get()
            available_assessments = []
            
            # Get student's completed assessments for status filtering
            completed_assessment_ids = set()
            if status_filter in ['completed', 'all']:
                completed_assessment_ids = await self._get_completed_assessment_ids(student_uid)
            
            for doc in docs:
                assessment_data = doc.to_dict()
                assessment = Assessment(**assessment_data)
                
                # Check if assessment is suitable for this student
                if not self._is_assessment_suitable_for_student(
                    assessment, student_grade, student_subjects, subject_filter
                ):
                    continue
                
                # Apply status filter
                if status_filter == 'active' and assessment.assessment_id in completed_assessment_ids:
                    continue
                elif status_filter == 'completed' and assessment.assessment_id not in completed_assessment_ids:
                    continue
                
                # Remove correct answers for student view (security)
                assessment = self._sanitize_assessment_for_student(assessment)
                available_assessments.append(assessment)
            
            # Sort by creation date (newest first)
            available_assessments.sort(key=lambda a: a.created_at, reverse=True)
            
            logger.info(f"Found {len(available_assessments)} assessments for student {student_uid}")
            return available_assessments
            
        except Exception as e:
            logger.error(f"Failed to get student assessments: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve assessments: {str(e)}"
            )
    
    async def get_assessment_for_student(
        self,
        assessment_id: str,
        student_uid: str,
        teacher_uid: str,
        student_grade: int,
        student_subjects: List[str]
    ) -> Optional[Assessment]:
        """
        Get a specific assessment for a student if they're eligible to take it.
        
        Args:
            assessment_id: Assessment's unique identifier
            student_uid: Student's unique identifier
            teacher_uid: Teacher's unique identifier
            student_grade: Student's grade level
            student_subjects: List of subjects student is enrolled in
            
        Returns:
            Assessment object if accessible, None otherwise
        """
        try:
            # Get the assessment
            doc_ref = db.collection(self.assessments_collection).document(assessment_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            assessment_data = doc.to_dict()
            assessment = Assessment(**assessment_data)
            
            # Verify the assessment belongs to the student's teacher
            if assessment.teacher_uid != teacher_uid:
                logger.warning(f"Assessment {assessment_id} does not belong to student's teacher")
                return None
            
            # Check if assessment is active
            if not assessment.is_active:
                logger.warning(f"Assessment {assessment_id} is not active")
                return None
            
            # Check if assessment is suitable for this student
            if not self._is_assessment_suitable_for_student(
                assessment, student_grade, student_subjects
            ):
                logger.warning(f"Assessment {assessment_id} is not suitable for student {student_uid}")
                return None
            
            # Remove correct answers for student view (security)
            assessment = self._sanitize_assessment_for_student(assessment)
            
            logger.info(f"Retrieved assessment {assessment_id} for student {student_uid}")
            return assessment
            
        except Exception as e:
            logger.error(f"Failed to get assessment for student: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve assessment: {str(e)}"
            )
    
    async def get_subjects_with_assessments(
        self,
        student_uid: str,
        teacher_uid: str,
        student_grade: int,
        student_subjects: List[str]
    ) -> List[str]:
        """
        Get list of subjects that have available assessments for the student.
        
        Args:
            student_uid: Student's unique identifier
            teacher_uid: Teacher's unique identifier
            student_grade: Student's grade level
            student_subjects: List of subjects student is enrolled in
            
        Returns:
            List of subject names with available assessments
        """
        try:
            # Get all active assessments from the student's teacher
            query = (db.collection(self.assessments_collection)
                    .where("teacher_uid", "==", teacher_uid)
                    .where("is_active", "==", True))
            
            docs = query.get()
            subjects_with_assessments = set()
            
            for doc in docs:
                assessment_data = doc.to_dict()
                assessment = Assessment(**assessment_data)
                
                # Check if assessment is suitable for this student
                if self._is_assessment_suitable_for_student(
                    assessment, student_grade, student_subjects
                ):
                    subjects_with_assessments.add(assessment.subject)
            
            return sorted(list(subjects_with_assessments))
            
        except Exception as e:
            logger.error(f"Failed to get subjects with assessments: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve subjects: {str(e)}"
            )
    
    async def get_student_assessment_summary(
        self,
        student_uid: str,
        teacher_uid: str,
        student_grade: int,
        student_subjects: List[str]
    ) -> Dict[str, Any]:
        """
        Get assessment statistics and summary for a student.
        
        Args:
            student_uid: Student's unique identifier
            teacher_uid: Teacher's unique identifier
            student_grade: Student's grade level
            student_subjects: List of subjects student is enrolled in
            
        Returns:
            Dictionary with assessment statistics
        """
        try:
            # Get all available assessments
            all_assessments = await self.get_student_assessments(
                student_uid, teacher_uid, student_grade, student_subjects, status_filter='all'
            )
            
            # Get completed assessments
            completed_assessment_ids = await self._get_completed_assessment_ids(student_uid)
            
            # Calculate statistics
            total_assessments = len(all_assessments)
            completed_assessments = len(completed_assessment_ids)
            pending_assessments = total_assessments - completed_assessments
            
            # Group by subject
            subject_stats = {}
            for assessment in all_assessments:
                subject = assessment.subject
                if subject not in subject_stats:
                    subject_stats[subject] = {
                        "total": 0,
                        "completed": 0,
                        "pending": 0
                    }
                
                subject_stats[subject]["total"] += 1
                if assessment.assessment_id in completed_assessment_ids:
                    subject_stats[subject]["completed"] += 1
                else:
                    subject_stats[subject]["pending"] += 1
            
            # Get recent assessment results
            recent_results = await self._get_recent_assessment_results(student_uid, limit=5)
            
            return {
                "total_assessments": total_assessments,
                "completed_assessments": completed_assessments,
                "pending_assessments": pending_assessments,
                "completion_rate": round((completed_assessments / total_assessments * 100) if total_assessments > 0 else 0, 1),
                "subject_breakdown": subject_stats,
                "enrolled_subjects": student_subjects,
                "recent_results": recent_results,
                "student_grade": student_grade
            }
            
        except Exception as e:
            logger.error(f"Failed to get student assessment summary: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve assessment summary: {str(e)}"
            )
    
    # ====================================================================
    # Helper Methods for Student Assessments
    # ====================================================================
    
    def _is_assessment_suitable_for_student(
        self,
        assessment: Assessment,
        student_grade: int,
        student_subjects: List[str],
        subject_filter: Optional[str] = None
    ) -> bool:
        """
        Check if an assessment is suitable for a student based on grade and subjects.
        
        Args:
            assessment: Assessment object
            student_grade: Student's grade level
            student_subjects: List of subjects student is enrolled in
            subject_filter: Optional subject filter
            
        Returns:
            True if assessment is suitable, False otherwise
        """
        # Check if student is enrolled in the assessment's subject
        if assessment.subject not in student_subjects:
            return False
        
        # Apply subject filter if specified
        if subject_filter and assessment.subject != subject_filter:
            return False
        
        # Check grade compatibility (allow assessments for same grade or one grade below/above)
        grade_difference = abs(assessment.target_grade - student_grade)
        if grade_difference > 1:
            return False
        
        return True
    
    def _sanitize_assessment_for_student(self, assessment: Assessment) -> Assessment:
        """
        Remove sensitive information from assessment for student view.
        
        Args:
            assessment: Original assessment object
            
        Returns:
            Sanitized assessment object
        """
        # Create a copy of the assessment
        sanitized_data = assessment.dict()
        
        # Remove correct answers from questions
        if 'questions' in sanitized_data:
            for question in sanitized_data['questions']:
                if 'correct_answer' in question:
                    del question['correct_answer']
                if 'explanation' in question:
                    del question['explanation']
        
        return Assessment(**sanitized_data)
    
    async def _get_completed_assessment_ids(self, student_uid: str) -> set:
        """
        Get set of assessment IDs that the student has completed.
        
        Args:
            student_uid: Student's unique identifier
            
        Returns:
            Set of completed assessment IDs
        """
        try:
            query = (db.collection(self.assessment_results_collection)
                    .where("student_id", "==", student_uid))
            
            docs = query.get()
            completed_ids = set()
            
            for doc in docs:
                result_data = doc.to_dict()
                completed_ids.add(result_data.get('assessment_id'))
            
            return completed_ids
            
        except Exception as e:
            logger.error(f"Failed to get completed assessment IDs: {e}")
            return set()
    
    async def _get_recent_assessment_results(
        self, 
        student_uid: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent assessment results for a student.
        
        Args:
            student_uid: Student's unique identifier
            limit: Maximum number of results to return
            
        Returns:
            List of recent assessment results
        """
        try:
            query = (db.collection(self.assessment_results_collection)
                    .where("student_id", "==", student_uid)
                    .order_by("completed_at", direction="DESCENDING")
                    .limit(limit))
            
            docs = query.get()
            results = []
            
            for doc in docs:
                result_data = doc.to_dict()
                results.append({
                    "assessment_id": result_data.get("assessment_id"),
                    "subject": result_data.get("subject"),
                    "score": result_data.get("score"),
                    "total_questions": result_data.get("total_questions"),
                    "completed_at": result_data.get("completed_at"),
                    "time_taken_minutes": result_data.get("time_taken_minutes")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get recent assessment results: {e}")
            return []

# Create singleton instance
student_service = StudentService()