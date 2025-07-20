# FILE: app/models/requests.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ====================================================================
# Authentication Models
# ====================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    id_token: str
    token_type: str = "bearer"

class UserInDB(BaseModel):
    uid: str
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)
    subjects: Optional[List[str]] = [] # <-- ADD THIS LINE

class UserProfileUpdate(BaseModel): # <-- ADD THIS NEW MODEL
    """
    Request model for updating a user's profile, e.g., their subjects.
    """
    subjects: List[str] = Field(..., description="A list of subjects the teacher handles.")

# ====================================================================
# Agent Interaction Models
# ====================================================================

class AgentPrompt(BaseModel):
    """Request model for agent invocation."""
    prompt: str = Field(..., description="The user's prompt to send to the agent", min_length=1)
    
class AgentResponse(BaseModel):
    """Response model for agent invocation."""
    response: str = Field(..., description="The agent's response text")
    session_id: Optional[str] = Field(None, description="The session ID for conversation continuity")
    
class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="The health status")
    message: str = Field(..., description="Additional health information")

# ====================================================================
# Content Generation Models
# ====================================================================

class LocalContentRequest(BaseModel):
    topic: str
    language: str
    cultural_context: Optional[str] = None
    grade_level: int = Field(..., ge=1, le=12, description="Grade level from 1 to 12")
    content_type: str = Field(..., pattern="^(story|explanation)$", description="Must be 'story' or 'explanation'")

class GeneratedContentResponse(BaseModel):
    id: str
    title: str
    content: str
    topic: str
    grade_level: int
    language: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
