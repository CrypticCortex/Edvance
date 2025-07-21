# FILE: app/models/lesson_models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class SlideType(str, Enum):
    """Types of slides in a lesson."""
    INTRODUCTION = "introduction"
    CONCEPT_EXPLANATION = "concept_explanation"
    EXAMPLE = "example"
    PRACTICE = "practice"
    INTERACTIVE_EXERCISE = "interactive_exercise"
    SUMMARY = "summary"
    ASSESSMENT = "assessment"
    REFLECTION = "reflection"

class ContentElementType(str, Enum):
    """Types of content elements within a slide."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    INTERACTIVE_WIDGET = "interactive_widget"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    DIAGRAM = "diagram"
    CODE_SNIPPET = "code_snippet"

class InteractiveWidget(BaseModel):
    """Interactive widget within a slide."""
    widget_id: str = Field(..., description="Unique widget identifier")
    widget_type: str = Field(..., description="Type of widget (drag_drop, multiple_choice, fill_blank, etc.)")
    title: str = Field(..., description="Widget title")
    instructions: str = Field(..., description="Instructions for the student")
    content: Dict[str, Any] = Field(..., description="Widget-specific content and configuration")
    correct_answer: Optional[Dict[str, Any]] = Field(None, description="Correct answer for validation")
    hints: List[str] = Field(default=[], description="Hints to help students")
    points: int = Field(default=1, description="Points awarded for correct completion")

class ContentElement(BaseModel):
    """A content element within a slide."""
    element_id: str = Field(..., description="Unique element identifier")
    element_type: ContentElementType = Field(..., description="Type of content element")
    title: Optional[str] = Field(None, description="Element title")
    content: Union[str, Dict[str, Any]] = Field(..., description="Element content")
    position: int = Field(..., description="Position within the slide")
    
    # Interactive elements
    interactive_widget: Optional[InteractiveWidget] = Field(None, description="Interactive widget if applicable")
    
    # Media elements
    media_url: Optional[str] = Field(None, description="URL for media content")
    alt_text: Optional[str] = Field(None, description="Alternative text for accessibility")
    
    # Styling and layout
    styling: Dict[str, Any] = Field(default={}, description="Styling and layout options")

class LessonSlide(BaseModel):
    """A single slide in a lesson."""
    slide_id: str = Field(..., description="Unique slide identifier")
    slide_number: int = Field(..., description="Order in the lesson")
    slide_type: SlideType = Field(..., description="Type of slide")
    title: str = Field(..., description="Slide title")
    subtitle: Optional[str] = Field(None, description="Slide subtitle")
    
    # Content
    content_elements: List[ContentElement] = Field(default=[], description="Content elements in this slide")
    learning_objective: str = Field(..., description="What students will learn from this slide")
    
    # Navigation and timing
    estimated_duration_minutes: int = Field(default=5, description="Expected time to complete")
    prerequisites: List[str] = Field(default=[], description="Previous slide IDs that should be completed first")
    
    # Interactivity
    is_interactive: bool = Field(default=False, description="Whether slide requires student interaction")
    completion_criteria: Dict[str, Any] = Field(default={}, description="Criteria for slide completion")
    
    # Student progress
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(None)
    student_responses: Dict[str, Any] = Field(default={}, description="Student responses to interactive elements")
    time_spent_seconds: int = Field(default=0, description="Time student spent on this slide")

class LessonContent(BaseModel):
    """Complete lesson content with slides and metadata."""
    lesson_id: str = Field(..., description="Unique lesson identifier")
    learning_step_id: str = Field(..., description="Associated learning step ID")
    student_id: str = Field(..., description="Student this lesson is for")
    teacher_uid: str = Field(..., description="Teacher who owns this lesson")
    
    # Lesson metadata
    title: str = Field(..., description="Lesson title")
    description: str = Field(..., description="What this lesson covers")
    subject: str = Field(..., description="Subject area")
    topic: str = Field(..., description="Main topic")
    subtopic: Optional[str] = Field(None, description="Specific subtopic")
    grade_level: int = Field(..., description="Target grade level")
    
    # Content structure
    slides: List[LessonSlide] = Field(default=[], description="Ordered list of slides")
    total_slides: int = Field(default=0, description="Total number of slides")
    
    # Learning context
    learning_objectives: List[str] = Field(default=[], description="Overall lesson objectives")
    prerequisite_knowledge: List[str] = Field(default=[], description="What students should know beforehand")
    key_concepts: List[str] = Field(default=[], description="Key concepts covered")
    
    # Progress tracking
    current_slide: int = Field(default=0, description="Current slide index")
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    total_time_spent_minutes: int = Field(default=0)
    
    # Generation metadata
    generation_method: str = Field(default="ai_generated", description="How this lesson was created")
    content_source: List[str] = Field(default=[], description="Source materials used")
    personalization_factors: Dict[str, Any] = Field(default={}, description="Factors used for personalization")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    """A message in the lesson chatbot conversation."""
    message_id: str = Field(..., description="Unique message identifier")
    lesson_id: str = Field(..., description="Associated lesson ID")
    sender: str = Field(..., description="'student' or 'agent'")
    message: str = Field(..., description="Message content")
    message_type: str = Field(default="text", description="Type of message (text, image, code, etc.)")
    
    # Context
    current_slide_id: Optional[str] = Field(None, description="Slide student was on when asking")
    related_concept: Optional[str] = Field(None, description="Concept the message relates to")
    
    # Agent response metadata (for agent messages)
    confidence_score: Optional[float] = Field(None, description="Agent's confidence in response")
    sources: List[str] = Field(default=[], description="Sources used for response")
    suggested_actions: List[str] = Field(default=[], description="Suggested next steps")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LessonChatSession(BaseModel):
    """A chatbot session for a lesson."""
    session_id: str = Field(..., description="Unique session identifier")
    lesson_id: str = Field(..., description="Associated lesson ID")
    student_id: str = Field(..., description="Student in this session")
    
    # Conversation
    messages: List[ChatMessage] = Field(default=[], description="Conversation messages")
    
    # Session state
    is_active: bool = Field(default=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(None)
    
    # Analytics
    total_messages: int = Field(default=0)
    student_questions: int = Field(default=0)
    agent_responses: int = Field(default=0)
    session_duration_minutes: int = Field(default=0)

class LessonProgress(BaseModel):
    """Detailed progress tracking for a lesson."""
    progress_id: str = Field(..., description="Unique progress identifier")
    lesson_id: str = Field(..., description="Associated lesson ID")
    student_id: str = Field(..., description="Student ID")
    
    # Overall progress
    slides_completed: int = Field(default=0)
    slides_total: int = Field(..., description="Total slides in lesson")
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Detailed slide progress
    slide_progress: List[Dict[str, Any]] = Field(default=[], description="Progress on each slide")
    
    # Engagement metrics
    time_spent_minutes: int = Field(default=0)
    interactions_count: int = Field(default=0)
    correct_responses: int = Field(default=0)
    total_responses: int = Field(default=0)
    
    # Learning indicators
    concept_mastery: Dict[str, float] = Field(default={}, description="Mastery level for each concept")
    areas_of_difficulty: List[str] = Field(default=[], description="Concepts student struggled with")
    strengths: List[str] = Field(default=[], description="Areas where student excelled")
    
    # Chatbot usage
    chatbot_sessions: int = Field(default=0)
    questions_asked: int = Field(default=0)
    help_requests: int = Field(default=0)
    
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
