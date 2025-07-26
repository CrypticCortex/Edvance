# FILE: app/models/rag_models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DocumentChunk(BaseModel):
    """A chunk of text extracted from a document."""
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    document_id: str = Field(..., description="ID of the source document")
    content: str = Field(..., description="Text content of the chunk")
    chunk_index: int = Field(..., description="Index of this chunk in the document")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    embedding_vector: Optional[List[float]] = Field(None, description="Vector embedding of the content")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentProcessingStatus(str, Enum):
    """Status of document processing."""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessedDocument(BaseModel):
    """Metadata for a processed document."""
    document_id: str = Field(..., description="Unique document identifier")
    teacher_uid: str = Field(..., description="Teacher who uploaded the document")
    original_filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Document type (pdf, docx, etc)")
    subject: Optional[str] = Field(None, description="Subject area")
    grade_level: Optional[int] = Field(None, description="Target grade level")
    total_chunks: int = Field(0, description="Number of chunks created")
    processing_status: DocumentProcessingStatus = Field(DocumentProcessingStatus.PENDING)
    processing_error: Optional[str] = Field(None, description="Error message if processing failed")
    processed_at: Optional[datetime] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RAGQuery(BaseModel):
    """Query for RAG retrieval."""
    query_text: str = Field(..., description="Query text for retrieval")
    subject: str = Field(..., description="Subject filter")
    grade_level: int = Field(..., description="Grade level filter")
    topic: Optional[str] = Field(None, description="Specific topic filter")
    max_results: int = Field(5, description="Maximum number of chunks to retrieve")
    similarity_threshold: float = Field(0.7, description="Minimum similarity score")

class RAGResult(BaseModel):
    """Result from RAG retrieval."""
    chunk: DocumentChunk = Field(..., description="Retrieved document chunk")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    document_metadata: Dict[str, Any] = Field(default_factory=dict, description="Source document metadata")

class QuestionGenerationRequest(BaseModel):
    """Request for AI question generation."""
    context_chunks: List[RAGResult] = Field(..., description="Retrieved context chunks")
    subject: str = Field(..., description="Subject area")
    grade_level: int = Field(..., description="Target grade level") 
    topic: str = Field(..., description="Specific topic")
    difficulty_level: str = Field(..., description="Difficulty: easy, medium, hard")
    question_count: int = Field(..., description="Number of questions to generate")
    question_type: str = Field("multiple_choice", description="Type of questions")
    language: str = Field(default="english", description="Language for AI generation (english, tamil, telugu)")

class GeneratedQuestionContext(BaseModel):
    """Additional context for a generated question."""
    source_chunks: List[str] = Field(..., description="IDs of source chunks used")
    confidence_score: float = Field(..., description="AI confidence in question quality")
    generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="AI generation details")

class EnhancedAssessmentQuestion(BaseModel):
    """Extended assessment question with RAG context."""
    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="Multiple choice options")
    correct_answer: int = Field(..., description="Index of correct answer (0-based)")
    explanation: str = Field(..., description="Explanation of the correct answer")
    difficulty: str = Field(..., description="Question difficulty level")
    topic: str = Field(..., description="Question topic")
    
    # RAG-specific fields
    context: GeneratedQuestionContext = Field(..., description="Generation context")
    bloom_taxonomy_level: Optional[str] = Field(None, description="Cognitive level (remember, understand, apply, etc)")
    learning_objectives: List[str] = Field(default_factory=list, description="Learning objectives addressed")
    
class VectorSearchMetrics(BaseModel):
    """Metrics for vector search performance."""
    query_time_ms: float = Field(..., description="Time taken for query")
    total_documents: int = Field(..., description="Total documents in collection")
    results_returned: int = Field(..., description="Number of results returned")
    average_similarity: float = Field(..., description="Average similarity score")
    search_timestamp: datetime = Field(default_factory=datetime.utcnow)
