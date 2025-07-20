# FILE: app/services/document_service.py

from __future__ import annotations
import logging
import uuid
import asyncio
import zipfile
import io
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import os
import tempfile

from fastapi import UploadFile, HTTPException
from google.cloud import storage
import PyPDF2
from PIL import Image

from app.core.config import settings
from app.core.firebase import db, storage_bucket
from app.models.requests import DocumentUploadResponse, DocumentIndexingStatus, DocumentMetadata, ZipUploadResponse, ExtractedFileInfo
from app.services.vertex_rag_service import vertex_rag_service

logger = logging.getLogger(__name__)

class MockUploadFile:
    """Mock UploadFile for extracted ZIP contents."""
    def __init__(self, filename: str, content: bytes, content_type: str):
        self.filename = filename
        self.content_type = content_type
        self.file = io.BytesIO(content)
        self.size = len(content)
    
    async def read(self, size: int = -1) -> bytes:
        return self.file.read(size)
    
    def seek(self, offset: int, whence: int = 0):
        return self.file.seek(offset, whence)

class DocumentService:
    """Service for handling document upload, storage, and indexing operations."""
    
    def __init__(self):
        self.storage_client = storage.Client()
        self.allowed_file_types = {
            "application/pdf": ".pdf",
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/tiff": ".tiff",
            "text/plain": ".txt",
            "application/msword": ".doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/zip": ".zip",
            "application/x-zip-compressed": ".zip"
        }
        self.max_file_size = 50 * 1024 * 1024  # 50MB
    
    def validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file type and size.
        
        Args:
            file: The uploaded file
            
        Raises:
            HTTPException: If file is invalid
        """
        # Check file type
        if file.content_type not in self.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not supported. Allowed types: {list(self.allowed_file_types.keys())}"
            )
        
        # Check file size (approximate, based on headers)
        if hasattr(file, 'size') and file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size {file.size} exceeds maximum allowed size of {self.max_file_size} bytes"
            )
    
    async def extract_zip_contents(
        self, 
        zip_content: bytes, 
        subject: str, 
        grade_level: int,
        teacher_uid: str,
        original_filename: str
    ) -> ZipUploadResponse:
        """
        Extract ZIP file contents and upload each file individually.
        
        Args:
            zip_content: ZIP file content as bytes
            subject: Subject category for documents
            grade_level: Grade level (1-12) for the documents
            teacher_uid: UID of the teacher uploading the documents
            original_filename: Original ZIP filename
            
        Returns:
            ZipUploadResponse with detailed extraction information
        """
        extracted_files = []
        files_processed = 0
        files_skipped = 0
        files_failed = 0
        total_files_found = 0
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
                # Get list of files in the ZIP
                file_list = zip_ref.namelist()
                
                # Filter out directories and system files
                actual_files = [f for f in file_list if not f.endswith('/') and not f.startswith('.') and '/__MACOSX/' not in f]
                total_files_found = len(actual_files)
                
                logger.info(f"Found {total_files_found} processable files in ZIP: {original_filename}")
                
                for file_path in actual_files:
                    try:
                        # Extract file content
                        file_content = zip_ref.read(file_path)
                        
                        # Get just the filename from the path
                        filename = os.path.basename(file_path)
                        if not filename:
                            continue
                        
                        # Determine file type based on extension
                        file_extension = os.path.splitext(filename)[1].lower()
                        content_type = self._get_content_type_from_extension(file_extension)
                        
                        if not content_type:
                            files_skipped += 1
                            extracted_files.append(ExtractedFileInfo(
                                filename=filename,
                                document_id="",
                                file_size=len(file_content),
                                file_type="unknown",
                                extraction_status="skipped",
                                error_message=f"Unsupported file type: {file_extension}"
                            ))
                            logger.warning(f"Skipping unsupported file type: {filename}")
                            continue
                        
                        # Validate file size
                        if len(file_content) > self.max_file_size:
                            files_skipped += 1
                            extracted_files.append(ExtractedFileInfo(
                                filename=filename,
                                document_id="",
                                file_size=len(file_content),
                                file_type=content_type,
                                extraction_status="skipped",
                                error_message=f"File size ({len(file_content)} bytes) exceeds limit ({self.max_file_size} bytes)"
                            ))
                            logger.warning(f"Skipping file {filename}: size exceeds limit")
                            continue
                        
                        # Create a mock UploadFile for the extracted content
                        mock_file = MockUploadFile(filename, file_content, content_type)
                        
                        # Upload the extracted file
                        result = await self._upload_single_document(
                            mock_file, subject, grade_level, teacher_uid, 
                            parent_zip=original_filename
                        )
                        
                        files_processed += 1
                        extracted_files.append(ExtractedFileInfo(
                            filename=filename,
                            document_id=result.document_id,
                            file_size=result.file_size,
                            file_type=result.file_type,
                            extraction_status="success",
                            storage_url=result.storage_url
                        ))
                        
                        logger.info(f"Successfully extracted and uploaded: {filename}")
                        
                    except Exception as e:
                        files_failed += 1
                        extracted_files.append(ExtractedFileInfo(
                            filename=filename if 'filename' in locals() else file_path,
                            document_id="",
                            file_size=len(file_content) if 'file_content' in locals() else 0,
                            file_type=content_type if 'content_type' in locals() else "unknown",
                            extraction_status="failed",
                            error_message=str(e)
                        ))
                        logger.error(f"Failed to process file {file_path} from ZIP: {e}")
                        continue
                        
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=400,
                detail="Invalid ZIP file format"
            )
        except Exception as e:
            logger.error(f"Failed to process ZIP file {original_filename}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process ZIP file: {str(e)}"
            )
        
        return ZipUploadResponse(
            zip_filename=original_filename,
            zip_file_size=len(zip_content),
            total_files_found=total_files_found,
            files_processed=files_processed,
            files_skipped=files_skipped,
            files_failed=files_failed,
            extracted_files=extracted_files,
            upload_status="completed" if files_failed == 0 else "partial",
            subject=subject,
            grade_level=grade_level
        )
    
    def _get_content_type_from_extension(self, extension: str) -> Optional[str]:
        """Get content type from file extension."""
        extension_map = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        return extension_map.get(extension.lower())
    
    async def _upload_single_document(
        self,
        file: UploadFile,
        subject: str,
        grade_level: int,
        teacher_uid: str,
        parent_zip: Optional[str] = None
    ) -> DocumentUploadResponse:
        """Upload a single document (used for both direct uploads and ZIP extraction)."""
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create storage path
        file_extension = self.allowed_file_types.get(file.content_type, "")
        if not file_extension:
            # Try to get extension from filename
            file_extension = os.path.splitext(file.filename)[1]
        
        filename_clean = file.filename.replace(" ", "_").replace("/", "_")
        
        # If this file is from a ZIP, include the ZIP name in the path
        if parent_zip:
            zip_name_clean = parent_zip.replace(" ", "_").replace("/", "_").replace(".zip", "")
            storage_path = f"documents/{teacher_uid}/{subject}/{zip_name_clean}/{document_id}_{filename_clean}"
        else:
            storage_path = f"documents/{teacher_uid}/{subject}/{document_id}_{filename_clean}"
        
        # Upload to Firebase Storage
        blob = storage_bucket.blob(storage_path)
        blob.upload_from_string(
            file_content,
            content_type=file.content_type
        )
        
        # Get the public URL
        storage_url = blob.public_url
        
        # Create document metadata
        metadata = DocumentMetadata(
            document_id=document_id,
            teacher_uid=teacher_uid,
            filename=file.filename,
            file_type=file.content_type,
            file_size=file_size,
            subject=subject,
            grade_level=grade_level,
            storage_path=storage_path,
            firebase_url=storage_url,
            upload_date=datetime.utcnow(),
            indexing_status="pending"
        )
        
        # Add parent ZIP info if applicable
        if parent_zip:
            metadata.metadata = {"parent_zip": parent_zip}
        
        # Save metadata to Firestore
        await self.save_document_metadata(metadata)
        
        # Start background indexing task
        asyncio.create_task(self.index_document_background(document_id, metadata))
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            file_type=file.content_type,
            subject=subject,
            grade_level=grade_level,
            upload_status="uploaded",
            storage_url=storage_url
        )
    
    async def upload_document(
        self, 
        file: UploadFile, 
        subject: str, 
        grade_level: int,
        teacher_uid: str
    ) -> Union[DocumentUploadResponse, ZipUploadResponse]:
        """
        Upload a document to Firebase Storage and create metadata.
        Handles both individual files and ZIP archives.
        
        Args:
            file: The uploaded file
            subject: Subject category for the document
            grade_level: Grade level (1-12) for the document
            teacher_uid: UID of the teacher uploading the document
            
        Returns:
            DocumentUploadResponse for single files, ZipUploadResponse for ZIP files
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Validate file
            self.validate_file(file)
            
            # Check if this is a ZIP file
            if file.content_type in ["application/zip", "application/x-zip-compressed"]:
                # Read ZIP content
                zip_content = await file.read()
                
                # Extract and upload all files in the ZIP
                zip_response = await self.extract_zip_contents(
                    zip_content, subject, grade_level, teacher_uid, file.filename
                )
                
                if zip_response.files_processed == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="No valid documents could be extracted from the ZIP file"
                    )
                
                return zip_response
            else:
                # Handle single file upload
                return await self._upload_single_document(file, subject, grade_level, teacher_uid)
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload document: {str(e)}"
            )
    
    async def save_document_metadata(self, metadata: DocumentMetadata) -> None:
        """
        Save document metadata to Firestore.
        
        Args:
            metadata: The document metadata to save
        """
        try:
            doc_ref = db.collection("documents").document(metadata.document_id)
            doc_ref.set(metadata.dict())
            logger.info(f"Saved metadata for document {metadata.document_id}")
        except Exception as e:
            logger.error(f"Failed to save document metadata: {e}")
            raise
    
    async def index_document_background(self, document_id: str, metadata: DocumentMetadata) -> None:
        """
        Background task to index document in Vertex AI RAG.
        
        Args:
            document_id: The document ID
            metadata: Document metadata
        """
        try:
            logger.info(f"Starting indexing for document {document_id}")
            
            # Update status to processing
            await self.update_indexing_status(document_id, "processing", 20)
            
            # Prepare metadata for Vertex AI
            vertex_metadata = {
                "teacher_uid": metadata.teacher_uid,
                "subject": metadata.subject,
                "grade_level": metadata.grade_level,
                "filename": metadata.filename,
                "file_type": metadata.file_type,
                "upload_date": metadata.upload_date.isoformat()
            }
            
            # Import to Vertex AI Search
            vertex_doc_id = await vertex_rag_service.import_document_to_vertex_ai(
                document_id=document_id,
                firebase_storage_url=metadata.firebase_url,
                metadata=vertex_metadata
            )
            
            # Update status to completed
            await self.update_indexing_status(document_id, "completed", 100, vertex_doc_id)
            
            logger.info(f"Successfully indexed document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to index document {document_id}: {e}")
            await self.update_indexing_status(document_id, "failed", 0, error_message=str(e))
    
    async def update_indexing_status(
        self, 
        document_id: str, 
        status: str, 
        progress: int,
        vertex_ai_index_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update the indexing status of a document.
        
        Args:
            document_id: The document ID
            status: New status (pending, processing, completed, failed)
            progress: Progress percentage (0-100)
            vertex_ai_index_id: Vertex AI index ID if completed
            error_message: Error message if failed
        """
        try:
            doc_ref = db.collection("documents").document(document_id)
            update_data = {
                "indexing_status": status,
                "indexing_progress": progress,
                "updated_at": datetime.utcnow()
            }
            
            if vertex_ai_index_id:
                update_data["vertex_ai_index_id"] = vertex_ai_index_id
            
            if error_message:
                update_data["error_message"] = error_message
            
            doc_ref.update(update_data)
            logger.info(f"Updated indexing status for document {document_id}: {status} ({progress}%)")
            
        except Exception as e:
            logger.error(f"Failed to update indexing status: {e}")
    
    async def get_indexing_status(self, document_id: str) -> DocumentIndexingStatus:
        """
        Get the current indexing status of a document.
        
        Args:
            document_id: The document ID
            
        Returns:
            DocumentIndexingStatus with current status
        """
        try:
            doc_ref = db.collection("documents").document(document_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Document not found")
            
            doc_data = doc.to_dict()
            
            return DocumentIndexingStatus(
                document_id=document_id,
                indexing_status=doc_data.get("indexing_status", "unknown"),
                progress_percentage=doc_data.get("indexing_progress", 0),
                vertex_ai_index_id=doc_data.get("vertex_ai_index_id"),
                error_message=doc_data.get("error_message")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get indexing status: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get indexing status: {str(e)}"
            )
    
    async def list_teacher_documents(
        self, 
        teacher_uid: str, 
        subject_filter: Optional[str] = None
    ) -> List[DocumentMetadata]:
        """
        List all documents uploaded by a teacher.
        
        Args:
            teacher_uid: The teacher's UID
            subject_filter: Optional subject filter
            
        Returns:
            List of DocumentMetadata
        """
        try:
            query = db.collection("documents").where("teacher_uid", "==", teacher_uid)
            
            if subject_filter:
                query = query.where("subject", "==", subject_filter)
            
            docs = query.order_by("upload_date", direction="DESCENDING").get()
            
            documents = []
            for doc in docs:
                doc_data = doc.to_dict()
                documents.append(DocumentMetadata(**doc_data))
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list teacher documents: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list documents: {str(e)}"
            )
    
    async def list_documents_with_zip_info(
        self, 
        teacher_uid: str, 
        subject_filter: Optional[str] = None
    ) -> Dict[str, List[DocumentMetadata]]:
        """
        List teacher documents grouped by ZIP files and individual uploads.
        
        Args:
            teacher_uid: UID of the teacher
            subject_filter: Optional filter by subject
            
        Returns:
            Dictionary with 'individual' and 'zip_extractions' keys containing document lists
        """
        try:
            documents = await self.list_teacher_documents(teacher_uid, subject_filter)
            
            individual_docs = []
            zip_groups = {}
            
            for doc in documents:
                # Check if this document was extracted from a ZIP
                if hasattr(doc, 'metadata') and doc.metadata and 'parent_zip' in doc.metadata:
                    parent_zip = doc.metadata['parent_zip']
                    if parent_zip not in zip_groups:
                        zip_groups[parent_zip] = []
                    zip_groups[parent_zip].append(doc)
                else:
                    individual_docs.append(doc)
            
            return {
                'individual': individual_docs,
                'zip_extractions': zip_groups
            }
            
        except Exception as e:
            logger.error(f"Failed to list documents with ZIP info: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list documents: {str(e)}"
            )

# Create singleton instance
document_service = DocumentService()
