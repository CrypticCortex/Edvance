# FILE: app/models/requests.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# ====================================================================
# Authentication Models
# ====================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    role: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

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
    subjects: Optional[List[str]] = []
    role: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

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
# Document Management Models
# ====================================================================

class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str = Field(..., description="Unique identifier for the uploaded document")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="MIME type of the file")
    subject: str = Field(..., description="Subject category for the document")
    grade_level: int = Field(..., ge=1, le=12, description="Grade level (1-12)")
    upload_status: str = Field(default="uploaded", description="Current upload status")
    storage_url: str = Field(..., description="Firebase Storage URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentIndexingStatus(BaseModel):
    """Response model for document indexing status."""
    document_id: str = Field(..., description="Document identifier")
    indexing_status: str = Field(..., description="Current indexing status: pending, processing, completed, failed")
    progress_percentage: int = Field(default=0, description="Indexing progress (0-100)")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_message: Optional[str] = Field(None, description="Error message if indexing failed")
    vertex_ai_index_id: Optional[str] = Field(None, description="Vertex AI Search index ID")

class ExtractedFileInfo(BaseModel):
    """Information about a file extracted from a ZIP archive."""
    filename: str = Field(..., description="Original filename from ZIP")
    document_id: str = Field(..., description="Generated document ID")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="MIME type of the file")
    extraction_status: str = Field(..., description="Status: success, skipped, failed")
    storage_url: Optional[str] = Field(None, description="Firebase Storage URL if successful")
    error_message: Optional[str] = Field(None, description="Error message if extraction failed")

class ZipUploadResponse(BaseModel):
    """Enhanced response model for ZIP file upload."""
    zip_filename: str = Field(..., description="Original ZIP filename")
    zip_file_size: int = Field(..., description="ZIP file size in bytes")
    total_files_found: int = Field(..., description="Total files found in ZIP")
    files_processed: int = Field(..., description="Number of files successfully processed")
    files_skipped: int = Field(..., description="Number of files skipped (unsupported/too large)")
    files_failed: int = Field(..., description="Number of files that failed to process")
    extracted_files: List[ExtractedFileInfo] = Field(..., description="Details of each extracted file")
    upload_status: str = Field(default="completed", description="Overall upload status")
    subject: str = Field(..., description="Subject category for documents")
    grade_level: int = Field(..., ge=1, le=12, description="Grade level (1-12)")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentMetadata(BaseModel):
    """Document metadata for storage and search."""
    document_id: str
    teacher_uid: str
    filename: str
    file_type: str
    file_size: int
    subject: str
    grade_level: int
    storage_path: str
    firebase_url: str
    upload_date: datetime
    indexing_status: str
    vertex_ai_index_id: Optional[str] = None
    page_count: Optional[int] = None
    text_content_preview: Optional[str] = None
    content_analysis: Optional[Dict[str, Any]] = None  # AI-generated content analysis
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata like parent_zip

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
