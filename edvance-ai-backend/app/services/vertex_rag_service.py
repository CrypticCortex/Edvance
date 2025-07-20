# FILE: app/services/vertex_rag_service.py

import logging
import uuid
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
import vertexai

from app.core.config import settings
from app.core.firebase import db
from app.models.rag_models import DocumentChunk, RAGQuery, RAGResult, VectorSearchMetrics

logger = logging.getLogger(__name__)

class VertexAIRAGService:
    """RAG service using Vertex AI Vector Search and Embeddings."""
    
    def __init__(self):
        self.project_id = settings.google_cloud_project
        self.location = settings.google_cloud_location
        self.collection_name = "document_embeddings"
        self.embedding_model = None
        self._initialize_vertex_ai()
        
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI."""
        try:
            vertexai.init(
                project=self.project_id,
                location=self.location
            )
            
            # Initialize embedding model
            self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")
            
            logger.info("Vertex AI RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI RAG: {str(e)}")
            # Don't raise, allow graceful fallback
            self.embedding_model = None
    
    async def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to Firestore with embeddings."""
        try:
            if not chunks:
                return True
                
            if not self.embedding_model:
                logger.warning("Embedding model not available, saving chunks without embeddings")
                return await self._save_chunks_without_embeddings(chunks)
            
            # Generate embeddings for all chunks
            texts = [chunk.content for chunk in chunks]
            embeddings = await self._generate_embeddings(texts)
            
            # Store chunks with embeddings in Firestore
            batch = db.batch()
            
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding_vector = embedding
                
                doc_ref = db.collection(self.collection_name).document(chunk.chunk_id)
                chunk_data = chunk.dict()
                batch.set(doc_ref, chunk_data)
            
            batch.commit()
            
            logger.info(f"Added {len(chunks)} chunks with embeddings to Firestore")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add chunks: {str(e)}")
            return False
    
    async def _save_chunks_without_embeddings(self, chunks: List[DocumentChunk]) -> bool:
        """Fallback to save chunks without embeddings."""
        try:
            batch = db.batch()
            
            for chunk in chunks:
                doc_ref = db.collection(self.collection_name).document(chunk.chunk_id)
                chunk_data = chunk.dict()
                batch.set(doc_ref, chunk_data)
            
            batch.commit()
            logger.info(f"Saved {len(chunks)} chunks without embeddings")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save chunks without embeddings: {str(e)}")
            return False
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Vertex AI."""
        try:
            if not self.embedding_model:
                return [[0.0] * 768 for _ in texts]  # Return dummy embeddings
            
            # Batch embeddings for efficiency
            embeddings = []
            batch_size = 5  # Process 5 texts at a time
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.embedding_model.get_embeddings(batch_texts)
                
                for embedding in batch_embeddings:
                    embeddings.append(embedding.values)
                
                # Small delay to avoid rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            return [[0.0] * 768 for _ in texts]  # Return dummy embeddings as fallback
    
    async def search_similar_chunks(self, query: RAGQuery) -> List[RAGResult]:
        """Search for similar chunks using vector similarity."""
        try:
            start_time = datetime.utcnow()
            
            if not self.embedding_model:
                logger.warning("Embedding model not available, using text-based search")
                return await self._text_based_search(query)
            
            # Generate embedding for query
            query_embeddings = await self._generate_embeddings([query.query_text])
            query_embedding = query_embeddings[0]
            
            # Build Firestore query with filters
            collection_ref = db.collection(self.collection_name)
            firestore_query = collection_ref
            
            # Apply filters
            if query.subject:
                firestore_query = firestore_query.where("metadata.subject", "==", query.subject)
            if query.grade_level:
                firestore_query = firestore_query.where("metadata.grade_level", "==", query.grade_level)
            
            # Get all matching documents
            docs = firestore_query.stream()
            
            # Calculate similarity scores
            candidates = []
            for doc in docs:
                doc_data = doc.to_dict()
                
                if not doc_data.get("embedding_vector"):
                    continue
                
                # Calculate cosine similarity
                similarity = self._calculate_cosine_similarity(
                    query_embedding, 
                    doc_data["embedding_vector"]
                )
                
                if similarity >= query.similarity_threshold:
                    chunk = DocumentChunk(**doc_data)
                    result = RAGResult(
                        chunk=chunk,
                        similarity_score=similarity,
                        document_metadata={
                            "filename": chunk.metadata.get("filename", ""),
                            "document_id": chunk.document_id
                        }
                    )
                    candidates.append(result)
            
            # Sort by similarity and return top results
            candidates.sort(key=lambda x: x.similarity_score, reverse=True)
            results = candidates[:query.max_results]
            
            # Calculate metrics
            end_time = datetime.utcnow()
            query_time = (end_time - start_time).total_seconds() * 1000
            
            logger.info(f"Vector search completed: {len(results)} results, {query_time:.2f}ms")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
    
    async def _text_based_search(self, query: RAGQuery) -> List[RAGResult]:
        """Fallback text-based search when embeddings aren't available."""
        try:
            collection_ref = db.collection(self.collection_name)
            firestore_query = collection_ref
            
            # Apply filters
            if query.subject:
                firestore_query = firestore_query.where("metadata.subject", "==", query.subject)
            if query.grade_level:
                firestore_query = firestore_query.where("metadata.grade_level", "==", query.grade_level)
            
            docs = firestore_query.stream()
            
            # Simple text matching
            candidates = []
            query_words = set(query.query_text.lower().split())
            
            for doc in docs:
                doc_data = doc.to_dict()
                content = doc_data.get("content", "").lower()
                content_words = set(content.split())
                
                # Calculate word overlap as similarity
                overlap = len(query_words.intersection(content_words))
                similarity = overlap / max(len(query_words), 1)
                
                if similarity >= query.similarity_threshold:
                    chunk = DocumentChunk(**doc_data)
                    result = RAGResult(
                        chunk=chunk,
                        similarity_score=similarity,
                        document_metadata={
                            "filename": chunk.metadata.get("filename", ""),
                            "document_id": chunk.document_id
                        }
                    )
                    candidates.append(result)
            
            # Sort and return top results
            candidates.sort(key=lambda x: x.similarity_score, reverse=True)
            return candidates[:query.max_results]
            
        except Exception as e:
            logger.error(f"Text-based search failed: {str(e)}")
            return []
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np
            
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            magnitude1 = np.linalg.norm(vec1)
            magnitude2 = np.linalg.norm(vec2)
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return float(dot_product / (magnitude1 * magnitude2))
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {str(e)}")
            return 0.0
    
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get a specific chunk by ID."""
        try:
            doc_ref = db.collection(self.collection_name).document(chunk_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return DocumentChunk(**doc.to_dict())
            return None
            
        except Exception as e:
            logger.error(f"Failed to get chunk {chunk_id}: {str(e)}")
            return None
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a document."""
        try:
            query = db.collection(self.collection_name).where("document_id", "==", document_id)
            docs = query.stream()
            
            batch = db.batch()
            chunk_count = 0
            
            for doc in docs:
                batch.delete(doc.reference)
                chunk_count += 1
            
            if chunk_count > 0:
                batch.commit()
                logger.info(f"Deleted {chunk_count} chunks for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection."""
        try:
            # Count total documents
            collection_ref = db.collection(self.collection_name)
            docs = collection_ref.stream()
            
            total_count = 0
            subjects = set()
            grades = set()
            with_embeddings = 0
            
            for doc in docs:
                total_count += 1
                doc_data = doc.to_dict()
                metadata = doc_data.get("metadata", {})
                
                if doc_data.get("embedding_vector"):
                    with_embeddings += 1
                
                if metadata.get("subject"):
                    subjects.add(metadata["subject"])
                if metadata.get("grade_level"):
                    grades.add(metadata["grade_level"])
            
            return {
                "total_chunks": total_count,
                "chunks_with_embeddings": with_embeddings,
                "unique_subjects": list(subjects),
                "grade_levels": sorted(list(grades)),
                "collection_name": self.collection_name,
                "embedding_model": "text-embedding-005" if self.embedding_model else "none"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {
                "total_chunks": 0,
                "chunks_with_embeddings": 0,
                "unique_subjects": [],
                "grade_levels": [],
                "collection_name": self.collection_name,
                "error": str(e)
            }

# Global instance for easy import
vertex_rag_service = VertexAIRAGService()
