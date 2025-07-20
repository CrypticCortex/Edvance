# FILE: app/models/learning_models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    """Difficulty levels for learning content."""
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADVANCED = "advanced"

class LearningObjectiveType(str, Enum):
    """Types of learning objectives based on Bloom's taxonomy."""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class KnowledgeGap(BaseModel):
    """Represents a knowledge gap identified from assessment results."""
    gap_id: str = Field(..., description="Unique gap identifier")
    student_id: str = Field(..., description="Student who has this gap")
    subject: str = Field(..., description="Subject area")
    topic: str = Field(..., description="Specific topic")
    subtopic: Optional[str] = Field(None, description="More specific subtopic")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level where gap exists")
    learning_objective: LearningObjectiveType = Field(..., description="Type of learning objective")
    
    # Performance metrics
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in gap identification")
    severity_score: float = Field(..., ge=0.0, le=1.0, description="How severe this gap is")
    frequency: int = Field(default=1, description="How many times this gap appeared")
    
    # Context
    source_assessments: List[str] = Field(default=[], description="Assessment IDs that identified this gap")
    related_questions: List[str] = Field(default=[], description="Question IDs that revealed this gap")
    prerequisites: List[str] = Field(default=[], description="Topics that should be learned first")
    
    identified_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class LearningStep(BaseModel):
    """A single step in a learning path."""
    step_id: str = Field(..., description="Unique step identifier")
    step_number: int = Field(..., description="Order in the learning path")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="What this step covers")
    
    # Content
    subject: str = Field(..., description="Subject area")
    topic: str = Field(..., description="Main topic")
    subtopic: Optional[str] = Field(None, description="Specific subtopic")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level")
    learning_objective: LearningObjectiveType = Field(..., description="Learning goal")
    
    # Resources
    content_type: str = Field(..., description="Type of content (video, reading, practice, etc.)")
    content_url: Optional[str] = Field(None, description="Link to content")
    content_text: Optional[str] = Field(None, description="Text content or instructions")
    estimated_duration_minutes: int = Field(default=15, description="Expected time to complete")
    
    # Dependencies
    prerequisites: List[str] = Field(default=[], description="Step IDs that must be completed first")
    addresses_gaps: List[str] = Field(default=[], description="Knowledge gap IDs this step addresses")
    
    # Completion tracking
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(None)
    performance_score: Optional[float] = Field(None, description="How well student performed on this step")

class LearningPath(BaseModel):
    """A personalized learning path for a student."""
    path_id: str = Field(..., description="Unique path identifier")
    student_id: str = Field(..., description="Student this path is for")
    teacher_uid: str = Field(..., description="Teacher who created/assigned this path")
    
    # Path metadata
    title: str = Field(..., description="Path title")
    description: str = Field(..., description="What this path accomplishes")
    subject: str = Field(..., description="Main subject")
    target_grade: int = Field(..., ge=1, le=12, description="Target grade level")
    
    # Learning goals
    learning_goals: List[str] = Field(default=[], description="What student will achieve")
    addresses_gaps: List[str] = Field(default=[], description="Knowledge gap IDs this path addresses")
    
    # Path structure
    steps: List[LearningStep] = Field(default=[], description="Ordered list of learning steps")
    total_estimated_duration_minutes: int = Field(default=0, description="Total expected time")
    
    # Progress tracking
    current_step: int = Field(default=0, description="Current step index")
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    
    # Personalization metadata
    generation_method: str = Field(default="ai_generated", description="How this path was created")
    source_assessments: List[str] = Field(default=[], description="Assessments that informed this path")
    adaptation_history: List[Dict[str, Any]] = Field(default=[], description="How path was modified over time")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class StudentPerformance(BaseModel):
    """Student performance on an assessment."""
    performance_id: str = Field(..., description="Unique performance record ID")
    student_id: str = Field(..., description="Student identifier")
    assessment_id: str = Field(..., description="Assessment taken")
    
    # Overall performance
    total_questions: int = Field(..., description="Total questions in assessment")
    correct_answers: int = Field(..., description="Number of correct answers")
    score_percentage: float = Field(..., ge=0.0, le=100.0, description="Overall score percentage")
    time_taken_minutes: int = Field(..., description="Time taken to complete")
    
    # Detailed performance
    question_performances: List[Dict[str, Any]] = Field(default=[], description="Performance on each question")
    topic_scores: Dict[str, float] = Field(default={}, description="Score by topic")
    difficulty_scores: Dict[str, float] = Field(default={}, description="Score by difficulty level")
    learning_objective_scores: Dict[str, float] = Field(default={}, description="Score by learning objective")
    
    # Analysis
    strengths: List[str] = Field(default=[], description="Topics/skills student performed well on")
    weaknesses: List[str] = Field(default=[], description="Topics/skills needing improvement")
    recommended_focus_areas: List[str] = Field(default=[], description="Areas to focus on next")
    
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class LearningRecommendation(BaseModel):
    """AI-generated learning recommendation for a student."""
    recommendation_id: str = Field(..., description="Unique recommendation ID")
    student_id: str = Field(..., description="Student this is for")
    
    # Recommendation content
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="What this recommendation suggests")
    rationale: str = Field(..., description="Why this is recommended")
    
    # Specifics
    recommended_action: str = Field(..., description="Specific action to take")
    content_type: str = Field(..., description="Type of content to study")
    difficulty_level: DifficultyLevel = Field(..., description="Recommended difficulty")
    estimated_duration_minutes: int = Field(..., description="Expected time investment")
    
    # Priority
    priority_score: float = Field(..., ge=0.0, le=1.0, description="How important this recommendation is")
    urgency_level: str = Field(..., description="How urgent this is (low/medium/high)")
    
    # Context
    based_on_assessments: List[str] = Field(default=[], description="Assessments that informed this")
    addresses_gaps: List[str] = Field(default=[], description="Knowledge gaps this addresses")
    
    # Status
    is_active: bool = Field(default=True)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
