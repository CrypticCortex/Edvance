# FILE: app/models/viva_models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class VivaStatus(str, Enum):
    """Status of a viva session."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class VivaMessage(BaseModel):
    """A message in a viva conversation."""
    sender: str = Field(..., description="'student' or 'agent'")
    text: str = Field(..., description="The transcribed text of the speech")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class VivaSession(BaseModel):
    """A model for a viva voce session."""
    session_id: str = Field(..., description="Unique viva session identifier")
    student_id: str = Field(..., description="Student participating in the viva")
    learning_step_id: str = Field(..., description="The learning step this viva is for")
    
    # Viva Content
    topic: str = Field(..., description="The topic of the viva")
    language: str = Field("english", description="Language for the viva (english, telugu, tamil)")
    
    # Session State
    status: VivaStatus = Field(default=VivaStatus.PENDING)
    conversation_history: List[VivaMessage] = Field(default=[], description="The conversation history")
    
    # Performance
    score: float = Field(default=0.0, description="The student's score")
    feedback: Optional[str] = Field(None, description="Qualitative feedback for the student")
    
    # Timestamps
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None