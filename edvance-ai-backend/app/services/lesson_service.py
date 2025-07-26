# FILE: app/services/lesson_service.py

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.firebase import db
from app.models.lesson_models import (
    LessonContent, LessonSlide, LessonProgress, LessonChatSession
)
from app.models.learning_models import LearningStep
from app.agents.lesson_agent.agent import lesson_agent
from app.agents.tools.lesson_tools import (
    generate_lesson_content,
    get_lesson_content,
    update_lesson_progress,
    start_lesson_chat,
    send_chat_message
)
from app.core.language import SupportedLanguage, validate_language

logger = logging.getLogger(__name__)

class LessonService:
    """Service for managing lesson content generation and interaction."""
    
    def __init__(self):
        self.lessons_collection = "lessons"
        self.progress_collection = "lesson_progress"
        self.chats_collection = "lesson_chats"
        
    async def create_lesson_from_step(
        self,
        learning_step_id: str,
        student_id: str,
        teacher_uid: str,
        customizations: Optional[Dict[str, Any]] = None,
        language: str = "english"
    ) -> Dict[str, Any]:
        """
        Create a new lesson from a learning step.
        
        Args:
            learning_step_id: ID of the learning step
            student_id: Student the lesson is for
            teacher_uid: Teacher who owns the learning path
            customizations: Optional lesson customizations
            
        Returns:
            Dict containing lesson creation results
        """
        try:
            # Validate and normalize language
            validated_language = validate_language(language)
            logger.info(f"Creating lesson for step {learning_step_id}, student {student_id} in {validated_language}")
            
            # Add language to customizations
            if customizations is None:
                customizations = {}
            customizations["language"] = validated_language
            
            # Generate lesson content using the agent
            result = await generate_lesson_content(
                learning_step_id=learning_step_id,
                student_id=student_id,
                teacher_uid=teacher_uid,
                customizations=customizations
            )
            
            if not result.get("success"):
                return result
            
            # Get the complete lesson data
            lesson_data = await get_lesson_content(
                lesson_id=result["lesson_id"],
                student_id=student_id,
                include_progress=True
            )
            
            logger.info(f"Successfully created lesson {result['lesson_id']}")
            
            return {
                "success": True,
                "lesson_id": result["lesson_id"],
                "lesson": lesson_data.get("lesson"),
                "progress": lesson_data.get("progress"),
                "creation_details": {
                    "total_slides": result["total_slides"],
                    "estimated_duration_minutes": result["estimated_duration_minutes"],
                    "learning_objectives": result["learning_objectives"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create lesson from step: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_student_lesson(
        self,
        lesson_id: str,
        student_id: str,
        include_chat_history: bool = False
    ) -> Dict[str, Any]:
        """
        Get lesson content for a student.
        
        Args:
            lesson_id: ID of the lesson
            student_id: Student requesting the lesson
            include_chat_history: Whether to include chat history
            
        Returns:
            Dict containing lesson data
        """
        try:
            # Get lesson content with progress
            result = await get_lesson_content(
                lesson_id=lesson_id,
                student_id=student_id,
                include_progress=True
            )
            
            if not result.get("success"):
                return result
            
            response = {
                "success": True,
                "lesson": result["lesson"],
                "progress": result["progress"]
            }
            
            # Add chat history if requested
            if include_chat_history:
                chat_sessions = await self._get_lesson_chat_sessions(lesson_id, student_id)
                response["chat_sessions"] = chat_sessions
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get student lesson: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_slide_progress(
        self,
        lesson_id: str,
        student_id: str,
        slide_id: str,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update student progress on a lesson slide.
        
        Args:
            lesson_id: ID of the lesson
            student_id: Student ID
            slide_id: ID of the slide
            progress_data: Progress information
            
        Returns:
            Dict containing update results
        """
        try:
            result = await update_lesson_progress(
                lesson_id=lesson_id,
                student_id=student_id,
                slide_id=slide_id,
                progress_data=progress_data
            )
            
            # If lesson is completed, trigger any follow-up actions
            if result.get("lesson_completed"):
                await self._handle_lesson_completion(lesson_id, student_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update slide progress: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def start_lesson_chatbot(
        self,
        lesson_id: str,
        student_id: str,
        initial_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a chatbot session for a lesson.
        
        Args:
            lesson_id: ID of the lesson
            student_id: Student starting the chat
            initial_message: Optional initial message
            
        Returns:
            Dict containing chat session information
        """
        try:
            result = await start_lesson_chat(
                lesson_id=lesson_id,
                student_id=student_id,
                initial_message=initial_message
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to start lesson chatbot: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_chatbot_message(
        self,
        session_id: str,
        student_id: str,
        message: str,
        current_slide_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the lesson chatbot.
        
        Args:
            session_id: Chat session ID
            student_id: Student sending the message
            message: Student's message
            current_slide_id: Current slide student is viewing
            
        Returns:
            Dict containing chatbot response
        """
        try:
            result = await send_chat_message(
                session_id=session_id,
                student_id=student_id,
                message=message,
                current_slide_id=current_slide_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send chatbot message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_lesson_analytics(
        self,
        lesson_id: str,
        teacher_uid: str
    ) -> Dict[str, Any]:
        """
        Get analytics for a lesson.
        
        Args:
            lesson_id: ID of the lesson
            teacher_uid: Teacher requesting analytics
            
        Returns:
            Dict containing lesson analytics
        """
        try:
            # Get lesson data
            lesson_doc = db.collection(self.lessons_collection).document(lesson_id).get()
            
            if not lesson_doc.exists:
                return {"success": False, "error": "Lesson not found"}
            
            lesson_data = lesson_doc.to_dict()
            
            # Verify teacher access
            if lesson_data.get("teacher_uid") != teacher_uid:
                return {"success": False, "error": "Access denied"}
            
            # Get progress data for all students
            progress_docs = db.collection(self.progress_collection).where(
                "lesson_id", "==", lesson_id
            ).get()
            
            progress_data = [doc.to_dict() for doc in progress_docs]
            
            # Get chat data
            chat_docs = db.collection(self.chats_collection).where(
                "lesson_id", "==", lesson_id
            ).get()
            
            chat_data = [doc.to_dict() for doc in chat_docs]
            
            # Calculate analytics
            analytics = self._calculate_lesson_analytics(lesson_data, progress_data, chat_data)
            
            return {
                "success": True,
                "lesson_analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"Failed to get lesson analytics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_student_lessons(
        self,
        student_id: str,
        teacher_uid: str,
        include_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Get all lessons for a student.
        
        Args:
            student_id: Student ID
            teacher_uid: Teacher UID for access control
            include_progress: Whether to include progress data
            
        Returns:
            Dict containing student's lessons
        """
        try:
            # Get lessons for the student
            lessons_docs = db.collection(self.lessons_collection).where(
                "student_id", "==", student_id
            ).where(
                "teacher_uid", "==", teacher_uid
            ).order_by("created_at", direction="DESCENDING").get()
            
            lessons = []
            
            for lesson_doc in lessons_docs:
                lesson_data = lesson_doc.to_dict()
                
                lesson_info = {
                    "lesson_id": lesson_data["lesson_id"],
                    "title": lesson_data["title"],
                    "topic": lesson_data["topic"],
                    "subject": lesson_data["subject"],
                    "total_slides": lesson_data["total_slides"],
                    "created_at": lesson_data["created_at"]
                }
                
                # Add progress if requested
                if include_progress:
                    progress = await self._get_lesson_progress_summary(
                        lesson_data["lesson_id"], student_id
                    )
                    lesson_info["progress"] = progress
                
                lessons.append(lesson_info)
            
            return {
                "success": True,
                "student_id": student_id,
                "total_lessons": len(lessons),
                "lessons": lessons
            }
            
        except Exception as e:
            logger.error(f"Failed to get student lessons: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def regenerate_lesson_slide(
        self,
        lesson_id: str,
        slide_id: str,
        student_id: str,
        regeneration_reason: str
    ) -> Dict[str, Any]:
        """
        Regenerate a specific slide in a lesson.
        
        Args:
            lesson_id: ID of the lesson
            slide_id: ID of the slide to regenerate
            student_id: Student ID for personalization
            regeneration_reason: Reason for regeneration
            
        Returns:
            Dict containing regeneration results
        """
        try:
            # Get current lesson
            lesson_doc = db.collection(self.lessons_collection).document(lesson_id).get()
            
            if not lesson_doc.exists:
                return {"success": False, "error": "Lesson not found"}
            
            lesson_data = lesson_doc.to_dict()
            
            # Find the slide to regenerate
            slides = lesson_data.get("slides", [])
            slide_to_regenerate = None
            slide_index = -1
            
            for i, slide in enumerate(slides):
                if slide.get("slide_id") == slide_id:
                    slide_to_regenerate = slide
                    slide_index = i
                    break
            
            if not slide_to_regenerate:
                return {"success": False, "error": "Slide not found"}
            
            # Get student context for personalization
            student_context = await self._get_student_context_for_regeneration(
                student_id, lesson_id, regeneration_reason
            )
            
            # Regenerate slide using AI
            from app.agents.tools.lesson_tools import generate_slide_content
            
            new_slide_result = await generate_slide_content(
                slide_type=slide_to_regenerate.get("slide_type", "concept_explanation"),
                topic=lesson_data.get("topic", ""),
                learning_objective=slide_to_regenerate.get("learning_objective", ""),
                grade_level=lesson_data.get("grade_level", 5),
                student_context=student_context
            )
            
            if not new_slide_result.get("success"):
                return new_slide_result
            
            # Update the slide in the lesson
            new_slide_data = new_slide_result["slide_content"]
            new_slide_data["slide_id"] = slide_id  # Keep the same ID
            new_slide_data["slide_number"] = slide_to_regenerate["slide_number"]
            new_slide_data["regenerated_at"] = datetime.utcnow()
            new_slide_data["regeneration_reason"] = regeneration_reason
            
            slides[slide_index] = new_slide_data
            
            # Update lesson in database
            db.collection(self.lessons_collection).document(lesson_id).update({
                "slides": slides,
                "last_updated": datetime.utcnow()
            })
            
            logger.info(f"Regenerated slide {slide_id} in lesson {lesson_id}")
            
            return {
                "success": True,
                "lesson_id": lesson_id,
                "slide_id": slide_id,
                "new_slide": new_slide_data,
                "regenerated_at": new_slide_data["regenerated_at"]
            }
            
        except Exception as e:
            logger.error(f"Failed to regenerate lesson slide: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Helper methods
    
    async def _get_lesson_chat_sessions(self, lesson_id: str, student_id: str) -> List[Dict[str, Any]]:
        """Get chat sessions for a lesson."""
        try:
            chat_docs = db.collection(self.chats_collection).where(
                "lesson_id", "==", lesson_id
            ).where(
                "student_id", "==", student_id
            ).order_by("started_at", direction="DESCENDING").get()
            
            return [doc.to_dict() for doc in chat_docs]
        except Exception as e:
            logger.error(f"Failed to get chat sessions: {str(e)}")
            return []
    
    async def _handle_lesson_completion(self, lesson_id: str, student_id: str) -> None:
        """Handle lesson completion events."""
        try:
            # Log completion
            completion_log = {
                "lesson_id": lesson_id,
                "student_id": student_id,
                "completed_at": datetime.utcnow(),
                "completion_type": "automatic"
            }
            
            db.collection("lesson_completions").add(completion_log)
            
            # Could trigger follow-up actions like:
            # - Generating next lesson
            # - Updating learning path progress
            # - Sending notifications
            
            logger.info(f"Lesson {lesson_id} completed by student {student_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle lesson completion: {str(e)}")
    
    def _calculate_lesson_analytics(
        self,
        lesson_data: Dict[str, Any],
        progress_data: List[Dict[str, Any]],
        chat_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate analytics for a lesson."""
        try:
            total_students = len(progress_data)
            
            if total_students == 0:
                return {
                    "total_students": 0,
                    "completion_rate": 0,
                    "average_time_spent": 0,
                    "engagement_metrics": {},
                    "chat_analytics": {}
                }
            
            # Calculate completion metrics
            completed_lessons = sum(1 for p in progress_data if p.get("completion_percentage", 0) >= 100)
            completion_rate = (completed_lessons / total_students) * 100
            
            # Calculate time metrics
            total_time = sum(p.get("time_spent_minutes", 0) for p in progress_data)
            average_time = total_time / total_students if total_students > 0 else 0
            
            # Calculate engagement metrics
            total_interactions = sum(p.get("interactions_count", 0) for p in progress_data)
            total_correct = sum(p.get("correct_responses", 0) for p in progress_data)
            total_responses = sum(p.get("total_responses", 0) for p in progress_data)
            
            success_rate = (total_correct / total_responses) * 100 if total_responses > 0 else 0
            
            # Calculate chat analytics
            total_chat_sessions = len(chat_data)
            total_messages = sum(chat.get("total_messages", 0) for chat in chat_data)
            total_questions = sum(chat.get("student_questions", 0) for chat in chat_data)
            
            return {
                "total_students": total_students,
                "completion_rate": round(completion_rate, 2),
                "average_time_spent_minutes": round(average_time, 2),
                "engagement_metrics": {
                    "total_interactions": total_interactions,
                    "success_rate": round(success_rate, 2),
                    "average_interactions_per_student": round(total_interactions / total_students, 2)
                },
                "chat_analytics": {
                    "total_sessions": total_chat_sessions,
                    "total_messages": total_messages,
                    "total_questions": total_questions,
                    "chat_usage_rate": round((total_chat_sessions / total_students) * 100, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate lesson analytics: {str(e)}")
            return {}
    
    async def _get_lesson_progress_summary(self, lesson_id: str, student_id: str) -> Dict[str, Any]:
        """Get progress summary for a lesson."""
        try:
            progress_docs = db.collection(self.progress_collection).where(
                "lesson_id", "==", lesson_id
            ).where(
                "student_id", "==", student_id
            ).limit(1).get()
            
            if not progress_docs:
                return {
                    "completion_percentage": 0,
                    "slides_completed": 0,
                    "time_spent_minutes": 0,
                    "last_activity": None
                }
            
            progress_data = progress_docs[0].to_dict()
            
            return {
                "completion_percentage": progress_data.get("completion_percentage", 0),
                "slides_completed": progress_data.get("slides_completed", 0),
                "time_spent_minutes": progress_data.get("time_spent_minutes", 0),
                "last_activity": progress_data.get("last_updated"),
                "started_at": progress_data.get("started_at")
            }
            
        except Exception as e:
            logger.error(f"Failed to get lesson progress summary: {str(e)}")
            return {}
    
    async def _get_student_context_for_regeneration(
        self,
        student_id: str,
        lesson_id: str,
        regeneration_reason: str
    ) -> Dict[str, Any]:
        """Get student context for slide regeneration."""
        try:
            # Get current progress
            progress = await self._get_lesson_progress_summary(lesson_id, student_id)
            
            # Get recent performance
            # This could be enhanced with more sophisticated analysis
            
            context = {
                "student_id": student_id,
                "current_progress": progress,
                "regeneration_reason": regeneration_reason,
                "needs_simplification": "struggling" in regeneration_reason.lower(),
                "needs_enhancement": "too_easy" in regeneration_reason.lower()
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get student context for regeneration: {str(e)}")
            return {}

# Global instance
lesson_service = LessonService()
