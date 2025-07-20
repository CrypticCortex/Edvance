# FILE: app/models/student.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class StudentProfile(BaseModel):
    """Student profile model."""
    student_id: str = Field(..., description="Unique student identifier")
    teacher_uid: str = Field(..., description="Teacher who manages this student")
    first_name: str = Field(..., min_length=1, description="Student's first name")
    last_name: str = Field(..., min_length=1, description="Student's last name")
    grade: int = Field(..., ge=1, le=12, description="Student's current grade level")
    default_password: str = Field(..., min_length=6, description="Teacher-generated default password")
    subjects: List[str] = Field(default=[], description="Subjects the student is enrolled in")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = Field(default=True)
    
    # Learning analytics
    current_learning_paths: Dict[str, str] = Field(default={}, description="Subject -> Learning Path ID mapping")
    completed_assessments: List[str] = Field(default=[], description="List of completed assessment IDs")
    performance_metrics: Dict[str, Any] = Field(default={}, description="Performance tracking data")

class StudentCSVRow(BaseModel):
    """Model for validating CSV row data."""
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1) 
    grade: int = Field(..., ge=1, le=12)
    password: str = Field(..., min_length=6)
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().title()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v.strip()) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v.strip()

class StudentBatchUploadResponse(BaseModel):
    """Response for student batch upload."""
    total_students: int = Field(..., description="Total students in CSV")
    students_created: int = Field(..., description="Successfully created students")
    students_updated: int = Field(..., description="Updated existing students")
    students_failed: int = Field(..., description="Failed to process students")
    failed_students: List[Dict[str, Any]] = Field(default=[], description="Details of failed student creations")
    created_student_ids: List[str] = Field(default=[], description="IDs of successfully created students")
    upload_summary: str = Field(..., description="Summary message")

class AssessmentConfig(BaseModel):
    """Configuration for assessment creation."""
    config_id: str = Field(..., description="Unique configuration ID")
    teacher_uid: str = Field(..., description="Teacher who created this config")
    name: str = Field(..., description="Assessment configuration name")
    subject: str = Field(..., description="Subject for assessment")
    target_grade: int = Field(..., ge=1, le=12, description="Target grade level")
    difficulty_level: str = Field(..., pattern="^(easy|medium|hard)$", description="Difficulty level")
    topic: str = Field(..., description="Specific topic to assess")
    question_count: int = Field(default=10, ge=5, le=20, description="Number of MCQ questions")
    time_limit_minutes: int = Field(default=30, ge=10, le=120, description="Time limit in minutes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

class AssessmentQuestion(BaseModel):
    """Individual assessment question."""
    question_id: str = Field(..., description="Unique question ID")
    question_text: str = Field(..., description="The question text")
    options: List[str] = Field(..., min_items=4, max_items=4, description="Four answer options")
    correct_answer: int = Field(..., ge=0, le=3, description="Index of correct answer (0-3)")
    explanation: str = Field(..., description="Explanation for the correct answer")
    difficulty: str = Field(..., description="Question difficulty level")
    topic: str = Field(..., description="Topic this question covers")

class Assessment(BaseModel):
    """Complete assessment model."""
    assessment_id: str = Field(..., description="Unique assessment ID")
    config_id: str = Field(..., description="Configuration used to create this assessment")
    teacher_uid: str = Field(..., description="Teacher who created the assessment")
    title: str = Field(..., description="Assessment title")
    subject: str = Field(..., description="Subject")
    grade: int = Field(..., description="Target grade")
    difficulty: str = Field(..., description="Difficulty level")
    topic: str = Field(..., description="Topic")
    questions: List[AssessmentQuestion] = Field(..., description="List of questions")
    time_limit_minutes: int = Field(..., description="Time limit")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
class StudentAssessmentResult(BaseModel):
    """Student's assessment result."""
    result_id: str = Field(..., description="Unique result ID")
    student_id: str = Field(..., description="Student who took the assessment")
    assessment_id: str = Field(..., description="Assessment that was taken")
    answers: List[int] = Field(..., description="Student's answers (indices)")
    score: int = Field(..., ge=0, description="Number of correct answers")
    total_questions: int = Field(..., description="Total number of questions")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage score")
    time_taken_minutes: int = Field(..., description="Time taken to complete")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Analysis results
    strengths: List[str] = Field(default=[], description="Topics student performed well in")
    weaknesses: List[str] = Field(default=[], description="Topics student needs improvement in")
    recommended_learning_path: Optional[str] = Field(None, description="Recommended learning path ID")

class LearningPath(BaseModel):
    """Personalized learning path for a student."""
    path_id: str = Field(..., description="Unique learning path ID")
    student_id: str = Field(..., description="Student this path is for")
    subject: str = Field(..., description="Subject")
    current_grade: int = Field(..., description="Student's current grade")
    target_grade: int = Field(..., description="Target grade level")
    
    # Path content
    topics_to_cover: List[str] = Field(..., description="Ordered list of topics to study")
    current_topic_index: int = Field(default=0, description="Current position in learning path")
    difficulty_progression: List[str] = Field(..., description="Difficulty level for each topic")
    
    # Resources
    assigned_documents: List[str] = Field(default=[], description="Document IDs assigned to this path")
    completed_topics: List[str] = Field(default=[], description="Topics student has completed")
    
    # Progress tracking
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall progress")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
