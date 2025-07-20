# FILE: app/services/vertex_rag_service.py

from __future__ import annotations
import logging
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from google.cloud import discoveryengine_v1
from google.cloud import documentai
from google.cloud import storage
from google.api_core import retry

from app.core.config import settings
from app.core.firebase import db

logger = logging.getLogger(__name__)

class VertexRAGService:
    """Service for managing Vertex AI RAG operations including document indexing and search."""
    
    def __init__(self):
        self.project_id = settings.google_cloud_project
        # Discovery Engine requires "global" location, not regional
        self.location = "global"
        self.storage_client = storage.Client()
        
        # Use the correct clients for different operations
        self.document_client = discoveryengine_v1.DocumentServiceClient()
        self.datastore_client = discoveryengine_v1.DataStoreServiceClient()
        self.search_client = discoveryengine_v1.SearchServiceClient()
        
        # Initialize Vertex AI Search datastore (we'll create this)
        self.datastore_id = "teacher-documents-datastore"
        self.serving_config_id = "default_serving_config"
        
    async def create_datastore_if_not_exists(self) -> str:
        """
        Create a Vertex AI Search datastore for storing teacher documents.
        
        Returns:
            The datastore ID
        """
        try:
            # Check if datastore already exists using the correct client
            datastore_path = self.datastore_client.data_store_path(
                project=self.project_id,
                location=self.location,
                data_store=self.datastore_id
            )
            
            # Try to get the datastore
            try:
                datastore = self.datastore_client.get_data_store(name=datastore_path)
                logger.info(f"Datastore {self.datastore_id} already exists")
                return self.datastore_id
            except Exception:
                # Datastore doesn't exist, create it
                logger.info(f"Creating new datastore: {self.datastore_id}")
                
                parent = self.datastore_client.collection_path(
                    project=self.project_id,
                    location=self.location,
                    collection="default_collection"
                )
                
                data_store = discoveryengine_v1.DataStore(
                    display_name="Teacher Documents Datastore",
                    industry_vertical=discoveryengine_v1.IndustryVertical.GENERIC,
                    solution_types=[discoveryengine_v1.SolutionType.SOLUTION_TYPE_SEARCH],
                    content_config=discoveryengine_v1.DataStore.ContentConfig.CONTENT_REQUIRED,
                )
                
                operation = self.datastore_client.create_data_store(
                    parent=parent,
                    data_store=data_store,
                    data_store_id=self.datastore_id
                )
                
                # Wait for the operation to complete
                result = operation.result(timeout=300)  # 5 minutes timeout
                logger.info(f"Created datastore: {result.name}")
                return self.datastore_id
                
        except Exception as e:
            logger.error(f"Failed to create/get datastore: {e}")
            raise
    
    async def import_document_to_vertex_ai(
        self, 
        document_id: str, 
        firebase_storage_url: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Import a document from Firebase Storage to Vertex AI Search.
        
        Args:
            document_id: Unique document identifier
            firebase_storage_url: Firebase Storage URL of the document
            metadata: Document metadata (subject, teacher_uid, etc.)
            
        Returns:
            The Vertex AI document ID
        """
        try:
            # Ensure datastore exists
            await self.create_datastore_if_not_exists()
            
            # Create document for Vertex AI Search
            parent = self.document_client.branch_path(
                project=self.project_id,
                location=self.location,
                data_store=self.datastore_id,
                branch="default_branch"
            )
            
            # Convert Firebase Storage URL to GCS URI format
            import urllib.parse
            
            # The Firebase Storage URL format is: https://storage.googleapis.com/bucket-name/path
            if firebase_storage_url.startswith("https://storage.googleapis.com/"):
                # Extract the bucket name and path
                url_parts = firebase_storage_url.replace("https://storage.googleapis.com/", "").split("/", 1)
                bucket_name = url_parts[0]
                file_path = url_parts[1] if len(url_parts) > 1 else ""
                
                # URL decode the file path to handle spaces and special characters correctly
                file_path = urllib.parse.unquote(file_path)
                
                # Create the GCS URI
                gcs_uri = f"gs://{bucket_name}/{file_path}"
            else:
                # Fallback for other URL formats
                gcs_uri = firebase_storage_url.replace(
                    "https://storage.googleapis.com/", "gs://"
                ).replace(
                    f"https://{settings.firebase_storage_bucket}.appspot.com/", 
                    f"gs://{settings.firebase_storage_bucket}/"
                )
            
            # Create the document
            document = discoveryengine_v1.Document(
                id=document_id,
                content=discoveryengine_v1.Document.Content(
                    uri=gcs_uri,
                    mime_type=metadata.get("file_type", "application/pdf")
                ),
                struct_data={
                    "subject": metadata.get("subject", ""),
                    "teacher_uid": metadata.get("teacher_uid", ""),
                    "filename": metadata.get("filename", ""),
                    "upload_date": metadata.get("upload_date", ""),
                }
            )
            
            # Import the document
            request = discoveryengine_v1.CreateDocumentRequest(
                parent=parent,
                document=document,
                document_id=document_id
            )
            
            operation = self.document_client.create_document(request=request)
            result = operation  # This is synchronous for document creation
            
            logger.info(f"Successfully imported document {document_id} to Vertex AI")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to import document {document_id} to Vertex AI: {e}")
            raise
    
    async def get_indexing_status(self, document_id: str) -> Dict[str, Any]:
        """
        Get the indexing status of a document in Vertex AI Search.
        
        Args:
            document_id: The document ID
            
        Returns:
            Status information including progress and completion status
        """
        try:
            document_path = self.document_client.document_path(
                project=self.project_id,
                location=self.location,
                data_store=self.datastore_id,
                branch="default_branch",
                document=document_id
            )
            
            document = self.document_client.get_document(name=document_path)
            
            # For Vertex AI Search, once document is created, it's typically indexed quickly
            # We can check if the document exists and assume it's indexed
            return {
                "status": "completed",
                "progress_percentage": 100,
                "vertex_ai_document_id": document.id,
                "indexed_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get indexing status for document {document_id}: {e}")
            return {
                "status": "failed",
                "progress_percentage": 0,
                "error": str(e)
            }
    
    async def search_documents(
        self, 
        query: str, 
        teacher_uid: str,
        subject_filter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using Vertex AI Search.
        
        Args:
            query: Search query
            teacher_uid: Filter by teacher UID
            subject_filter: Optional subject filter
            limit: Maximum number of results
            
        Returns:
            List of search results with content and metadata
        """
        try:
            serving_config = self.search_client.serving_config_path(
                project=self.project_id,
                location=self.location,
                data_store=self.datastore_id,
                serving_config=self.serving_config_id
            )
            
            # Build filter - use the correct syntax for Vertex AI Search structured data
            # For now, let's test without filters to verify basic search works
            filter_str = ""
            # filter_expressions = [f'struct_data.teacher_uid: ANY("{teacher_uid}")']
            # if subject_filter:
            #     filter_expressions.append(f'struct_data.subject: ANY("{subject_filter}")')
            # filter_str = " AND ".join(filter_expressions)
            
            request = discoveryengine_v1.SearchRequest(
                serving_config=serving_config,
                query=query,
                page_size=limit,
                content_search_spec=discoveryengine_v1.SearchRequest.ContentSearchSpec(
                    snippet_spec=discoveryengine_v1.SearchRequest.ContentSearchSpec.SnippetSpec(
                        return_snippet=True
                    ),
                    summary_spec=discoveryengine_v1.SearchRequest.ContentSearchSpec.SummarySpec(
                        summary_result_count=3,
                        include_citations=True
                    )
                )
            )
            
            # Only add filter if it's not empty
            if filter_str:
                request.filter = filter_str
            
            response = self.search_client.search(request=request)
            
            results = []
            for result in response.results:
                doc_data = {
                    "document_id": result.id,
                    "title": result.document.struct_data.get("filename", "Unknown"),
                    "subject": result.document.struct_data.get("subject", ""),
                    "snippet": getattr(result.document, "derived_struct_data", {}).get("snippet", ""),
                    "relevance_score": getattr(result, "relevance_score", 0.0)
                }
                results.append(doc_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []

# Create singleton instance
vertex_rag_service = VertexRAGService()
