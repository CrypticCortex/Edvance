# FILE: app/services/rag_service.py

import logging
from typing import List, Dict, Any, Optional
import asyncio

from app.services.vertex_rag_service import VertexAIRAGService
from app.models.rag_models import RAGQuery, RAGResult, DocumentChunk
from app.core.firebase import db

logger = logging.getLogger(__name__)

class RAGService:
    """Service for Retrieval-Augmented Generation operations."""
    
    def __init__(self):
        self.vector_service = VertexAIRAGService()
        self.processed_docs_collection = "processed_documents"
    
    async def retrieve_context_for_assessment(
        self,
        subject: str,
        grade_level: int,
        topic: str,
        teacher_uid: str,
        max_chunks: int = 5
    ) -> List[RAGResult]:
        """Retrieve relevant context for assessment generation."""
        
        try:
            # Create search queries with different strategies
            queries = self._create_search_queries(subject, grade_level, topic)
            
            all_results = []
            
            for query in queries:
                # Add teacher filter to query if needed
                results = await self.vector_service.search_similar_chunks(query)
                
                # Filter by teacher ownership
                filtered_results = await self._filter_by_teacher_ownership(results, teacher_uid)
                all_results.extend(filtered_results)
            
            # Remove duplicates and rank by relevance
            unique_results = self._deduplicate_results(all_results)
            ranked_results = self._rank_results(unique_results, subject, topic)
            
            # Return top results
            return ranked_results[:max_chunks]
            
        except Exception as e:
            logger.error(f"RAG retrieval failed for {subject} grade {grade_level}: {str(e)}")
            return []
    
    def _create_search_queries(
        self,
        subject: str,
        grade_level: int,
        topic: str
    ) -> List[RAGQuery]:
        """Create multiple search queries with different strategies."""
        
        queries = []
        
        # Primary query: exact topic match
        primary_query = RAGQuery(
            query_text=f"{topic} {subject} grade {grade_level}",
            subject=subject,
            grade_level=grade_level,
            topic=topic,
            max_results=3,
            similarity_threshold=0.7
        )
        queries.append(primary_query)
        
        # Secondary query: broader subject context
        secondary_query = RAGQuery(
            query_text=f"{subject} concepts grade {grade_level}",
            subject=subject,
            grade_level=grade_level,
            max_results=2,
            similarity_threshold=0.6
        )
        queries.append(secondary_query)
        
        # Tertiary query: topic without grade restriction (for flexibility)
        tertiary_query = RAGQuery(
            query_text=f"{topic} {subject}",
            subject=subject,
            grade_level=0,  # No grade filter
            max_results=2,
            similarity_threshold=0.65
        )
        queries.append(tertiary_query)
        
        return queries
    
    async def _filter_by_teacher_ownership(
        self,
        results: List[RAGResult],
        teacher_uid: str
    ) -> List[RAGResult]:
        """Filter results to only include documents owned by the teacher."""
        
        filtered_results = []
        
        for result in results:
            # Check if chunk belongs to teacher's documents
            chunk_teacher = result.chunk.metadata.get("teacher_uid")
            if chunk_teacher == teacher_uid:
                filtered_results.append(result)
        
        return filtered_results
    
    def _deduplicate_results(self, results: List[RAGResult]) -> List[RAGResult]:
        """Remove duplicate chunks and keep the one with highest similarity."""
        
        seen_chunks = {}
        
        for result in results:
            chunk_id = result.chunk.chunk_id
            
            if chunk_id not in seen_chunks or result.similarity_score > seen_chunks[chunk_id].similarity_score:
                seen_chunks[chunk_id] = result
        
        return list(seen_chunks.values())
    
    def _rank_results(
        self,
        results: List[RAGResult],
        subject: str,
        topic: str
    ) -> List[RAGResult]:
        """Rank results by relevance with custom scoring."""
        
        def calculate_relevance_score(result: RAGResult) -> float:
            score = result.similarity_score
            
            # Boost score for exact topic matches
            if topic.lower() in result.chunk.content.lower():
                score += 0.1
            
            # Boost score for exact subject matches in metadata
            if result.chunk.metadata.get("subject", "").lower() == subject.lower():
                score += 0.05
            
            # Penalty for very short chunks (less informative)
            if len(result.chunk.content) < 100:
                score -= 0.05
            
            return min(score, 1.0)  # Cap at 1.0
        
        # Calculate relevance scores and sort
        for result in results:
            result.similarity_score = calculate_relevance_score(result)
        
        return sorted(results, key=lambda x: x.similarity_score, reverse=True)
    
    async def get_context_summary(
        self,
        results: List[RAGResult]
    ) -> Dict[str, Any]:
        """Get a summary of the retrieved context."""
        
        if not results:
            return {
                "total_chunks": 0,
                "avg_similarity": 0.0,
                "sources": [],
                "content_length": 0
            }
        
        # Analyze sources
        sources = set()
        total_length = 0
        
        for result in results:
            filename = result.document_metadata.get("filename", "Unknown")
            sources.add(filename)
            total_length += len(result.chunk.content)
        
        avg_similarity = sum(r.similarity_score for r in results) / len(results)
        
        return {
            "total_chunks": len(results),
            "avg_similarity": round(avg_similarity, 3),
            "sources": list(sources),
            "content_length": total_length,
            "chunks_preview": [
                {
                    "chunk_id": r.chunk.chunk_id,
                    "content_preview": r.chunk.content[:100] + "..." if len(r.chunk.content) > 100 else r.chunk.content,
                    "similarity": round(r.similarity_score, 3),
                    "source": r.document_metadata.get("filename", "Unknown")
                }
                for r in results[:3]  # Show first 3 chunks
            ]
        }
    
    async def search_documents_by_content(
        self,
        search_text: str,
        teacher_uid: str,
        subject_filter: Optional[str] = None,
        grade_filter: Optional[int] = None,
        max_results: int = 10
    ) -> List[RAGResult]:
        """Search documents by content for teacher's content management."""
        
        try:
            query = RAGQuery(
                query_text=search_text,
                subject=subject_filter or "",
                grade_level=grade_filter or 0,
                max_results=max_results,
                similarity_threshold=0.5
            )
            
            results = await self.vector_service.search_similar_chunks(query)
            filtered_results = await self._filter_by_teacher_ownership(results, teacher_uid)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Content search failed: {str(e)}")
            return []
    
    async def get_teacher_content_stats(self, teacher_uid: str) -> Dict[str, Any]:
        """Get statistics about teacher's uploaded content."""
        
        try:
            # Get processed documents
            docs_ref = db.collection(self.processed_docs_collection)
            teacher_docs = docs_ref.where("teacher_uid", "==", teacher_uid).stream()
            
            doc_count = 0
            subjects = set()
            grades = set()
            total_chunks = 0
            
            for doc in teacher_docs:
                doc_data = doc.to_dict()
                doc_count += 1
                total_chunks += doc_data.get("total_chunks", 0)
                
                if doc_data.get("subject"):
                    subjects.add(doc_data["subject"])
                if doc_data.get("grade_level"):
                    grades.add(doc_data["grade_level"])
            
            return {
                "total_documents": doc_count,
                "total_chunks": total_chunks,
                "subjects": list(subjects),
                "grade_levels": sorted(list(grades)),
                "teacher_uid": teacher_uid
            }
            
        except Exception as e:
            logger.error(f"Failed to get teacher content stats: {str(e)}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "subjects": [],
                "grade_levels": [],
                "teacher_uid": teacher_uid
            }
