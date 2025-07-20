# FILE: app/models.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ====================================================================
# Authentication Models
# ====================================================================

class UserCreate(BaseModel):
    """
    Request model for creating a new user.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class UserLogin(BaseModel):
    """
    Request model for user login.
    Client-side should use this to get an ID token from Firebase.
    """
    email: EmailStr
    password: str

class Token(BaseModel):
    """
    Response model for a successful authentication, containing the access token.
    Our backend will receive this token from the client for protected routes.
    """
    id_token: str
    token_type: str = "bearer"

class UserInDB(BaseModel):
    """
    Model representing user data as stored in Firestore.
    """
    uid: str
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ====================================================================
# Content Generation Models (from your design document)
# We will use these in the next step.
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
    language: str
    grade_level: int
    topic: str
    created_at: datetime
    teacher_id: str # This will be the user's UID