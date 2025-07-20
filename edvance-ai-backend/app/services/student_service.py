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

# Create singleton instance
student_service = StudentService()
