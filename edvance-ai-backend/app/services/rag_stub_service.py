# FILE: app/services/rag_stub_service.py

import logging
from typing import List, Dict, Any, Optional

from app.models.rag_models import RAGQuery, RAGResult, DocumentChunk
from app.models.student import AssessmentConfig, Assessment, AssessmentQuestion

logger = logging.getLogger(__name__)

class RAGStubService:
    """Stub RAG service for when full RAG dependencies aren't available."""
    
    def __init__(self):
        self.is_rag_enabled = False
        logger.warning("Using RAG stub service - full RAG functionality not available")
    
    async def retrieve_context_for_assessment(
        self,
        subject: str,
        grade_level: int,
        topic: str,
        teacher_uid: str,
        max_chunks: int = 5
    ) -> List[RAGResult]:
        """Stub method - returns empty results."""
        logger.info(f"RAG stub: would retrieve context for {subject} grade {grade_level} topic {topic}")
        return []
    
    async def get_context_summary(self, results: List[RAGResult]) -> Dict[str, Any]:
        """Stub method for context summary."""
        return {
            "total_chunks": 0,
            "avg_similarity": 0.0,
            "sources": [],
            "content_length": 0,
            "message": "RAG not fully configured"
        }
    
    async def search_documents_by_content(
        self,
        search_text: str,
        teacher_uid: str,
        subject_filter: Optional[str] = None,
        grade_filter: Optional[int] = None,
        max_results: int = 10
    ) -> List[RAGResult]:
        """Stub method for content search."""
        logger.info(f"RAG stub: would search for '{search_text}' for teacher {teacher_uid}")
        return []
    
    async def get_teacher_content_stats(self, teacher_uid: str) -> Dict[str, Any]:
        """Stub method for teacher content stats."""
        return {
            "total_documents": 0,
            "total_chunks": 0,
            "subjects": [],
            "grade_levels": [],
            "teacher_uid": teacher_uid,
            "message": "RAG not fully configured"
        }
