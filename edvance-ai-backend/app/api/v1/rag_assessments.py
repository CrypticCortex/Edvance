# FILE: app/api/v1/rag_assessments.py

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, UploadFile, File
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.services.enhanced_assessment_service import EnhancedAssessmentService
from app.services.document_processor import DocumentProcessor
from app.models.student import AssessmentConfig, Assessment
from app.models.rag_models import ProcessedDocument

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG Assessments"])

# Initialize services
enhanced_assessment_service = EnhancedAssessmentService()
document_processor = DocumentProcessor()

# ====================================================================
# Document Upload and Processing Endpoints
# ====================================================================

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    processing_status: str
    message: str

@router.post("/documents/upload", response_model=DocumentUploadResponse, tags=["Document Management"])
async def upload_document_for_rag(
    file: UploadFile = File(...),
    subject: Optional[str] = Query(None, description="Subject area"),
    grade_level: Optional[int] = Query(None, description="Target grade level"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> DocumentUploadResponse:
    """
    Upload a document for RAG processing.
    
    Supported formats: PDF, DOCX, TXT
    """
    teacher_uid = current_user["uid"]
    
    try:
        # Validate file type
        allowed_types = [".pdf", ".docx", ".txt"]
        file_extension = "." + file.filename.split(".")[-1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process document
            document_id = f"doc_{teacher_uid}_{int(datetime.utcnow().timestamp())}"
            
            processed_doc = await document_processor.process_document(
                file_path=tmp_file_path,
                document_id=document_id,
                teacher_uid=teacher_uid,
                filename=file.filename,
                subject=subject,
                grade_level=grade_level
            )
            
            return DocumentUploadResponse(
                document_id=processed_doc.document_id,
                filename=processed_doc.original_filename,
                processing_status=processed_doc.processing_status.value,
                message=f"Document uploaded and processed successfully. Created {processed_doc.total_chunks} text chunks."
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed for {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )

@router.get("/documents", response_model=List[ProcessedDocument], tags=["Document Management"])
async def get_teacher_documents(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[ProcessedDocument]:
    """Get all documents uploaded by the teacher."""
    
    teacher_uid = current_user["uid"]
    
    try:
        documents = await document_processor.get_teacher_documents(teacher_uid)
        return documents
        
    except Exception as e:
        logger.error(f"Failed to get documents for {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )

@router.get("/documents/{document_id}", response_model=ProcessedDocument, tags=["Document Management"])
async def get_document_details(
    document_id: str = Path(..., description="Document ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ProcessedDocument:
    """Get details of a specific document."""
    
    teacher_uid = current_user["uid"]
    
    try:
        document = await document_processor.get_processed_document(document_id)
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        # Verify ownership
        if document.teacher_uid != teacher_uid:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this document"
            )
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        )

# ====================================================================
# RAG Assessment Generation Endpoints
# ====================================================================

@router.post("/configs/{config_id}/generate-rag", response_model=Assessment, tags=["RAG Generation"])
async def generate_rag_assessment(
    config_id: str = Path(..., description="Assessment configuration ID"),
    force_rag: bool = Query(True, description="Force RAG generation even with limited context"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Assessment:
    """
    Generate an assessment using RAG and AI based on uploaded documents.
    
    This endpoint uses the teacher's uploaded documents to generate 
    contextually relevant questions using AI.
    """
    teacher_uid = current_user["uid"]
    
    try:
        # Get the configuration
        config = await enhanced_assessment_service.get_assessment_config_by_id(
            config_id=config_id,
            teacher_uid=teacher_uid
        )
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="Assessment configuration not found"
            )
        
        # Generate RAG-enhanced assessment
        assessment = await enhanced_assessment_service.create_rag_assessment(
            config=config,
            force_rag=force_rag
        )
        
        logger.info(f"Generated RAG assessment {assessment.assessment_id} from config {config_id}")
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate RAG assessment from config {config_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate RAG assessment: {str(e)}"
        )

@router.get("/assessments/{assessment_id}/metadata", tags=["RAG Generation"])
async def get_assessment_metadata(
    assessment_id: str = Path(..., description="Assessment ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed metadata about how an assessment was generated,
    including RAG context and AI generation details.
    """
    teacher_uid = current_user["uid"]
    
    try:
        assessment_data = await enhanced_assessment_service.get_assessment_with_metadata(assessment_id)
        
        if not assessment_data:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )
        
        # TODO: Add ownership verification once we track assessment ownership
        
        # Return metadata
        metadata = {
            "assessment_id": assessment_id,
            "generation_method": assessment_data.get("generation_method", "simple"),
            "rag_metadata": assessment_data.get("rag_metadata", {}),
            "basic_info": {
                "title": assessment_data.get("title"),
                "subject": assessment_data.get("subject"),
                "grade": assessment_data.get("grade"),
                "topic": assessment_data.get("topic"),
                "question_count": len(assessment_data.get("questions", []))
            }
        }
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get assessment metadata {assessment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment metadata: {str(e)}"
        )

# ====================================================================
# Content Search and Analytics Endpoints  
# ====================================================================

class ContentSearchRequest(BaseModel):
    search_query: str
    subject_filter: Optional[str] = None
    grade_filter: Optional[int] = None

@router.post("/content/search", tags=["Content Management"])
async def search_uploaded_content(
    request: ContentSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Search through uploaded document content using semantic similarity.
    """
    teacher_uid = current_user["uid"]
    
    try:
        results = await enhanced_assessment_service.search_teacher_content(
            teacher_uid=teacher_uid,
            search_query=request.search_query,
            subject_filter=request.subject_filter,
            grade_filter=request.grade_filter
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Content search failed for {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content search failed: {str(e)}"
        )

@router.get("/analytics/rag-stats", tags=["Analytics"])
async def get_rag_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get RAG usage analytics and content statistics for the teacher.
    """
    teacher_uid = current_user["uid"]
    
    try:
        stats = await enhanced_assessment_service.get_teacher_rag_statistics(teacher_uid)
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get RAG analytics for {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve RAG analytics: {str(e)}"
        )
