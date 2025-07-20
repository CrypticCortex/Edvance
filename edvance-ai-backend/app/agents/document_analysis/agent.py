# FILE: app/agents/document_analysis/agent.py

from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List
import PyPDF2
import io
from PIL import Image
import pytesseract

from app.core.vertex import get_vertex_model

logger = logging.getLogger(__name__)

class DocumentAnalysisAgent:
    """Agent for analyzing document content and extracting metadata."""
    
    def __init__(self):
        self.model = get_vertex_model()
        
    async def analyze_document(
        self, 
        file_content: bytes, 
        filename: str, 
        file_type: str,
        subject: str,
        grade_level: int
    ) -> Dict[str, Any]:
        """
        Analyze document content and extract metadata.
        
        Args:
            file_content: The document file content as bytes
            filename: Original filename
            file_type: MIME type of the file
            subject: Subject category
            grade_level: Grade level provided by teacher
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract text content based on file type
            text_content = await self._extract_text_content(file_content, file_type)
            
            if not text_content or len(text_content.strip()) < 50:
                return {
                    "content_type": "unknown",
                    "topics": [],
                    "learning_objectives": [],
                    "difficulty_level": "unknown",
                    "key_vocabulary": [],
                    "text_preview": text_content[:200] if text_content else "",
                    "analysis_status": "insufficient_content"
                }
            
            # Use AI to analyze the content
            analysis = await self._ai_analyze_content(
                text_content, filename, subject, grade_level
            )
            
            return {
                **analysis,
                "text_preview": text_content[:500],
                "analysis_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze document {filename}: {e}")
            return {
                "content_type": "unknown",
                "topics": [],
                "learning_objectives": [],
                "difficulty_level": "unknown", 
                "key_vocabulary": [],
                "text_preview": "",
                "analysis_status": "failed",
                "error": str(e)
            }
    
    async def _extract_text_content(self, file_content: bytes, file_type: str) -> str:
        """Extract text content from different file types."""
        try:
            if file_type == "application/pdf":
                return await self._extract_pdf_text(file_content)
            elif file_type == "text/plain":
                return file_content.decode('utf-8')
            elif file_type.startswith("image/"):
                return await self._extract_image_text(file_content)
            else:
                logger.warning(f"Unsupported file type for text extraction: {file_type}")
                return ""
        except Exception as e:
            logger.error(f"Failed to extract text from {file_type}: {e}")
            return ""
    
    async def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF files."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            return ""
    
    async def _extract_image_text(self, file_content: bytes) -> str:
        """Extract text from images using OCR."""
        try:
            image = Image.open(io.BytesIO(file_content))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract image text: {e}")
            return ""
    
    async def _ai_analyze_content(
        self, 
        text_content: str, 
        filename: str, 
        subject: str, 
        grade_level: int
    ) -> Dict[str, Any]:
        """Use AI to analyze document content."""
        
        prompt = f"""Analyze this educational document and provide structured information:

DOCUMENT INFO:
- Filename: {filename}
- Subject: {subject}
- Grade Level: {grade_level}

DOCUMENT CONTENT:
{text_content[:3000]}  # Limit to avoid token limits

Please analyze and return ONLY a JSON object with these exact fields:
{{
    "content_type": "one of: worksheet, lesson_plan, assessment, quiz, homework, reading_material, activity, project, handout, other",
    "topics": ["list of 3-5 main topics covered"],
    "learning_objectives": ["list of 2-4 learning objectives the document addresses"],
    "difficulty_level": "one of: basic, intermediate, advanced",
    "key_vocabulary": ["list of 5-10 important terms or concepts"],
    "educational_value": "brief description of what students will learn"
}}

Focus on extracting concrete, actionable information that will help with personalized learning recommendations."""

        try:
            response = await self.model.generate_content_async(prompt)
            
            # Parse the JSON response
            import json
            analysis_text = response.text.strip()
            
            # Clean up the response if it has markdown formatting
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text[7:]
            if analysis_text.endswith("```"):
                analysis_text = analysis_text[:-3]
            
            analysis = json.loads(analysis_text.strip())
            
            # Validate required fields
            required_fields = ["content_type", "topics", "learning_objectives", "difficulty_level", "key_vocabulary"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = [] if field in ["topics", "learning_objectives", "key_vocabulary"] else "unknown"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to AI analyze content: {e}")
            return {
                "content_type": "unknown",
                "topics": [],
                "learning_objectives": [],
                "difficulty_level": "unknown",
                "key_vocabulary": [],
                "educational_value": "Analysis failed"
            }

# Global instance
document_analysis_agent = DocumentAnalysisAgent()
