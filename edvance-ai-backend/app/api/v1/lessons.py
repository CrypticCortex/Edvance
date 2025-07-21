# FILE: app/api/v1/lessons.py

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional, List
import logging

from app.core.auth import get_current_user
from app.services.lesson_service import lesson_service

router = APIRouter(prefix="/lessons", tags=["lessons"])
logger = logging.getLogger(__name__)

# ====================================================================
# LESSON CREATION AND MANAGEMENT ENDPOINTS
# ====================================================================

@router.post("/create-from-step", response_model=Dict[str, Any])
async def create_lesson_from_learning_step(
    lesson_request: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new interactive lesson from a learning step.
    
    Expected request body:
    {
        "learning_step_id": "step_id",
        "student_id": "student_id",
        "customizations": {
            "difficulty_adjustment": "easier|normal|harder",
            "focus_areas": ["area1", "area2"],
            "learning_style": "visual|auditory|kinesthetic",
            "include_interactive": true,
            "slide_count_preference": "short|medium|long"
        }
    }
    """
    teacher_uid = current_user["uid"]
    
    try:
        learning_step_id = lesson_request.get("learning_step_id")
        student_id = lesson_request.get("student_id")
        customizations = lesson_request.get("customizations", {})
        
        if not learning_step_id or not student_id:
            raise HTTPException(
                status_code=400,
                detail="learning_step_id and student_id are required"
            )
        
        # Create lesson using the service
        result = await lesson_service.create_lesson_from_step(
            learning_step_id=learning_step_id,
            student_id=student_id,
            teacher_uid=teacher_uid,
            customizations=customizations
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create lesson: {result.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Created lesson {result['lesson_id']} for student {student_id}")
        
        return {
            "lesson_created": True,
            "lesson_id": result["lesson_id"],
            "lesson_details": {
                "title": result["lesson"]["title"],
                "total_slides": result["creation_details"]["total_slides"],
                "estimated_duration_minutes": result["creation_details"]["estimated_duration_minutes"],
                "learning_objectives": result["creation_details"]["learning_objectives"]
            },
            "progress": result["progress"],
            "next_actions": [
                "Student can start the lesson",
                "Teacher can monitor progress",
                "Chatbot is available for student questions"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create lesson from step: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lesson creation failed: {str(e)}"
        )

@router.get("/{lesson_id}", response_model=Dict[str, Any])
async def get_lesson_content(
    lesson_id: str,
    include_chat: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get lesson content and progress for a student.
    """
    try:
        # For students, they can only access their own lessons
        # For teachers, they can access lessons for their students
        user_role = current_user.get("role", "student")
        
        if user_role == "student":
            student_id = current_user["uid"]
        else:
            # Teacher access - would need to verify lesson ownership
            # For now, get student_id from query params or lesson data
            student_id = current_user.get("viewing_student_id", current_user["uid"])
        
        result = await lesson_service.get_student_lesson(
            lesson_id=lesson_id,
            student_id=student_id,
            include_chat_history=include_chat
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Lesson not found")
            )
        
        return {
            "lesson": result["lesson"],
            "progress": result["progress"],
            "chat_sessions": result.get("chat_sessions", []) if include_chat else [],
            "access_role": user_role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get lesson content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve lesson: {str(e)}"
        )

@router.get("/student/{student_id}", response_model=Dict[str, Any])
async def get_student_lessons(
    student_id: str,
    include_progress: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all lessons for a specific student.
    """
    teacher_uid = current_user["uid"]
    
    try:
        result = await lesson_service.get_student_lessons(
            student_id=student_id,
            teacher_uid=teacher_uid,
            include_progress=include_progress
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to retrieve lessons")
            )
        
        return {
            "student_id": student_id,
            "total_lessons": result["total_lessons"],
            "lessons": result["lessons"],
            "summary": {
                "completed_lessons": sum(1 for lesson in result["lessons"] 
                                       if lesson.get("progress", {}).get("completion_percentage", 0) >= 100),
                "in_progress_lessons": sum(1 for lesson in result["lessons"] 
                                         if 0 < lesson.get("progress", {}).get("completion_percentage", 0) < 100),
                "not_started_lessons": sum(1 for lesson in result["lessons"] 
                                         if lesson.get("progress", {}).get("completion_percentage", 0) == 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get student lessons: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve student lessons: {str(e)}"
        )

# ====================================================================
# LESSON PROGRESS AND INTERACTION ENDPOINTS
# ====================================================================

@router.post("/{lesson_id}/progress", response_model=Dict[str, Any])
async def update_lesson_progress(
    lesson_id: str,
    progress_update: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update student progress on a lesson slide.
    
    Expected request body:
    {
        "slide_id": "slide_id",
        "is_completed": true,
        "time_spent_minutes": 5,
        "responses": {
            "interactive_element_1": "answer",
            "quiz_response": "option_b"
        },
        "difficulty_feedback": "too_easy|just_right|too_hard",
        "understanding_level": 1-5
    }
    """
    student_id = current_user["uid"]
    
    try:
        slide_id = progress_update.get("slide_id")
        
        if not slide_id:
            raise HTTPException(
                status_code=400,
                detail="slide_id is required"
            )
        
        # Prepare progress data
        progress_data = {
            "is_completed": progress_update.get("is_completed", False),
            "time_spent_minutes": progress_update.get("time_spent_minutes", 0),
            "student_responses": progress_update.get("responses", {}),
            "difficulty_feedback": progress_update.get("difficulty_feedback"),
            "understanding_level": progress_update.get("understanding_level"),
            "completed_at": progress_update.get("completed_at"),
            "last_updated": progress_update.get("last_updated")
        }
        
        result = await lesson_service.update_slide_progress(
            lesson_id=lesson_id,
            student_id=student_id,
            slide_id=slide_id,
            progress_data=progress_data
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to update progress")
            )
        
        response = {
            "progress_updated": True,
            "slides_completed": result["slides_completed"],
            "completion_percentage": result["completion_percentage"],
            "lesson_completed": result["lesson_completed"]
        }
        
        # Add congratulations message if lesson completed
        if result["lesson_completed"]:
            response["congratulations"] = {
                "message": "🎉 Congratulations! You've completed this lesson!",
                "achievements": [
                    f"Completed {result['slides_completed']} slides",
                    "Gained new knowledge and skills",
                    "Ready for the next learning challenge"
                ]
            }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update lesson progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Progress update failed: {str(e)}"
        )

# ====================================================================
# LESSON CHATBOT ENDPOINTS
# ====================================================================

@router.post("/{lesson_id}/chat/start", response_model=Dict[str, Any])
async def start_lesson_chatbot(
    lesson_id: str,
    chat_request: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start a new chatbot session for a lesson.
    
    Expected request body:
    {
        "initial_message": "I need help with fractions"  // Optional
    }
    """
    student_id = current_user["uid"]
    
    try:
        initial_message = chat_request.get("initial_message")
        
        result = await lesson_service.start_lesson_chatbot(
            lesson_id=lesson_id,
            student_id=student_id,
            initial_message=initial_message
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to start chat session")
            )
        
        return {
            "chat_started": True,
            "session_id": result["session_id"],
            "messages": result["messages"],
            "chatbot_features": [
                "Ask questions about lesson content",
                "Get explanations and examples",
                "Receive hints for exercises",
                "Clarify difficult concepts"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start lesson chatbot: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat session start failed: {str(e)}"
        )

@router.post("/chat/{session_id}/message", response_model=Dict[str, Any])
async def send_chat_message(
    session_id: str,
    message_request: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a message to the lesson chatbot.
    
    Expected request body:
    {
        "message": "Can you explain this concept again?",
        "current_slide_id": "slide_123"  // Optional, for context
    }
    """
    student_id = current_user["uid"]
    
    try:
        message = message_request.get("message")
        current_slide_id = message_request.get("current_slide_id")
        
        if not message:
            raise HTTPException(
                status_code=400,
                detail="message is required"
            )
        
        result = await lesson_service.send_chatbot_message(
            session_id=session_id,
            student_id=student_id,
            message=message,
            current_slide_id=current_slide_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to send message")
            )
        
        return {
            "message_sent": True,
            "agent_response": result["agent_response"],
            "suggested_actions": result.get("suggested_actions", []),
            "conversation_active": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Message sending failed: {str(e)}"
        )

# ====================================================================
# LESSON ANALYTICS AND MANAGEMENT ENDPOINTS
# ====================================================================

@router.get("/{lesson_id}/analytics", response_model=Dict[str, Any])
async def get_lesson_analytics(
    lesson_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a lesson (teacher access).
    """
    teacher_uid = current_user["uid"]
    
    try:
        result = await lesson_service.get_lesson_analytics(
            lesson_id=lesson_id,
            teacher_uid=teacher_uid
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Lesson not found or access denied")
            )
        
        return {
            "lesson_id": lesson_id,
            "analytics": result["lesson_analytics"],
            "insights": {
                "performance_summary": _generate_performance_insights(result["lesson_analytics"]),
                "recommendations": _generate_lesson_recommendations(result["lesson_analytics"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get lesson analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analytics retrieval failed: {str(e)}"
        )

@router.post("/{lesson_id}/regenerate-slide", response_model=Dict[str, Any])
async def regenerate_lesson_slide(
    lesson_id: str,
    regeneration_request: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Regenerate a specific slide in a lesson based on feedback.
    
    Expected request body:
    {
        "slide_id": "slide_123",
        "student_id": "student_456",
        "reason": "too_difficult|too_easy|confusing|needs_more_examples",
        "specific_feedback": "Student struggled with the math problems"
    }
    """
    try:
        slide_id = regeneration_request.get("slide_id")
        student_id = regeneration_request.get("student_id")
        reason = regeneration_request.get("reason")
        specific_feedback = regeneration_request.get("specific_feedback", "")
        
        if not slide_id or not student_id or not reason:
            raise HTTPException(
                status_code=400,
                detail="slide_id, student_id, and reason are required"
            )
        
        # Combine reason and feedback
        regeneration_reason = f"{reason}: {specific_feedback}".strip(": ")
        
        result = await lesson_service.regenerate_lesson_slide(
            lesson_id=lesson_id,
            slide_id=slide_id,
            student_id=student_id,
            regeneration_reason=regeneration_reason
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to regenerate slide")
            )
        
        return {
            "slide_regenerated": True,
            "lesson_id": lesson_id,
            "slide_id": slide_id,
            "new_slide": result["new_slide"],
            "regenerated_at": result["regenerated_at"],
            "changes_made": [
                "Updated content based on feedback",
                "Adjusted difficulty level",
                "Enhanced explanations",
                "Improved interactive elements"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to regenerate lesson slide: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Slide regeneration failed: {str(e)}"
        )

# ====================================================================
# HELPER FUNCTIONS
# ====================================================================

def _generate_performance_insights(analytics: Dict[str, Any]) -> List[str]:
    """Generate performance insights from analytics data."""
    insights = []
    
    completion_rate = analytics.get("completion_rate", 0)
    success_rate = analytics.get("engagement_metrics", {}).get("success_rate", 0)
    chat_usage_rate = analytics.get("chat_analytics", {}).get("chat_usage_rate", 0)
    
    if completion_rate >= 80:
        insights.append("🎉 Excellent completion rate - students are engaging well with the lesson")
    elif completion_rate >= 60:
        insights.append("✅ Good completion rate - most students are finishing the lesson")
    else:
        insights.append("⚠️ Low completion rate - consider reviewing lesson difficulty or length")
    
    if success_rate >= 80:
        insights.append("💪 High success rate - students understand the concepts well")
    elif success_rate >= 60:
        insights.append("👍 Moderate success rate - some concepts may need reinforcement")
    else:
        insights.append("📚 Low success rate - consider adding more examples or simplifying content")
    
    if chat_usage_rate >= 50:
        insights.append("💬 High chatbot usage - students are actively seeking help")
    elif chat_usage_rate >= 25:
        insights.append("🤔 Moderate chatbot usage - some students using available support")
    else:
        insights.append("💡 Low chatbot usage - consider promoting the chatbot feature")
    
    return insights

def _generate_lesson_recommendations(analytics: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on analytics."""
    recommendations = []
    
    completion_rate = analytics.get("completion_rate", 0)
    success_rate = analytics.get("engagement_metrics", {}).get("success_rate", 0)
    
    if completion_rate < 60:
        recommendations.append("Consider shortening the lesson or breaking it into smaller parts")
        recommendations.append("Add more interactive elements to maintain engagement")
    
    if success_rate < 60:
        recommendations.append("Add more examples and practice exercises")
        recommendations.append("Consider regenerating difficult slides with simpler explanations")
    
    if analytics.get("chat_analytics", {}).get("total_questions", 0) > 0:
        recommendations.append("Review common questions to identify areas needing clearer explanation")
    
    if analytics.get("average_time_spent_minutes", 0) > 60:
        recommendations.append("Lesson may be too long - consider optimizing content length")
    
    return recommendations if recommendations else ["Lesson is performing well - no immediate changes needed"]
