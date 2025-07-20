# FILE: app/services/vector_service.py

import logging
import uuid
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False

from google.cloud import aiplatform
from app.core.config import settings
from app.models.rag_models import DocumentChunk, RAGQuery, RAGResult, VectorSearchMetrics

logger = logging.getLogger(__name__)

class VectorService:
    """Service for vector database operations using ChromaDB."""
    
    def __init__(self):
        self.settings = settings
        self.collection_name = "document_embeddings"
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection."""
        try:
            if not CHROMADB_AVAILABLE:
                raise ImportError("ChromaDB not installed. Run: pip install chromadb")
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize Vertex AI embedding function
            self.embedding_function = self._get_vertex_embedding_function()
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Connected to existing collection: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"description": "Document chunks for RAG"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {str(e)}")
            raise e
    
    def _get_vertex_embedding_function(self):
        """Get Vertex AI embedding function."""
        try:
            # Use Google Vertex AI for embeddings
            return embedding_functions.GoogleVertexEmbeddingFunction(
                api_key=None,  # Will use service account
                model_name="text-embedding-005",
                project_id=self.settings.google_cloud_project or self.settings.firebase_project_id
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI embeddings: {str(e)}")
            # Fallback to sentence transformers
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
    
    async def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to vector database."""
        try:
            if not chunks:
                return True
            
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                documents.append(chunk.content)
                ids.append(chunk.chunk_id)
                
                # Prepare metadata (ChromaDB requires flat dict)
                metadata = {
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "teacher_uid": chunk.metadata.get("teacher_uid", ""),
                    "subject": chunk.metadata.get("subject", ""),
                    "grade_level": chunk.metadata.get("grade_level", 0),
                    "filename": chunk.metadata.get("filename", ""),
                    "created_at": chunk.created_at.isoformat()
                }
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add chunks to vector database: {str(e)}")
            return False
    
    async def search_similar_chunks(
        self,
        query: RAGQuery
    ) -> List[RAGResult]:
        """Search for similar document chunks."""
        try:
            start_time = datetime.utcnow()
            
            # Build where filter
            where_filter = {}
            if query.subject:
                where_filter["subject"] = query.subject
            if query.grade_level:
                where_filter["grade_level"] = query.grade_level
            
            # Perform vector search
            results = self.collection.query(
                query_texts=[query.query_text],
                n_results=query.max_results,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            rag_results = []
            if results and results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                
                for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1.0 - distance
                    
                    # Skip results below threshold
                    if similarity_score < query.similarity_threshold:
                        continue
                    
                    # Create DocumentChunk from search result
                    chunk = DocumentChunk(
                        chunk_id=results["ids"][0][i],
                        document_id=metadata["document_id"],
                        content=doc,
                        chunk_index=metadata["chunk_index"],
                        metadata={
                            "teacher_uid": metadata.get("teacher_uid", ""),
                            "subject": metadata.get("subject", ""),
                            "grade_level": metadata.get("grade_level", 0),
                            "filename": metadata.get("filename", "")
                        }
                    )
                    
                    rag_result = RAGResult(
                        chunk=chunk,
                        similarity_score=similarity_score,
                        document_metadata={
                            "filename": metadata.get("filename", ""),
                            "document_id": metadata["document_id"]
                        }
                    )
                    rag_results.append(rag_result)
            
            # Calculate metrics
            end_time = datetime.utcnow()
            query_time = (end_time - start_time).total_seconds() * 1000
            
            metrics = VectorSearchMetrics(
                query_time_ms=query_time,
                total_documents=self.collection.count(),
                results_returned=len(rag_results),
                average_similarity=sum(r.similarity_score for r in rag_results) / len(rag_results) if rag_results else 0.0
            )
            
            logger.info(f"Vector search completed: {len(rag_results)} results, {query_time:.2f}ms")
            return rag_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
    
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get a specific chunk by ID."""
        try:
            results = self.collection.get(
                ids=[chunk_id],
                include=["documents", "metadatas"]
            )
            
            if results and results["documents"]:
                doc = results["documents"][0]
                metadata = results["metadatas"][0]
                
                return DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=metadata["document_id"],
                    content=doc,
                    chunk_index=metadata["chunk_index"],
                    metadata={
                        "teacher_uid": metadata.get("teacher_uid", ""),
                        "subject": metadata.get("subject", ""),
                        "grade_level": metadata.get("grade_level", 0),
                        "filename": metadata.get("filename", "")
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get chunk {chunk_id}: {str(e)}")
            return None
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a document."""
        try:
            # Get all chunks for the document
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents"]
            )
            
            if results and results["ids"]:
                chunk_ids = results["ids"]
                self.collection.delete(ids=chunk_ids)
                logger.info(f"Deleted {len(chunk_ids)} chunks for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection."""
        try:
            count = self.collection.count()
            
            # Get sample of metadata to analyze subjects/grades
            sample_results = self.collection.get(
                limit=100,
                include=["metadatas"]
            )
            
            subjects = set()
            grades = set()
            
            if sample_results and sample_results["metadatas"]:
                for metadata in sample_results["metadatas"]:
                    if metadata.get("subject"):
                        subjects.add(metadata["subject"])
                    if metadata.get("grade_level"):
                        grades.add(metadata["grade_level"])
            
            return {
                "total_chunks": count,
                "unique_subjects": list(subjects),
                "grade_levels": sorted(list(grades)),
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {
                "total_chunks": 0,
                "unique_subjects": [],
                "grade_levels": [],
                "collection_name": self.collection_name
            }
    
    def reset_collection(self) -> bool:
        """Reset the vector collection (for testing/development)."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Document chunks for RAG"}
            )
            logger.info("Vector collection reset successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reset collection: {str(e)}")
            return False
