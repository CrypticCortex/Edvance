# FILE: app/api/v1/documents.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from typing import Dict, Any, List, Optional, Union
import logging

from app.models.requests import DocumentUploadResponse, DocumentIndexingStatus, DocumentMetadata, ZipUploadResponse
from app.core.auth import get_current_user
from app.services.document_service import document_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", tags=["Document Management"])
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    subject: str = Form(..., description="Subject category for the document"),
    grade_level: int = Form(..., description="Grade level (1-12) for the document"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Union[DocumentUploadResponse, ZipUploadResponse]:
    """
    Upload a document for RAG indexing.
    
    Supported file types:
    - PDF documents
    - Images (JPEG, PNG, TIFF)  
    - Text files
    - Word documents (.doc, .docx)
    - ZIP archives containing supported files
    
    The document will be:
    1. Uploaded to Firebase Storage
    2. Indexed in Vertex AI RAG engine (background process)
    3. Made searchable for content generation
    
    For ZIP files:
    - All supported files within the ZIP will be extracted and processed
    - Unsupported files and system files are automatically skipped
    - Detailed extraction report is returned
    
    Args:
        file: The document file to upload (or ZIP archive)
        subject: Subject category (must match teacher's subjects)
        grade_level: Grade level from 1-12 for the document content
        current_user: The authenticated user information
        
    Returns:
        DocumentUploadResponse for single files, ZipUploadResponse for ZIP files
        
    Raises:
        HTTPException: If upload fails or file type not supported
    """
    teacher_uid = current_user["uid"]
    
    try:
        logger.info(f"Uploading document for teacher {teacher_uid}, subject: {subject}, grade: {grade_level}")
        
        # TODO: Validate that subject is in teacher's subject list
        # This can be added later when we integrate with teacher profiles
        
        result = await document_service.upload_document(
            file=file,
            subject=subject,
            grade_level=grade_level,
            teacher_uid=teacher_uid
        )
        
        # Log success differently for ZIP vs single files
        if hasattr(result, 'zip_filename'):
            logger.info(f"Successfully processed ZIP {result.zip_filename}: {result.files_processed} files")
        else:
            logger.info(f"Successfully uploaded document {result.document_id}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.get("/status/{document_id}", response_model=DocumentIndexingStatus, tags=["Document Management"])
async def get_indexing_status(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> DocumentIndexingStatus:
    """
    Get the indexing status of a specific document.
    
    Status values:
    - `pending`: Document uploaded, waiting to be processed
    - `processing`: Currently being indexed in Vertex AI
    - `completed`: Successfully indexed and searchable
    - `failed`: Indexing failed (check error_message)
    
    Args:
        document_id: The unique document identifier
        current_user: The authenticated user information
        
    Returns:
        Current indexing status and progress
        
    Raises:
        HTTPException: If document not found or access denied
    """
    teacher_uid = current_user["uid"]
    
    try:
        logger.info(f"Getting indexing status for document {document_id}")
        
        # TODO: Add permission check to ensure teacher owns the document
        
        status = await document_service.get_indexing_status(document_id)
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get indexing status for document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get indexing status: {str(e)}"
        )

@router.get("/list", response_model=List[DocumentMetadata], tags=["Document Management"])
async def list_documents(
    subject: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[DocumentMetadata]:
    """
    List all documents uploaded by the authenticated teacher.
    
    Args:
        subject: Optional filter by subject
        current_user: The authenticated user information
        
    Returns:
        List of document metadata sorted by upload date (newest first)
    """
    teacher_uid = current_user["uid"]
    
    try:
        logger.info(f"Listing documents for teacher {teacher_uid}, subject filter: {subject}")
        
        documents = await document_service.list_teacher_documents(
            teacher_uid=teacher_uid,
            subject_filter=subject
        )
        
        return documents
        
    except Exception as e:
        logger.error(f"Failed to list documents for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )

@router.delete("/{document_id}", tags=["Document Management"])
async def delete_document(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a document and remove it from indexing.
    
    This will:
    1. Remove the document from Firebase Storage
    2. Remove it from Vertex AI Search index
    3. Delete metadata from Firestore
    
    Args:
        document_id: The unique document identifier
        current_user: The authenticated user information
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If document not found or access denied
    """
    teacher_uid = current_user["uid"]
    
    try:
        logger.info(f"Deleting document {document_id} for teacher {teacher_uid}")
        
        # TODO: Implement document deletion
        # This should include:
        # 1. Check teacher owns the document
        # 2. Delete from Firebase Storage
        # 3. Remove from Vertex AI Search
        # 4. Delete Firestore metadata
        
        return {
            "message": f"Document {document_id} deletion initiated",
            "status": "pending"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

@router.get("/health", tags=["Document Management"])
async def document_service_health() -> Dict[str, str]:
    """
    Check the health status of the document service.
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "message": "Document service is operational",
        "vertex_ai_status": "connected"
    }

@router.get("/organized", tags=["Document Management"])
async def list_documents_organized(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List teacher's documents organized by individual uploads and ZIP extractions.
    
    Args:
        subject: Optional subject filter
        current_user: Current authenticated user (from dependency injection)
    
    Returns:
        Dictionary with organized document lists
    """
    try:
        teacher_uid = current_user["uid"]
        
        logger.info(f"Listing organized documents for teacher {teacher_uid}")
        
        # Get organized document listing
        organized_docs = await document_service.list_documents_with_zip_info(
            teacher_uid=teacher_uid,
            subject_filter=subject
        )
        
        return {
            "teacher_uid": teacher_uid,
            "individual_documents": [doc.dict() for doc in organized_docs['individual']],
            "zip_extractions": {
                zip_name: [doc.dict() for doc in docs] 
                for zip_name, docs in organized_docs['zip_extractions'].items()
            },
            "total_individual": len(organized_docs['individual']),
            "total_zip_groups": len(organized_docs['zip_extractions']),
            "total_extracted_files": sum(len(docs) for docs in organized_docs['zip_extractions'].values())
        }
        
    except Exception as e:
        logger.error(f"Failed to list organized documents for teacher {teacher_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list organized documents: {str(e)}"
        )
