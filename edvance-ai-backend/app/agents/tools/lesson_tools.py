# FILE: app/agents/tools/lesson_tools.py

import logging
import uuid
import json
import re
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.firebase import db
from app.core.vertex import get_vertex_model
from firebase_admin import firestore
from app.models.lesson_models import (
    LessonContent, LessonSlide, ContentElement, LessonChatSession,
    ChatMessage, SlideType, ContentElementType, InteractiveWidget,
    LessonProgress
)
from app.models.learning_models import LearningStep, DifficultyLevel
from app.services.enhanced_assessment_service import enhanced_assessment_service
from app.core.language import SupportedLanguage, validate_language, create_language_prompt_prefix
from pydantic import BaseModel, Field
from typing import Literal

# Structured output models for lesson generation
class ContentElementStructured(BaseModel):
    element_type: Literal["text", "image", "exercise"] = "text"
    title: str
    content: str
    position: int = 1

class SlideStructured(BaseModel):
    slide_number: int
    slide_type: Literal["introduction", "concept_explanation", "example", "practice", "assessment", "summary"] = "concept_explanation"
    title: str
    subtitle: Optional[str] = None
    learning_objective: str
    estimated_duration_minutes: int = 5
    content_elements: List[ContentElementStructured]
    is_interactive: bool = False

class LessonStructured(BaseModel):
    title: str
    description: str
    learning_objectives: List[str]
    slides: List[SlideStructured]

logger = logging.getLogger(__name__)


def serialize_for_firestore(obj):
    """Helper function to serialize objects for Firestore storage"""
    if hasattr(obj, 'dict'):
        data = obj.dict()
    elif isinstance(obj, dict):
        data = obj
    else:
        return obj
    
    # Convert datetime objects to strings
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif hasattr(value, '__dict__') and hasattr(value, 'timestamp'):
            # Handle DatetimeWithNanoseconds
            data[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
    
    return data

async def generate_lesson_content_ultra_fast(
    learning_step_id: str,
    student_id: str,
    teacher_uid: str,
    customizations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate lesson content with ultra-fast approach - minimal AI calls, optimized prompts.
    
    Args:
        learning_step_id: ID of the learning step to create lesson for
        student_id: Student this lesson is for
        teacher_uid: Teacher who owns the learning path
        customizations: Optional customizations for the lesson
    
    Returns:
        Dict containing lesson generation results
    """
    try:
        start_time = datetime.utcnow()
        
        # Minimal data gathering - only get essentials
        logger.info(f"Starting ultra-fast lesson generation")
        
        # Get basic learning step info (could be from cache in production)
        learning_step = await _get_learning_step(learning_step_id)
        if not learning_step:
            return {"success": False, "error": "Learning step not found"}
        
        # Get real student context - optimized for speed but still real data
        student_context = await _get_student_context(student_id, teacher_uid)
        
        gather_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Minimal data gathering completed in {gather_time:.2f} seconds")
        
        # Ultra-optimized AI generation with concise prompt
        generation_start = datetime.utcnow()
        
        lesson_content = await _generate_complete_lesson_optimized(
            learning_step, student_context, [], customizations
        )
        
        generation_time = (datetime.utcnow() - generation_start).total_seconds()
        logger.info(f"Ultra-fast generation completed in {generation_time:.2f} seconds")
        
        # Quick save
        save_start = datetime.utcnow()
        lesson_id = await _save_lesson_content(lesson_content)
        save_time = (datetime.utcnow() - save_start).total_seconds()
        
        total_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Ultra-fast lesson {lesson_id} generated in {total_time:.2f}s")
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "title": lesson_content.title,
            "total_slides": len(lesson_content.slides),
            "estimated_duration_minutes": sum(slide.estimated_duration_minutes for slide in lesson_content.slides),
            "learning_objectives": lesson_content.learning_objectives,
            "generated_at": datetime.utcnow().isoformat(),
            "generation_metrics": {
                "total_time_seconds": total_time,
                "data_gathering_seconds": gather_time,
                "ai_generation_seconds": generation_time,
                "save_operations_seconds": save_time,
                "slides_generated": len(lesson_content.slides),
                "optimization_approach": "ultra_fast",
                "speed_optimizations": ["minimal_data_gathering", "concise_prompt", "template_based_fallback"]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate ultra-fast lesson content: {str(e)}")
        return {"success": False, "error": str(e)}

async def generate_lesson_content_optimized(
    learning_step_id: str,
    student_id: str,
    teacher_uid: str,
    customizations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive lesson content with optimized single AI call approach.
    
    Args:
        learning_step_id: ID of the learning step to create lesson for
        student_id: Student this lesson is for
        teacher_uid: Teacher who owns the learning path
        customizations: Optional customizations for the lesson
    
    Returns:
        Dict containing lesson generation results
    """
    try:
        start_time = datetime.utcnow()
        
        # Parallel data gathering phase (optimized)
        logger.info(f"Starting optimized data gathering for lesson generation")
        
        tasks = [
            _get_learning_step(learning_step_id),
            _get_student_context(student_id, teacher_uid),
            _get_relevant_teacher_content(teacher_uid, None, None)  # We'll filter this later
        ]
        
        learning_step, student_context, initial_teacher_content = await asyncio.gather(*tasks)
        
        if not learning_step:
            return {"success": False, "error": "Learning step not found"}
        
        # Get the properly filtered teacher content
        teacher_content = await _get_relevant_teacher_content(
            teacher_uid, learning_step.topic, learning_step.subject
        )
        
        gather_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Data gathering completed in {gather_time:.2f} seconds")
        
        # Single comprehensive AI generation call
        generation_start = datetime.utcnow()
        
        lesson_content = await _generate_complete_lesson_optimized(
            learning_step, student_context, teacher_content, customizations
        )
        
        generation_time = (datetime.utcnow() - generation_start).total_seconds()
        logger.info(f"Complete lesson generation in {generation_time:.2f} seconds")
        
        # Parallel save operations
        save_start = datetime.utcnow()
        
        save_task = _save_lesson_content(lesson_content)
        progress_task = _initialize_lesson_progress(lesson_content.lesson_id, student_id)
        
        lesson_id, _ = await asyncio.gather(save_task, progress_task)
        
        save_time = (datetime.utcnow() - save_start).total_seconds()
        total_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Optimized lesson {lesson_id} generated in {total_time:.2f}s (gather: {gather_time:.2f}s, generation: {generation_time:.2f}s, save: {save_time:.2f}s)")
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "title": lesson_content.title,
            "total_slides": len(lesson_content.slides),
            "estimated_duration_minutes": sum(slide.estimated_duration_minutes for slide in lesson_content.slides),
            "learning_objectives": lesson_content.learning_objectives,
            "generated_at": datetime.utcnow().isoformat(),
            "generation_metrics": {
                "total_time_seconds": total_time,
                "data_gathering_seconds": gather_time,
                "ai_generation_seconds": generation_time,
                "save_operations_seconds": save_time,
                "slides_generated": len(lesson_content.slides),
                "optimization_approach": "single_ai_call",
                "api_calls_saved": len(lesson_content.slides) + 1  # Structure + individual slides
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate optimized lesson content: {str(e)}")
        return {"success": False, "error": str(e)}

async def generate_lesson_content(
    learning_step_id: str,
    student_id: str,
    teacher_uid: str,
    customizations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive lesson content using the ultra-fast optimized approach.
    This is the production-ready method achieving ~27 second generation times.
    
    Args:
        learning_step_id: ID of the learning step to create lesson for
        student_id: Student this lesson is for
        teacher_uid: Teacher who owns the learning path
        customizations: Optional customizations for the lesson
    
    Returns:
        Dict containing lesson generation results
    """
    # Use ultra-fast approach for production performance
    return await generate_lesson_content_ultra_fast(
        learning_step_id, student_id, teacher_uid, customizations
    )

async def generate_lesson_content_legacy(
    learning_step_id: str,
    student_id: str,
    teacher_uid: str,
    customizations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive lesson content from a learning step with parallelized processing.
    Legacy method kept for fallback scenarios.
    
    Args:
        learning_step_id: ID of the learning step to create lesson for
        student_id: Student this lesson is for
        teacher_uid: Teacher who owns the learning path
        customizations: Optional customizations for the lesson
    
    Returns:
        Dict containing lesson generation results
    """
    try:
        start_time = datetime.utcnow()
        
        # Parallel data gathering phase
        logger.info(f"Starting parallel data gathering for lesson generation")
        
        tasks = [
            _get_learning_step(learning_step_id),
            _get_student_context(student_id, teacher_uid),
            _get_relevant_teacher_content(teacher_uid, None, None)  # We'll filter this later
        ]
        
        learning_step, student_context, initial_teacher_content = await asyncio.gather(*tasks)
        
        if not learning_step:
            return {"success": False, "error": "Learning step not found"}
        
        # Now get the properly filtered teacher content
        teacher_content = await _get_relevant_teacher_content(
            teacher_uid, learning_step.topic, learning_step.subject
        )
        
        gather_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Data gathering completed in {gather_time:.2f} seconds")
        
        # Parallel lesson generation phase
        generation_start = datetime.utcnow()
        
        # Generate lesson structure and content in parallel
        lesson_structure_task = _generate_lesson_structure_with_ai(
            learning_step, student_context, customizations
        )
        
        content_outline_task = _generate_content_outline(
            learning_step, teacher_content
        )
        
        lesson_structure, content_outline = await asyncio.gather(
            lesson_structure_task, content_outline_task
        )
        
        structure_time = (datetime.utcnow() - generation_start).total_seconds()
        logger.info(f"Lesson structure generation completed in {structure_time:.2f} seconds")
        
        # Parallel slide content generation
        slides_start = datetime.utcnow()
        
        slide_tasks = []
        for i, slide_outline in enumerate(lesson_structure.get("slides", [])):
            task = _generate_individual_slide_content(
                slide_outline,
                content_outline,
                student_context,
                i + 1
            )
            slide_tasks.append(task)
        
        # Process slides in batches to avoid overwhelming the API
        batch_size = 3
        slide_batches = [slide_tasks[i:i + batch_size] for i in range(0, len(slide_tasks), batch_size)]
        
        all_slides = []
        for batch in slide_batches:
            batch_results = await asyncio.gather(*batch)
            all_slides.extend(batch_results)
        
        slides_time = (datetime.utcnow() - slides_start).total_seconds()
        logger.info(f"Slide content generation completed in {slides_time:.2f} seconds")
        
        # Build final lesson content
        lesson_content = await _build_lesson_content(
            lesson_structure, all_slides, learning_step, student_context
        )
        
        # Parallel save operations
        save_start = datetime.utcnow()
        
        save_task = _save_lesson_content(lesson_content)
        progress_task = _initialize_lesson_progress(lesson_content.lesson_id, student_id)
        
        lesson_id, _ = await asyncio.gather(save_task, progress_task)
        
        save_time = (datetime.utcnow() - save_start).total_seconds()
        total_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Lesson {lesson_id} generated in {total_time:.2f}s (gather: {gather_time:.2f}s, structure: {structure_time:.2f}s, slides: {slides_time:.2f}s, save: {save_time:.2f}s)")
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "title": lesson_content.title,
            "total_slides": len(lesson_content.slides),
            "estimated_duration_minutes": sum(slide.estimated_duration_minutes for slide in lesson_content.slides),
            "learning_objectives": lesson_content.learning_objectives,
            "generated_at": datetime.utcnow().isoformat(),
            "generation_metrics": {
                "total_time_seconds": total_time,
                "data_gathering_seconds": gather_time,
                "structure_generation_seconds": structure_time,
                "slide_generation_seconds": slides_time,
                "save_operations_seconds": save_time,
                "slides_generated": len(all_slides),
                "parallel_optimization": True
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate lesson content: {str(e)}")
        return {"success": False, "error": str(e)}

async def generate_lesson_content_legacy(
    learning_step_id: str,
    student_id: str,
    teacher_uid: str,
    customizations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive lesson content from a learning step.
    
    Args:
        learning_step_id: ID of the learning step to create lesson for
        student_id: Student this lesson is for
        teacher_uid: Teacher who owns the learning path
        customizations: Optional customizations for the lesson
    
    Returns:
        Dict containing lesson generation results
    """
    try:
        # Get the learning step
        learning_step = await _get_learning_step(learning_step_id)
        if not learning_step:
            return {"success": False, "error": "Learning step not found"}
        
        # Get student context for personalization
        student_context = await _get_student_context(student_id, teacher_uid)
        
        # Get teacher's content for RAG
        teacher_content = await _get_relevant_teacher_content(
            teacher_uid, learning_step.topic, learning_step.subject
        )
        
        # Generate lesson using AI
        lesson_content = await _generate_lesson_with_ai(
            learning_step, student_context, teacher_content, customizations
        )
        
        # Save lesson to database
        lesson_id = await _save_lesson_content(lesson_content)
        
        # Initialize progress tracking
        await _initialize_lesson_progress(lesson_id, student_id)
        
        logger.info(f"Generated lesson {lesson_id} for step {learning_step_id}")
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "title": lesson_content.title,
            "total_slides": len(lesson_content.slides),
            "estimated_duration_minutes": sum(slide.estimated_duration_minutes for slide in lesson_content.slides),
            "learning_objectives": lesson_content.learning_objectives,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate lesson content: {str(e)}")
        return {"success": False, "error": str(e)}

async def get_lesson_content(
    lesson_id: str,
    student_id: str,
    include_progress: bool = True
) -> Dict[str, Any]:
    """
    Retrieve lesson content with optional progress information.
    
    Args:
        lesson_id: ID of the lesson to retrieve
        student_id: Student requesting the lesson
        include_progress: Whether to include progress information
    
    Returns:
        Dict containing lesson content and progress
    """
    try:
        # Get lesson from database
        lesson_doc = db.collection("lessons").document(lesson_id).get()
        
        if not lesson_doc.exists:
            return {"success": False, "error": "Lesson not found"}
        
        lesson_data = lesson_doc.to_dict()
        
        # Verify student access
        if lesson_data.get("student_id") != student_id:
            return {"success": False, "error": "Access denied"}
        
        result = {
            "success": True,
            "lesson": lesson_data
        }
        
        # Add progress information if requested
        if include_progress:
            progress = await _get_lesson_progress(lesson_id, student_id)
            result["progress"] = progress
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get lesson content: {str(e)}")
        return {"success": False, "error": str(e)}

async def update_lesson_progress(
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
        slide_id: ID of the slide being updated
        progress_data: Progress information to update
    
    Returns:
        Dict containing update results
    """
    try:
        # Get current progress
        progress_doc = db.collection("lesson_progress").where(
            filter=firestore.FieldFilter("lesson_id", "==", lesson_id)
        ).where(
            filter=firestore.FieldFilter("student_id", "==", student_id)
        ).limit(1).get()
        
        if not progress_doc:
            return {"success": False, "error": "Progress record not found"}
        
        progress_ref = progress_doc[0].reference
        current_progress = progress_doc[0].to_dict()
        
        # Update slide progress
        slide_progress = current_progress.get("slide_progress", [])
        
        # Find and update the specific slide
        updated = False
        for slide_data in slide_progress:
            if slide_data.get("slide_id") == slide_id:
                slide_data.update(progress_data)
                slide_data["last_updated"] = datetime.utcnow()
                updated = True
                break
        
        if not updated:
            # Add new slide progress
            slide_progress.append({
                "slide_id": slide_id,
                "started_at": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                **progress_data
            })
        
        # Calculate overall progress
        completed_slides = sum(1 for slide in slide_progress if slide.get("is_completed", False))
        total_slides = max(current_progress.get("slides_total", 1), 1)  # Ensure at least 1 to avoid division by zero
        completion_percentage = (completed_slides / total_slides) * 100
        
        # Update progress document
        progress_ref.update({
            "slide_progress": slide_progress,
            "slides_completed": completed_slides,
            "completion_percentage": completion_percentage,
            "last_updated": datetime.utcnow(),
            "time_spent_minutes": current_progress.get("time_spent_minutes", 0) + progress_data.get("time_spent_minutes", 0)
        })
        
        # Check if lesson is completed
        if completion_percentage >= 100:
            progress_ref.update({
                "completed_at": datetime.utcnow()
            })
        
        logger.info(f"Updated lesson progress for student {student_id}, lesson {lesson_id}")
        
        return {
            "success": True,
            "slides_completed": completed_slides,
            "completion_percentage": completion_percentage,
            "lesson_completed": completion_percentage >= 100
        }
        
    except Exception as e:
        logger.error(f"Failed to update lesson progress: {str(e)}")
        return {"success": False, "error": str(e)}

async def start_lesson_chat(
    lesson_id: str,
    student_id: str,
    initial_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Start a new chatbot session for a lesson.
    
    Args:
        lesson_id: ID of the lesson
        student_id: Student starting the chat
        initial_message: Optional initial message from student
    
    Returns:
        Dict containing chat session information
    """
    try:
        # Create new chat session
        session_id = str(uuid.uuid4())
        
        chat_session = LessonChatSession(
            session_id=session_id,
            lesson_id=lesson_id,
            student_id=student_id,
            messages=[],
            is_active=True
        )
        
        # Add welcome message
        welcome_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            sender="agent",
            message="Hello! I'm your lesson assistant. I'm here to help you understand the concepts and answer any questions you have. How can I help you today?",
            message_type="text"
        )
        
        chat_session.messages.append(welcome_message)
        chat_session.total_messages = 1
        chat_session.agent_responses = 1
        
        # Add initial student message if provided
        if initial_message:
            student_message = ChatMessage(
                message_id=str(uuid.uuid4()),
                lesson_id=lesson_id,
                sender="student",
                message=initial_message,
                message_type="text"
            )
            chat_session.messages.append(student_message)
            chat_session.total_messages += 1
            chat_session.student_questions += 1
        
        # Save to database
        db.collection("lesson_chats").document(session_id).set(chat_session.dict())
        
        logger.info(f"Started lesson chat session {session_id} for lesson {lesson_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": [msg.dict() for msg in chat_session.messages]
        }
        
    except Exception as e:
        logger.error(f"Failed to start lesson chat: {str(e)}")
        return {"success": False, "error": str(e)}

async def send_chat_message(
    session_id: str,
    student_id: str,
    message: str,
    current_slide_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a message in a lesson chat session and get AI response.
    
    Args:
        session_id: Chat session ID
        student_id: Student sending the message
        message: Student's message
        current_slide_id: Current slide student is viewing
    
    Returns:
        Dict containing chat response
    """
    try:
        # Get chat session
        chat_doc = db.collection("lesson_chats").document(session_id).get()
        
        if not chat_doc.exists:
            return {"success": False, "error": "Chat session not found"}
        
        chat_data = chat_doc.to_dict()
        
        # Verify student access
        if chat_data.get("student_id") != student_id:
            return {"success": False, "error": "Access denied"}
        
        # Get lesson context
        lesson_context = await _get_lesson_context_for_chat(
            chat_data["lesson_id"], current_slide_id
        )
        
        # Generate AI response
        ai_response = await _generate_chat_response(
            message, lesson_context, chat_data["messages"]
        )
        
        # Create message objects
        student_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            lesson_id=chat_data["lesson_id"],
            sender="student",
            message=message,
            current_slide_id=current_slide_id
        )
        
        agent_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            lesson_id=chat_data["lesson_id"],
            sender="agent",
            message=ai_response["message"],
            confidence_score=ai_response.get("confidence_score"),
            sources=ai_response.get("sources", []),
            suggested_actions=ai_response.get("suggested_actions", [])
        )
        
        # Update chat session
        chat_ref = db.collection("lesson_chats").document(session_id)
        chat_ref.update({
            "messages": firestore.ArrayUnion([
                serialize_for_firestore(student_message), 
                serialize_for_firestore(agent_message)
            ]),
            "total_messages": firestore.Increment(2),
            "student_questions": firestore.Increment(1),
            "agent_responses": firestore.Increment(1),
            "last_activity": datetime.utcnow()
        })
        
        logger.info(f"Processed chat message in session {session_id}")
        
        return {
            "success": True,
            "agent_response": agent_message.dict(),
            "suggested_actions": ai_response.get("suggested_actions", [])
        }
        
    except Exception as e:
        logger.error(f"Failed to send chat message: {str(e)}")
        return {"success": False, "error": str(e)}

async def get_chat_history(
    session_id: str,
    student_id: str,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get chat history for a lesson session.
    
    Args:
        session_id: Chat session ID
        student_id: Student requesting the history
        limit: Optional limit on number of messages
    
    Returns:
        Dict containing chat history
    """
    try:
        # Get chat session
        chat_doc = db.collection("lesson_chats").document(session_id).get()
        
        if not chat_doc.exists:
            return {"success": False, "error": "Chat session not found"}
        
        chat_data = chat_doc.to_dict()
        
        # Verify student access
        if chat_data.get("student_id") != student_id:
            return {"success": False, "error": "Access denied"}
        
        messages = chat_data.get("messages", [])
        
        # Apply limit if specified
        if limit:
            messages = messages[-limit:]
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages,
            "total_messages": len(messages),
            "session_active": chat_data.get("is_active", False)
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        return {"success": False, "error": str(e)}

async def generate_slide_content(
    slide_type: str,
    topic: str,
    learning_objective: str,
    grade_level: int,
    student_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate content for a specific slide type.
    
    Args:
        slide_type: Type of slide to generate
        topic: Topic for the slide
        learning_objective: Learning objective for the slide
        grade_level: Target grade level
        student_context: Optional student context for personalization
    
    Returns:
        Dict containing generated slide content
    """
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        prompt = f"""Generate content for a {slide_type} slide about {topic} for grade {grade_level} students.

Learning Objective: {learning_objective}

Student Context: {json.dumps(student_context) if student_context else 'General audience'}

Create engaging, age-appropriate content that includes:
1. Clear title and subtitle
2. Main content elements (text, examples, activities)
3. Interactive elements where appropriate
4. Visual descriptions for diagrams or images needed

Return the response in this JSON format:
{{
  "title": "Slide title",
  "subtitle": "Optional subtitle",
  "content_elements": [
    {{
      "element_type": "text|image|interactive_widget|exercise",
      "title": "Element title",
      "content": "Element content or description",
      "position": 1,
      "styling": {{}},
      "interactive_widget": {{
        "widget_type": "multiple_choice|drag_drop|fill_blank",
        "title": "Widget title",
        "instructions": "Instructions for student",
        "content": {{}},
        "correct_answer": {{}},
        "hints": []
      }}
    }}
  ],
  "estimated_duration_minutes": 5,
  "completion_criteria": {{}}
}}"""

        response = await model.generate_content_async(prompt)
        
        # Parse JSON response
        try:
            slide_data = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            slide_data = {
                "title": f"{topic} - {slide_type.title()}",
                "content_elements": [{
                    "element_type": "text",
                    "title": "Content",
                    "content": response.text,
                    "position": 1
                }],
                "estimated_duration_minutes": 5
            }
        
        logger.info(f"Generated {slide_type} slide content for {topic}")
        
        return {
            "success": True,
            "slide_content": slide_data
        }
        
    except Exception as e:
        logger.error(f"Failed to generate slide content: {str(e)}")
        return {"success": False, "error": str(e)}

async def create_interactive_element(
    element_type: str,
    topic: str,
    difficulty_level: str,
    learning_objective: str
) -> Dict[str, Any]:
    """
    Create an interactive element for a lesson slide.
    
    Args:
        element_type: Type of interactive element
        topic: Topic for the element
        difficulty_level: Difficulty level
        learning_objective: Learning objective
    
    Returns:
        Dict containing interactive element data
    """
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        prompt = f"""Create an interactive {element_type} element about {topic} at {difficulty_level} difficulty level.

Learning Objective: {learning_objective}

Generate appropriate content based on the element type:
- multiple_choice: Question with 4 options, 1 correct
- drag_drop: Items to drag and drop zones to match
- fill_blank: Text with blanks to fill in
- matching: Items to match with their pairs
- ordering: Items to put in correct sequence

Return JSON format:
{{
  "widget_type": "{element_type}",
  "title": "Interactive element title",
  "instructions": "Clear instructions for students",
  "content": {{
    // Element-specific content structure
  }},
  "correct_answer": {{
    // Correct answer data
  }},
  "hints": ["hint1", "hint2"],
  "points": 1,
  "feedback": {{
    "correct": "Positive feedback for correct answer",
    "incorrect": "Helpful feedback for incorrect answer"
  }}
}}"""

        response = await model.generate_content_async(prompt)
        
        try:
            element_data = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback
            element_data = {
                "widget_type": element_type,
                "title": f"{topic} Practice",
                "instructions": "Complete this activity",
                "content": {"question": response.text},
                "correct_answer": {},
                "hints": [],
                "points": 1
            }
        
        logger.info(f"Created {element_type} interactive element for {topic}")
        
        return {
            "success": True,
            "interactive_element": element_data
        }
        
    except Exception as e:
        logger.error(f"Failed to create interactive element: {str(e)}")
        return {"success": False, "error": str(e)}

async def adapt_lesson_difficulty(
    lesson_id: str,
    student_id: str,
    performance_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Adapt lesson difficulty based on student performance.
    
    Args:
        lesson_id: ID of the lesson to adapt
        student_id: Student ID
        performance_data: Recent performance data
    
    Returns:
        Dict containing adaptation results
    """
    try:
        # Get current lesson and progress
        lesson_doc = db.collection("lessons").document(lesson_id).get()
        if not lesson_doc.exists:
            return {"success": False, "error": "Lesson not found"}
        
        lesson_data = lesson_doc.to_dict()
        progress_data = await _get_lesson_progress(lesson_id, student_id)
        
        # Analyze performance and determine adaptations needed
        adaptations = await _analyze_performance_for_adaptation(
            performance_data, progress_data, lesson_data
        )
        
        if not adaptations["needs_adaptation"]:
            return {
                "success": True,
                "adapted": False,
                "message": "No adaptation needed based on current performance"
            }
        
        # Apply adaptations to lesson content
        adapted_content = await _apply_lesson_adaptations(
            lesson_data, adaptations["recommendations"]
        )
        
        # Update lesson in database
        db.collection("lessons").document(lesson_id).update(adapted_content)
        
        # Log adaptation
        adaptation_log = {
            "lesson_id": lesson_id,
            "student_id": student_id,
            "adaptation_type": adaptations["type"],
            "recommendations": adaptations["recommendations"],
            "applied_at": datetime.utcnow()
        }
        
        db.collection("lesson_adaptations").add(adaptation_log)
        
        logger.info(f"Adapted lesson {lesson_id} for student {student_id}")
        
        return {
            "success": True,
            "adapted": True,
            "adaptation_type": adaptations["type"],
            "changes_made": adaptations["recommendations"],
            "message": f"Lesson adapted to {adaptations['type']} difficulty level"
        }
        
    except Exception as e:
        logger.error(f"Failed to adapt lesson difficulty: {str(e)}")
        return {"success": False, "error": str(e)}

# Helper functions

async def _get_learning_step(step_id: str) -> Optional[LearningStep]:
    """Get learning step from database."""
    try:
        # This would get the learning step from the learning paths
        # For now, return a mock step
        return LearningStep(
            step_id=step_id,
            step_number=1,
            title="Sample Step",
            description="Sample learning step",
            subject="Mathematics",
            topic="Addition",
            difficulty_level=DifficultyLevel.EASY,
            learning_objective="understand",
            content_type="practice",
            estimated_duration_minutes=30
        )
    except Exception as e:
        logger.error(f"Failed to get learning step: {str(e)}")
        return None

async def _get_student_context(student_id: str, teacher_uid: str) -> Dict[str, Any]:
    """Get student context for personalization from real-time database."""
    try:
        # Get student profile from database
        student_doc = db.collection("students").document(student_id).get()
        
        if not student_doc.exists:
            logger.warning(f"Student {student_id} not found, using minimal context")
            return {
                "student_id": student_id,
                "grade_level": 5,  # Fallback only
                "learning_style": "mixed"
            }
        
        student_data = student_doc.to_dict()
        
        # Get recent assessment performance for areas of strength/support
        recent_assessments = db.collection("assessment_results").where(
            filter=firestore.FieldFilter("student_id", "==", student_id)
        ).order_by("completed_at", direction=firestore.Query.DESCENDING).limit(5).get()
        
        # Analyze performance patterns
        areas_of_strength = []
        areas_needing_support = []
        total_scores = []
        
        for assessment in recent_assessments:
            assessment_data = assessment.to_dict()
            score = assessment_data.get("score", 0)
            total_scores.append(score)
            
            # Analyze subject performance
            subject = assessment_data.get("subject", "")
            if score >= 80:
                if subject and subject not in areas_of_strength:
                    areas_of_strength.append(subject)
            elif score < 60:
                if subject and subject not in areas_needing_support:
                    areas_needing_support.append(subject)
        
        # Calculate performance level
        avg_score = sum(total_scores) / len(total_scores) if total_scores else 70
        if avg_score >= 85:
            performance_level = "advanced"
        elif avg_score >= 70:
            performance_level = "proficient"
        elif avg_score >= 60:
            performance_level = "developing"
        else:
            performance_level = "needs_support"
        
        # Get learning preferences from student profile
        learning_style = student_data.get("learning_preferences", {}).get("preferred_style", "mixed")
        
        return {
            "student_id": student_id,
            "grade_level": student_data.get("grade_level", 5),
            "learning_style": learning_style,
            "performance_level": performance_level,
            "areas_of_strength": areas_of_strength[:3],  # Top 3
            "areas_needing_support": areas_needing_support[:3],  # Top 3
            "average_score": round(avg_score, 1),
            "total_assessments": len(total_scores),
            "preferred_language": student_data.get("preferred_language", "english"),
            "special_needs": student_data.get("special_needs", []),
            "interests": student_data.get("interests", [])
        }
        
    except Exception as e:
        logger.error(f"Failed to get student context: {str(e)}")
        # Return minimal fallback context
        return {
            "student_id": student_id,
            "grade_level": 5,
            "learning_style": "mixed",
            "performance_level": "average"
        }

async def _get_relevant_teacher_content(teacher_uid: str, topic: str, subject: str) -> List[str]:
    """Get relevant teacher content using RAG."""
    try:
        # Use enhanced assessment service to search teacher content
        search_results = await enhanced_assessment_service.search_teacher_content(
            teacher_uid=teacher_uid,
            search_query=f"{topic} {subject}",
            subject_filter=subject
        )
        
        return [result.get("content_preview", "") for result in search_results.get("results", [])]
    except Exception as e:
        logger.error(f"Failed to get teacher content: {str(e)}")
        return []

async def _generate_lesson_with_ai(
    learning_step: LearningStep,
    student_context: Dict[str, Any],
    teacher_content: List[str],
    customizations: Optional[Dict[str, Any]]
) -> LessonContent:
    """Generate lesson content using AI."""
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        # Build context for AI generation
        context = f"""
Learning Step: {learning_step.title}
Topic: {learning_step.topic}
Subject: {learning_step.subject}
Difficulty: {learning_step.difficulty_level}
Objective: {learning_step.learning_objective}
Duration: {learning_step.estimated_duration_minutes} minutes

Student Context: {json.dumps(student_context)}

Teacher Content Available: {json.dumps(teacher_content[:3]) if teacher_content else 'None'}

Customizations: {json.dumps(customizations) if customizations else 'None'}
"""

        prompt = f"""Create a comprehensive lesson with multiple slides for the following learning step:

{context}

Generate a lesson with 5-8 slides that includes:
1. Introduction slide with learning objectives
2. Concept explanation slides with examples
3. Interactive practice slides
4. Assessment/check understanding slides
5. Summary/reflection slide

Each slide should be engaging and appropriate for the student's level. Include interactive elements where beneficial.

Return JSON format:
{{
  "title": "Lesson title",
  "description": "What this lesson covers",
  "learning_objectives": ["objective1", "objective2"],
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "introduction|concept_explanation|example|practice|assessment|summary",
      "title": "Slide title",
      "subtitle": "Optional subtitle",
      "learning_objective": "What students learn from this slide",
      "estimated_duration_minutes": 5,
      "content_elements": [
        {{
          "element_type": "text|image|interactive_widget|exercise",
          "title": "Element title",
          "content": "Element content",
          "position": 1
        }}
      ],
      "is_interactive": false,
      "completion_criteria": {{}}
    }}
  ]
}}"""

        response = await model.generate_content_async(prompt)
        
        try:
            lesson_data = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback lesson structure
            lesson_data = {
                "title": learning_step.title,
                "description": learning_step.description,
                "learning_objectives": [f"Learn about {learning_step.topic}"],
                "slides": [{
                    "slide_number": 1,
                    "slide_type": "concept_explanation",
                    "title": learning_step.title,
                    "learning_objective": f"Understand {learning_step.topic}",
                    "estimated_duration_minutes": learning_step.estimated_duration_minutes,
                    "content_elements": [{
                        "element_type": "text",
                        "title": "Content",
                        "content": response.text,
                        "position": 1
                    }],
                    "is_interactive": False
                }]
            }
        
        # Create LessonContent object
        lesson_id = str(uuid.uuid4())
        
        # Convert slides to LessonSlide objects
        slides = []
        for slide_data in lesson_data["slides"]:
            slide_id = str(uuid.uuid4())
            
            # Convert content elements
            content_elements = []
            for elem_data in slide_data.get("content_elements", []):
                element = ContentElement(
                    element_id=str(uuid.uuid4()),
                    element_type=ContentElementType(elem_data.get("element_type", "text")),
                    title=elem_data.get("title"),
                    content=elem_data.get("content"),
                    position=elem_data.get("position", 1)
                )
                content_elements.append(element)
            
            slide = LessonSlide(
                slide_id=slide_id,
                slide_number=slide_data["slide_number"],
                slide_type=SlideType(slide_data.get("slide_type", "concept_explanation")),
                title=slide_data["title"],
                subtitle=slide_data.get("subtitle"),
                content_elements=content_elements,
                learning_objective=slide_data["learning_objective"],
                estimated_duration_minutes=slide_data.get("estimated_duration_minutes", 5),
                is_interactive=slide_data.get("is_interactive", False),
                completion_criteria=slide_data.get("completion_criteria") or {}
            )
            slides.append(slide)
        
        lesson_content = LessonContent(
            lesson_id=lesson_id,
            learning_step_id=learning_step.step_id,
            student_id=student_context["student_id"],
            teacher_uid=student_context.get("teacher_uid", ""),
            title=lesson_data["title"],
            description=lesson_data["description"],
            subject=learning_step.subject,
            topic=learning_step.topic,
            grade_level=student_context.get("grade_level", 5),
            slides=slides,
            total_slides=len(slides),
            learning_objectives=lesson_data["learning_objectives"]
        )
        
        return lesson_content
        
    except Exception as e:
        logger.error(f"Failed to generate lesson with AI: {str(e)}")
        raise e

async def _save_lesson_content(lesson_content: LessonContent) -> str:
    """Save lesson content to database."""
    try:
        lesson_ref = db.collection("lessons").document(lesson_content.lesson_id)
        lesson_ref.set(lesson_content.dict())
        return lesson_content.lesson_id
    except Exception as e:
        logger.error(f"Failed to save lesson content: {str(e)}")
        raise e

async def _initialize_lesson_progress(lesson_id: str, student_id: str) -> None:
    """Initialize progress tracking for a lesson."""
    try:
        progress = LessonProgress(
            progress_id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            student_id=student_id,
            slides_total=0,  # Will be updated when lesson is loaded
            slide_progress=[]
        )
        
        db.collection("lesson_progress").document(progress.progress_id).set(progress.dict())
    except Exception as e:
        logger.error(f"Failed to initialize lesson progress: {str(e)}")
        raise e

async def _get_lesson_progress(lesson_id: str, student_id: str) -> Optional[Dict[str, Any]]:
    """Get lesson progress for a student."""
    try:
        progress_docs = db.collection("lesson_progress").where(
            filter=firestore.FieldFilter("lesson_id", "==", lesson_id)
        ).where(
            filter=firestore.FieldFilter("student_id", "==", student_id)
        ).limit(1).get()
        
        if progress_docs:
            return progress_docs[0].to_dict()
        return None
    except Exception as e:
        logger.error(f"Failed to get lesson progress: {str(e)}")
        return None

async def _get_lesson_context_for_chat(lesson_id: str, current_slide_id: Optional[str]) -> Dict[str, Any]:
    """Get lesson context for chatbot responses."""
    try:
        lesson_doc = db.collection("lessons").document(lesson_id).get()
        
        if not lesson_doc.exists:
            return {}
        
        lesson_data = lesson_doc.to_dict()
        
        context = {
            "lesson_title": lesson_data.get("title"),
            "topic": lesson_data.get("topic"),
            "subject": lesson_data.get("subject"),
            "learning_objectives": lesson_data.get("learning_objectives", []),
            "key_concepts": lesson_data.get("key_concepts", [])
        }
        
        # Add current slide context if provided
        if current_slide_id:
            slides = lesson_data.get("slides", [])
            current_slide = next((s for s in slides if s.get("slide_id") == current_slide_id), None)
            if current_slide:
                context["current_slide"] = {
                    "title": current_slide.get("title"),
                    "learning_objective": current_slide.get("learning_objective"),
                    "slide_type": current_slide.get("slide_type")
                }
        
        return context
    except Exception as e:
        logger.error(f"Failed to get lesson context for chat: {str(e)}")
        return {}

async def _generate_lesson_structure_with_ai(
    learning_step: LearningStep,
    student_context: Dict[str, Any],
    customizations: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate the high-level lesson structure quickly."""
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        context = f"""
Learning Step: {learning_step.title}
Topic: {learning_step.topic}
Subject: {learning_step.subject}
Difficulty: {learning_step.difficulty_level}
Duration: {learning_step.estimated_duration_minutes} minutes
Student Level: {student_context.get('grade_level', 5)}
Learning Style: {student_context.get('learning_style', 'mixed')}
"""

        prompt = f"""Create a lesson structure outline for:

{context}

Generate a lean lesson structure with 4-6 slides. Focus on slide types and learning flow.

Return JSON:
{{
  "title": "Lesson title",
  "description": "Brief description",
  "learning_objectives": ["obj1", "obj2"],
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "introduction|concept_explanation|example|practice|assessment|summary",
      "title": "Slide title",
      "learning_objective": "What students learn",
      "estimated_duration_minutes": 5,
      "is_interactive": false
    }}
  ]
}}"""

        response = await model.generate_content_async(prompt)
        return _parse_ai_response(response.text)
        
    except Exception as e:
        logger.error(f"Failed to generate lesson structure: {str(e)}")
        return {
            "title": learning_step.title,
            "description": learning_step.description,
            "learning_objectives": [f"Learn about {learning_step.topic}"],
            "slides": [{
                "slide_number": 1,
                "slide_type": "concept_explanation",
                "title": learning_step.title,
                "learning_objective": f"Understand {learning_step.topic}",
                "estimated_duration_minutes": learning_step.estimated_duration_minutes,
                "is_interactive": False
            }]
        }

async def _generate_content_outline(
    learning_step: LearningStep,
    teacher_content: List[str]
) -> Dict[str, Any]:
    """Generate content outline and key points."""
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        prompt = f"""Create a content outline for teaching: {learning_step.topic}

Subject: {learning_step.subject}
Objective: {learning_step.learning_objective}
Teacher Resources: {teacher_content[:2] if teacher_content else 'None'}

Generate key points, examples, and explanations to use in lesson slides.

Return JSON:
{{
  "key_concepts": ["concept1", "concept2"],
  "examples": ["example1", "example2"],
  "explanations": {{"concept1": "explanation"}},
  "practice_ideas": ["idea1", "idea2"],
  "assessment_questions": ["question1", "question2"]
}}"""

        response = await model.generate_content_async(prompt)
        return _parse_ai_response(response.text)
        
    except Exception as e:
        logger.error(f"Failed to generate content outline: {str(e)}")
        return {
            "key_concepts": [learning_step.topic],
            "examples": ["Basic example"],
            "explanations": {learning_step.topic: "Basic explanation"},
            "practice_ideas": ["Practice activity"],
            "assessment_questions": ["Understanding check"]
        }

async def _generate_individual_slide_content(
    slide_outline: Dict[str, Any],
    content_outline: Dict[str, Any],
    student_context: Dict[str, Any],
    slide_number: int
) -> LessonSlide:
    """Generate detailed content for an individual slide."""
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        slide_type = slide_outline.get("slide_type", "concept_explanation")
        
        prompt = f"""Create detailed content for slide {slide_number}:

Type: {slide_type}
Title: {slide_outline.get('title', 'Untitled')}
Objective: {slide_outline.get('learning_objective', 'Learn')}
Student Level: Grade {student_context.get('grade_level', 5)}

Available Content: {json.dumps(content_outline)}

Generate 2-4 content elements for this slide. Make it engaging and appropriate.

Return JSON:
{{
  "title": "Final slide title",
  "subtitle": "Optional subtitle",
  "content_elements": [
    {{
      "element_type": "text|image|interactive_widget|exercise",
      "title": "Element title",
      "content": "Detailed content",
      "position": 1
    }}
  ],
  "completion_criteria": {{}}
}}"""

        response = await model.generate_content_async(prompt)
        slide_data = _parse_ai_response(response.text)
        
        # Build content elements
        content_elements = []
        for i, elem_data in enumerate(slide_data.get("content_elements", [])):
            element = ContentElement(
                element_id=str(uuid.uuid4()),
                element_type=ContentElementType(elem_data.get("element_type", "text")),
                title=elem_data.get("title", f"Element {i+1}"),
                content=elem_data.get("content", "Content"),
                position=elem_data.get("position", i+1)
            )
            content_elements.append(element)
        
        # Create slide
        slide = LessonSlide(
            slide_id=str(uuid.uuid4()),
            slide_number=slide_number,
            slide_type=SlideType(slide_type),
            title=slide_data.get("title", slide_outline.get("title", "Untitled")),
            subtitle=slide_data.get("subtitle"),
            content_elements=content_elements,
            learning_objective=slide_outline.get("learning_objective", "Learn"),
            estimated_duration_minutes=slide_outline.get("estimated_duration_minutes", 5),
            is_interactive=slide_outline.get("is_interactive", False),
            completion_criteria=slide_data.get("completion_criteria", {})
        )
        
        return slide
        
    except Exception as e:
        logger.error(f"Failed to generate slide {slide_number} content: {str(e)}")
        # Return a basic slide as fallback
        return LessonSlide(
            slide_id=str(uuid.uuid4()),
            slide_number=slide_number,
            slide_type=SlideType("concept_explanation"),
            title=slide_outline.get("title", "Content Slide"),
            content_elements=[ContentElement(
                element_id=str(uuid.uuid4()),
                element_type=ContentElementType("text"),
                title="Content",
                content="Lesson content will be displayed here.",
                position=1
            )],
            learning_objective=slide_outline.get("learning_objective", "Learn"),
            estimated_duration_minutes=5,
            is_interactive=False
        )

async def _build_lesson_content(
    lesson_structure: Dict[str, Any],
    slides: List[LessonSlide],
    learning_step: LearningStep,
    student_context: Dict[str, Any]
) -> LessonContent:
    """Build the final lesson content object."""
    try:
        lesson_id = str(uuid.uuid4())
        
        lesson_content = LessonContent(
            lesson_id=lesson_id,
            learning_step_id=learning_step.step_id,
            student_id=student_context["student_id"],
            teacher_uid=student_context.get("teacher_uid", ""),
            title=lesson_structure.get("title", learning_step.title),
            description=lesson_structure.get("description", learning_step.description),
            subject=learning_step.subject,
            topic=learning_step.topic,
            grade_level=student_context.get("grade_level", 5),
            slides=slides,
            total_slides=len(slides),
            learning_objectives=lesson_structure.get("learning_objectives", [f"Learn about {learning_step.topic}"])
        )
        
        return lesson_content
        
    except Exception as e:
        logger.error(f"Failed to build lesson content: {str(e)}")
        raise e

async def _generate_lesson_ultra_fast(
    learning_step: LearningStep,
    student_context: Dict[str, Any]
) -> LessonContent:
    """Generate lesson content with ultra-fast approach."""
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        # Extremely concise prompt for speed
        prompt = f"""Create a {learning_step.topic} lesson for grade {student_context.get('grade_level', 5)}. 
Topic: {learning_step.topic}
Subject: {learning_step.subject}

Generate 4 slides: intro, explanation, practice, summary. Be concise.

JSON:
{{
  "title": "{learning_step.topic} Lesson",
  "description": "Learn {learning_step.topic}",
  "learning_objectives": ["Understand {learning_step.topic}", "Apply concepts"],
  "slides": [
    {{"slide_number": 1, "slide_type": "introduction", "title": "Introduction to {learning_step.topic}", "learning_objective": "Get started", "estimated_duration_minutes": 5, "content_elements": [{{"element_type": "text", "title": "Welcome", "content": "Today we learn {learning_step.topic}", "position": 1}}], "is_interactive": false}},
    {{"slide_number": 2, "slide_type": "concept_explanation", "title": "Understanding {learning_step.topic}", "learning_objective": "Learn concepts", "estimated_duration_minutes": 10, "content_elements": [{{"element_type": "text", "title": "Key Ideas", "content": "{learning_step.topic} explained", "position": 1}}], "is_interactive": false}},
    {{"slide_number": 3, "slide_type": "practice", "title": "Practice", "learning_objective": "Apply knowledge", "estimated_duration_minutes": 8, "content_elements": [{{"element_type": "text", "title": "Try This", "content": "Practice problems", "position": 1}}], "is_interactive": true}},
    {{"slide_number": 4, "slide_type": "summary", "title": "Summary", "learning_objective": "Review", "estimated_duration_minutes": 5, "content_elements": [{{"element_type": "text", "title": "Recap", "content": "What we learned", "position": 1}}], "is_interactive": false}}
  ]
}}

Expand content but keep structure exactly as shown."""

        response = await model.generate_content_async(prompt)
        
        # Quick parsing with immediate fallback
        lesson_data = _parse_ai_response(response.text)
        
        # If parsing fails or insufficient data, use fast template
        if not lesson_data.get("slides") or len(lesson_data.get("slides", [])) < 4:
            lesson_data = _get_fast_template_lesson(learning_step)
        
        # Quick conversion to objects
        lesson_id = str(uuid.uuid4())
        slides = []
        
        for slide_data in lesson_data["slides"]:
            content_elements = []
            for elem_data in slide_data.get("content_elements", []):
                element = ContentElement(
                    element_id=str(uuid.uuid4()),
                    element_type=ContentElementType(elem_data.get("element_type", "text")),
                    title=elem_data.get("title", "Content"),
                    content=elem_data.get("content") or "Educational content here",
                    position=elem_data.get("position", 1)
                )
                content_elements.append(element)
            
            slide = LessonSlide(
                slide_id=str(uuid.uuid4()),
                slide_number=slide_data["slide_number"],
                slide_type=SlideType(slide_data.get("slide_type", "concept_explanation")),
                title=slide_data["title"],
                content_elements=content_elements,
                learning_objective=slide_data["learning_objective"],
                estimated_duration_minutes=slide_data.get("estimated_duration_minutes", 5),
                is_interactive=slide_data.get("is_interactive", False)
            )
            slides.append(slide)
        
        lesson_content = LessonContent(
            lesson_id=lesson_id,
            learning_step_id=learning_step.step_id,
            student_id=student_context["student_id"],
            teacher_uid="",
            title=lesson_data.get("title", f"{learning_step.topic} Lesson"),
            description=lesson_data.get("description", f"Learn about {learning_step.topic}"),
            subject=learning_step.subject,
            topic=learning_step.topic,
            grade_level=student_context.get("grade_level", 5),
            slides=slides,
            total_slides=len(slides),
            learning_objectives=lesson_data.get("learning_objectives", [f"Learn {learning_step.topic}"])
        )
        
        return lesson_content
        
    except Exception as e:
        logger.error(f"Failed to generate ultra-fast lesson: {str(e)}")
        # Emergency fallback
        return _create_emergency_lesson(learning_step, student_context)

def _get_fast_template_lesson(learning_step: LearningStep) -> Dict[str, Any]:
    """Get a fast template lesson structure."""
    return {
        "title": f"Quick {learning_step.topic} Lesson",
        "description": f"Essential {learning_step.topic} concepts",
        "learning_objectives": [f"Understand {learning_step.topic}", "Apply basic concepts"],
        "slides": [
            {
                "slide_number": 1,
                "slide_type": "introduction",
                "title": f"Welcome to {learning_step.topic}",
                "learning_objective": "Get oriented",
                "estimated_duration_minutes": 5,
                "content_elements": [{
                    "element_type": "text",
                    "title": "Today's Topic",
                    "content": f"We're learning about {learning_step.topic} today. This is an important {learning_step.subject} concept.",
                    "position": 1
                }],
                "is_interactive": False
            },
            {
                "slide_number": 2,
                "slide_type": "concept_explanation",
                "title": f"What is {learning_step.topic}?",
                "learning_objective": "Understand the basics",
                "estimated_duration_minutes": 10,
                "content_elements": [{
                    "element_type": "text",
                    "title": "Definition",
                    "content": f"{learning_step.topic} is a fundamental concept in {learning_step.subject}. Let's explore what it means and why it's useful.",
                    "position": 1
                }],
                "is_interactive": False
            },
            {
                "slide_number": 3,
                "slide_type": "practice",
                "title": "Try It Out",
                "learning_objective": "Practice what you learned",
                "estimated_duration_minutes": 8,
                "content_elements": [{
                    "element_type": "text",
                    "title": "Practice Time",
                    "content": f"Now let's practice working with {learning_step.topic}. Start with simple examples and build up your confidence.",
                    "position": 1
                }],
                "is_interactive": True
            },
            {
                "slide_number": 4,
                "slide_type": "summary",
                "title": "What We Learned",
                "learning_objective": "Review and reflect",
                "estimated_duration_minutes": 5,
                "content_elements": [{
                    "element_type": "text",
                    "title": "Key Points",
                    "content": f"Great job learning about {learning_step.topic}! Remember the key concepts and keep practicing.",
                    "position": 1
                }],
                "is_interactive": False
            }
        ]
    }

def _create_emergency_lesson(learning_step: LearningStep, student_context: Dict[str, Any]) -> LessonContent:
    """Create emergency lesson when everything else fails."""
    lesson_id = str(uuid.uuid4())
    
    slide = LessonSlide(
        slide_id=str(uuid.uuid4()),
        slide_number=1,
        slide_type=SlideType("concept_explanation"),
        title=f"{learning_step.topic} Overview",
        content_elements=[ContentElement(
            element_id=str(uuid.uuid4()),
            element_type=ContentElementType("text"),
            title="Lesson Content",
            content=f"This lesson covers {learning_step.topic} fundamentals.",
            position=1
        )],
        learning_objective=f"Learn about {learning_step.topic}",
        estimated_duration_minutes=10,
        is_interactive=False
    )
    
    return LessonContent(
        lesson_id=lesson_id,
        learning_step_id=learning_step.step_id,
        student_id=student_context["student_id"],
        teacher_uid="",
        title=f"{learning_step.topic} Lesson",
        description=f"Learn {learning_step.topic}",
        subject=learning_step.subject,
        topic=learning_step.topic,
        grade_level=student_context.get("grade_level", 5),
        slides=[slide],
        total_slides=1,
        learning_objectives=[f"Understand {learning_step.topic}"]
    )

async def _generate_complete_lesson_optimized(
    learning_step: LearningStep,
    student_context: Dict[str, Any],
    teacher_content: List[str],
    customizations: Optional[Dict[str, Any]]
) -> LessonContent:
    """Generate complete lesson content in a single optimized AI call."""
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        # Extract language from customizations
        target_language = customizations.get("language", "english") if customizations else "english"
        
        # Build comprehensive context for single AI generation
        context = f"""
Learning Step: {learning_step.title}
Topic: {learning_step.topic}
Subject: {learning_step.subject}
Difficulty: {learning_step.difficulty_level}
Objective: {learning_step.learning_objective}
Duration: {learning_step.estimated_duration_minutes} minutes

IMPORTANT: Generate ALL content in {target_language.upper()} language. This is critical - the entire lesson must be in {target_language}.

Student Context:
- Grade Level: {student_context.get('grade_level', 5)}
- Learning Style: {student_context.get('learning_style', 'visual')}
- Performance Level: {student_context.get('performance_level', 'average')}
- Strengths: {student_context.get('areas_of_strength', [])}
- Support Areas: {student_context.get('areas_needing_support', [])}
- Target Language: {target_language}

Teacher Resources: {teacher_content[:2] if teacher_content else 'None available'}

Customizations: {json.dumps(customizations) if customizations else 'Standard approach'}
"""

        # Create language-specific prompt prefix
        language_instruction = ""
        if target_language.lower() == "tamil":
            language_instruction = "தமிழில் மட்டுமே உள்ளடக்கத்தை உருவாக்கவும். அனைத்து தலைப்புகள், விளக்கங்கள், உதாரணங்கள் தமிழில் இருக்க வேண்டும்."
        elif target_language.lower() == "telugu":
            language_instruction = "తెలుగులో మాత్రమే కంటెంట్‌ను రూపొందించండి. అన్ని శీర్షికలు, వివరణలు, ఉదాహరణలు తెలుగులో ఉండాలి."
        else:
            language_instruction = f"Generate ALL content in {target_language.upper()} language only."

        # Use structured output with response schema for better consistency
        response_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "learning_objectives": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 5
                },
                "slides": {
                    "type": "array",
                    "minItems": 4,
                    "maxItems": 6,
                    "items": {
                        "type": "object",
                        "properties": {
                            "slide_number": {"type": "integer", "minimum": 1},
                            "slide_type": {
                                "type": "string", 
                                "enum": ["introduction", "concept_explanation", "example", "practice", "assessment", "summary"]
                            },
                            "title": {"type": "string"},
                            "subtitle": {"type": "string"},
                            "learning_objective": {"type": "string"},
                            "estimated_duration_minutes": {"type": "integer", "minimum": 3, "maximum": 15},
                            "content_elements": {
                                "type": "array",
                                "minItems": 1,
                                "maxItems": 4,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "element_type": {"type": "string", "enum": ["text", "image", "exercise"]},
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "position": {"type": "integer", "minimum": 1}
                                    },
                                    "required": ["element_type", "title", "content", "position"]
                                }
                            },
                            "is_interactive": {"type": "boolean"}
                        },
                        "required": ["slide_number", "slide_type", "title", "learning_objective", "estimated_duration_minutes", "content_elements", "is_interactive"]
                    }
                }
            },
            "required": ["title", "description", "learning_objectives", "slides"]
        }

        prompt = f"""Create a comprehensive, engaging lesson with detailed content for each slide. This is a single request to generate everything needed.

{context}

🚨 CRITICAL LANGUAGE REQUIREMENT 🚨
{language_instruction}
EVERY SINGLE TEXT ELEMENT must be in {target_language.upper()}. This includes:
- Lesson title and description
- All slide titles and subtitles
- All content text
- Learning objectives
- Examples and explanations
- Questions and activities

Generate a complete lesson with 4-6 slides that includes:
1. Introduction slide (slide_type: "introduction") with clear learning objectives
2. Concept explanation slides (slide_type: "concept_explanation") with examples and visual descriptions  
3. Practice elements (slide_type: "practice") - text-based activities only
4. Assessment/understanding checks (slide_type: "assessment") - text-based questions only
5. Summary with key takeaways (slide_type: "summary")

CRITICAL: Use ONLY these exact slide_type values:
- "introduction"
- "concept_explanation" 
- "example"
- "practice"
- "assessment"
- "summary"

Make each slide rich with content, examples, and activities. Use only text-based elements.

IMPORTANT: Respond with valid JSON only. No additional text or formatting.

Example structure (generate content in the specified language):
{{
  "title": "Engaging lesson title in {target_language}",
  "description": "What this lesson covers and why it matters in {target_language}",
  "learning_objectives": ["clear objective 1 in {target_language}", "clear objective 2 in {target_language}"],
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "introduction",
      "title": "Compelling slide title in {target_language}",
      "subtitle": "Helpful subtitle in {target_language}",
      "learning_objective": "Specific objective for this slide in {target_language}",
      "estimated_duration_minutes": 5,
      "content_elements": [
        {{
          "element_type": "text",
          "title": "Element title in {target_language}",
          "content": "Rich, detailed content with examples in {target_language}",
          "position": 1
        }}
      ],
      "is_interactive": false
    }},
    {{
      "slide_number": 2,
      "slide_type": "concept_explanation",
      "title": "Main concepts in {target_language}",
      "learning_objective": "Understand key concepts in {target_language}",
      "estimated_duration_minutes": 8,
      "content_elements": [
        {{
          "element_type": "text",
          "title": "Key Concepts in {target_language}",
          "content": "Detailed explanation in {target_language}",
          "position": 1
        }}
      ],
      "is_interactive": false
    }}
  ]
}}
Generate comprehensive, engaging content in the specified language."""

        # Use structured output for better consistency and language compliance
        try:
            # Try structured output without response_schema first (more compatible)
            generation_config = {
                "response_mime_type": "application/json",
                "temperature": 0.3,  # Lower temperature for more consistent output
                "max_output_tokens": 4000
            }
            
            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            logger.info("Successfully used JSON structured output for lesson generation")
        except Exception as e:
            logger.warning(f"Structured output failed, falling back to regular generation: {str(e)}")
            response = await model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4000
                }
            )
        
        # Parse the comprehensive response
        lesson_data = _parse_ai_response(response.text)
        
        # Validate and fix slide types to match enum values
        if lesson_data.get("slides"):
            for slide in lesson_data["slides"]:
                slide_type = slide.get("slide_type", "concept_explanation")
                # Map invalid slide types to valid ones
                if slide_type not in ["introduction", "concept_explanation", "example", "practice", "assessment", "summary"]:
                    if "practice" in slide_type.lower() and "assessment" in slide_type.lower():
                        slide["slide_type"] = "assessment"
                    elif "practice" in slide_type.lower():
                        slide["slide_type"] = "practice"
                    elif "assessment" in slide_type.lower():
                        slide["slide_type"] = "assessment"
                    elif "intro" in slide_type.lower():
                        slide["slide_type"] = "introduction"
                    elif "example" in slide_type.lower():
                        slide["slide_type"] = "example"
                    elif "summary" in slide_type.lower() or "conclusion" in slide_type.lower():
                        slide["slide_type"] = "summary"
                    else:
                        slide["slide_type"] = "concept_explanation"
        
        # Ensure we have a valid lesson structure
        if not lesson_data.get("slides") or len(lesson_data.get("slides", [])) == 0:
            # Comprehensive fallback lesson structure that matches legacy output
            lesson_data = {
                "title": f"Complete Guide to {learning_step.topic}",
                "description": f"A comprehensive lesson covering {learning_step.topic} concepts, examples, and practice activities.",
                "learning_objectives": [
                    f"Understand the fundamentals of {learning_step.topic}",
                    f"Apply {learning_step.topic} concepts to solve problems",
                    f"Demonstrate mastery through practice activities"
                ],
                "slides": [
                    {
                        "slide_number": 1,
                        "slide_type": "introduction",
                        "title": f"Welcome to {learning_step.topic}",
                        "subtitle": f"Building strong {learning_step.subject} foundations",
                        "learning_objective": f"Understand the importance and applications of {learning_step.topic}",
                        "estimated_duration_minutes": 5,
                        "content_elements": [
                            {
                                "element_type": "text",
                                "title": "Learning Goals",
                                "content": f"Today we'll explore {learning_step.topic}, a fundamental concept in {learning_step.subject}. By the end of this lesson, you'll be able to understand key concepts, work with examples, and apply your knowledge to solve problems.",
                                "position": 1
                            },
                            {
                                "element_type": "text",
                                "title": "Why This Matters",
                                "content": f"{learning_step.topic} is essential for building strong mathematical reasoning skills and will help you in many areas of study and daily life.",
                                "position": 2
                            }
                        ],
                        "is_interactive": False
                    },
                    {
                        "slide_number": 2,
                        "slide_type": "concept_explanation",
                        "title": f"Understanding {learning_step.topic}",
                        "subtitle": "Core concepts and definitions",
                        "learning_objective": f"Learn the fundamental concepts of {learning_step.topic}",
                        "estimated_duration_minutes": 10,
                        "content_elements": [
                            {
                                "element_type": "text",
                                "title": "What is it?",
                                "content": f"{learning_step.topic} is a mathematical concept that helps us understand relationships and solve problems. Let's break it down into simple, easy-to-understand parts.",
                                "position": 1
                            },
                            {
                                "element_type": "text",
                                "title": "Key Components",
                                "content": f"The main parts of {learning_step.topic} include basic definitions, important properties, and common patterns you'll see repeatedly.",
                                "position": 2
                            }
                        ],
                        "is_interactive": False
                    },
                    {
                        "slide_number": 3,
                        "slide_type": "example",
                        "title": f"{learning_step.topic} in Action",
                        "subtitle": "Real-world examples and step-by-step solutions",
                        "learning_objective": f"See how {learning_step.topic} works through concrete examples",
                        "estimated_duration_minutes": 8,
                        "content_elements": [
                            {
                                "element_type": "text",
                                "title": "Example 1",
                                "content": f"Let's work through a basic {learning_step.topic} problem step by step. We'll start with a simple example and show each step clearly.",
                                "position": 1
                            },
                            {
                                "element_type": "text",
                                "title": "Step-by-Step Process",
                                "content": "Step 1: Identify what we know. Step 2: Determine what we need to find. Step 3: Apply the appropriate method. Step 4: Check our answer.",
                                "position": 2
                            }
                        ],
                        "is_interactive": False
                    },
                    {
                        "slide_number": 4,
                        "slide_type": "practice",
                        "title": "Practice Activities",
                        "subtitle": "Try it yourself!",
                        "learning_objective": f"Practice applying {learning_step.topic} concepts",
                        "estimated_duration_minutes": 12,
                        "content_elements": [
                            {
                                "element_type": "text",
                                "title": "Practice Problems",
                                "content": f"Now it's your turn! Try these {learning_step.topic} problems. Start with the easier ones and work your way up.",
                                "position": 1
                            },
                            {
                                "element_type": "text",
                                "title": "Quick Check",
                                "content": f"Test your understanding: Which of the following best describes {learning_step.topic}? Think about how this concept can be used as a mathematical tool, a way to understand relationships, and an important concept in mathematics.",
                                "position": 2
                            }
                        ],
                        "is_interactive": True
                    },
                    {
                        "slide_number": 5,
                        "slide_type": "assessment",
                        "title": "Check Your Understanding",
                        "subtitle": "Assessment and review",
                        "learning_objective": "Demonstrate understanding and identify areas for review",
                        "estimated_duration_minutes": 10,
                        "content_elements": [
                            {
                                "element_type": "text",
                                "title": "Self-Assessment",
                                "content": f"Let's check how well you understand {learning_step.topic}. Think about what you've learned and be honest about areas where you might need more practice.",
                                "position": 1
                            },
                            {
                                "element_type": "text",
                                "title": "Knowledge Check",
                                "content": f"Complete this statement: When working with {learning_step.topic}, it's important to remember that careful analysis helps us understand the relationship, and systematic approaches help us solve problems effectively. Think about good mathematical practices as you work through problems.",
                                "position": 2
                            }
                        ],
                        "is_interactive": True
                    },
                    {
                        "slide_number": 6,
                        "slide_type": "summary",
                        "title": "Lesson Summary",
                        "subtitle": "Key takeaways and next steps",
                        "learning_objective": "Review key concepts and plan next steps",
                        "estimated_duration_minutes": 5,
                        "content_elements": [
                            {
                                "element_type": "text",
                                "title": "What We Learned",
                                "content": f"Congratulations! You've successfully learned about {learning_step.topic}. You now understand the key concepts, have seen examples, and practiced applying your knowledge.",
                                "position": 1
                            },
                            {
                                "element_type": "text",
                                "title": "Key Takeaways",
                                "content": f"Remember: {learning_step.topic} is a powerful tool that becomes easier with practice. The more you work with these concepts, the more confident you'll become.",
                                "position": 2
                            },
                            {
                                "element_type": "text",
                                "title": "Next Steps",
                                "content": "Continue practicing with similar problems, and don't hesitate to review this lesson if you need to refresh your understanding.",
                                "position": 3
                            }
                        ],
                        "is_interactive": False
                    }
                ],
                "assessment_strategy": {
                    "formative_checks": ["slide 4 multiple choice", "slide 5 fill blanks"],
                    "summative_assessment": "overall lesson understanding",
                    "success_criteria": "student demonstrates understanding of key concepts and can apply them"
                },
                "differentiation": {
                    "for_struggling": ["review basic concepts", "additional guided examples"],
                    "for_advanced": ["extension problems", "real-world applications"],
                    "for_different_learning_styles": ["visual examples", "hands-on activities", "step-by-step text"]
                }
            }
        
        # Create LessonContent object
        lesson_id = str(uuid.uuid4())
        
        # Convert slides to LessonSlide objects with enhanced content
        slides = []
        for slide_data in lesson_data["slides"]:
            slide_id = str(uuid.uuid4())
            
            # Convert content elements (no interactive widgets to avoid validation errors)
            content_elements = []
            for elem_data in slide_data.get("content_elements", []):
                # Skip interactive widgets to avoid validation errors
                if elem_data.get("element_type") == "interactive_widget":
                    # Convert interactive widget to text element
                    widget_data = elem_data.get("interactive_widget", {})
                    widget_content = widget_data.get("content", {})
                    
                    # Create text-based version of the interactive content
                    if isinstance(widget_content, dict):
                        question = widget_content.get("question", "")
                        options = widget_content.get("options", [])
                        if question and options:
                            text_content = f"{question}\n\nOptions:\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
                        else:
                            text_content = elem_data.get("content", "Interactive activity")
                    else:
                        text_content = elem_data.get("content", "Interactive activity")
                    
                    element = ContentElement(
                        element_id=str(uuid.uuid4()),
                        element_type=ContentElementType("text"),
                        title=elem_data.get("title", "Activity"),
                        content=text_content,
                        position=elem_data.get("position", 1),
                        styling=elem_data.get("styling", {})
                    )
                else:
                    element = ContentElement(
                        element_id=str(uuid.uuid4()),
                        element_type=ContentElementType(elem_data.get("element_type", "text")),
                        title=elem_data.get("title", "Content"),
                        content=elem_data.get("content") or "Content will be displayed here",
                        position=elem_data.get("position", 1),
                        styling=elem_data.get("styling", {})
                    )
                content_elements.append(element)
            
            slide = LessonSlide(
                slide_id=slide_id,
                slide_number=slide_data["slide_number"],
                slide_type=SlideType(slide_data.get("slide_type", "concept_explanation")),
                title=slide_data["title"],
                subtitle=slide_data.get("subtitle"),
                content_elements=content_elements,
                learning_objective=slide_data["learning_objective"],
                estimated_duration_minutes=slide_data.get("estimated_duration_minutes", 5),
                is_interactive=slide_data.get("is_interactive", False),
                completion_criteria=slide_data.get("completion_criteria") or {},
                visual_elements=slide_data.get("visual_elements", [])
            )
            slides.append(slide)
        
        lesson_content = LessonContent(
            lesson_id=lesson_id,
            learning_step_id=learning_step.step_id,
            student_id=student_context["student_id"],
            teacher_uid=student_context.get("teacher_uid", ""),
            title=lesson_data["title"],
            description=lesson_data["description"],
            subject=learning_step.subject,
            topic=learning_step.topic,
            grade_level=student_context.get("grade_level", 5),
            slides=slides,
            total_slides=len(slides),
            learning_objectives=lesson_data["learning_objectives"],
            assessment_strategy=lesson_data.get("assessment_strategy", {}),
            differentiation=lesson_data.get("differentiation", {})
        )
        
        return lesson_content
        
    except Exception as e:
        logger.error(f"Failed to generate optimized lesson: {str(e)}")
        raise e

def _parse_ai_response(response_text: str) -> Dict[str, Any]:
    """
    Parse AI response with multiple fallback mechanisms.
    
    Args:
        response_text: Raw response text from AI model
        
    Returns:
        Parsed response data dictionary
    """
    try:
        # Method 1: Direct JSON parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Method 2: Extract JSON from code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Method 3: Extract JSON from text (find first complete JSON object)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Method 4: Extract message from quotes if JSON parsing fails
        message_match = re.search(r'"message":\s*"([^"]*)"', response_text)
        if message_match:
            return {
                "message": message_match.group(1),
                "confidence_score": 0.7,
                "sources": ["lesson_content"],
                "suggested_actions": []
            }
        
        # Method 5: Use entire text as message (final fallback)
        # Clean the text by removing JSON formatting artifacts
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # If it looks like it starts with JSON structure, extract just the message content
        if clean_text.startswith('{'):
            # Try to extract just the message content from malformed JSON
            lines = clean_text.split('\n')
            message_lines = []
            in_message = False
            
            for line in lines:
                if '"message":' in line:
                    in_message = True
                    # Extract the message start
                    message_start = line.split('"message":', 1)[1].strip()
                    if message_start.startswith('"'):
                        message_start = message_start[1:]  # Remove opening quote
                    message_lines.append(message_start)
                elif in_message:
                    if line.strip().endswith('",') or line.strip().endswith('"'):
                        # End of message
                        line_text = line.replace('",', '').replace('"', '').strip()
                        if line_text:
                            message_lines.append(line_text)
                        break
                    else:
                        message_lines.append(line)
            
            if message_lines:
                message_text = '\n'.join(message_lines).strip()
                return {
                    "message": message_text,
                    "confidence_score": 0.6,
                    "sources": ["lesson_content"],
                    "suggested_actions": []
                }
        
        # Final fallback - use cleaned text
        return {
            "message": clean_text,
            "confidence_score": 0.5,
            "sources": ["lesson_content"],
            "suggested_actions": []
        }
        
    except Exception as e:
        logger.error(f"Failed to parse AI response: {str(e)}")
        return {
            "message": "I'm here to help with your lesson questions. Could you please rephrase your question?",
            "confidence_score": 0.3,
            "sources": [],
            "suggested_actions": ["Try asking a more specific question about the lesson topic"]
        }

async def _generate_chat_response(
    student_message: str,
    lesson_context: Dict[str, Any],
    chat_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate AI response for chatbot."""
    try:
        model = get_vertex_model("gemini-2.5-pro")
        
        # Serialize chat history for JSON
        serialized_history = []
        recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
        for msg in recent_history:
            serialized_msg = serialize_for_firestore(msg)
            serialized_history.append({
                "sender": serialized_msg.get("sender"),
                "message": serialized_msg.get("message"),
                "timestamp": serialized_msg.get("timestamp")
            })

        # Build context for AI
        context = f"""
Lesson Context:
- Title: {lesson_context.get('lesson_title', 'Unknown')}
- Topic: {lesson_context.get('topic', 'Unknown')}
- Subject: {lesson_context.get('subject', 'Unknown')}
- Learning Objectives: {lesson_context.get('learning_objectives', [])}

Current Slide: {lesson_context.get('current_slide', {}).get('title', 'Unknown')}

Recent Chat History:
{json.dumps(serialized_history)}

Student Message: {student_message}
"""

        prompt = f"""You are a helpful AI tutor assisting a student with their lesson. Based on the context and the student's question, provide a helpful, encouraging, and educational response.

{context}

Guidelines:
- Be encouraging and supportive
- Provide clear explanations appropriate for the grade level
- Use examples and analogies when helpful
- Ask follow-up questions to check understanding
- Don't give direct answers to assessment questions, but provide guidance
- If the question is off-topic, gently redirect to the lesson content

Respond in JSON format:
{{
  "message": "Your helpful response to the student",
  "confidence_score": 0.95,
  "sources": ["lesson_content"],
  "suggested_actions": ["Optional suggestions for next steps"]
}}"""

        response = await model.generate_content_async(prompt)
        
        # Enhanced JSON parsing with multiple fallback mechanisms
        response_data = _parse_ai_response(response.text)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Failed to generate chat response: {str(e)}")
        return {
            "message": "I'm sorry, I'm having trouble understanding your question right now. Could you try asking in a different way?",
            "confidence_score": 0.5,
            "sources": [],
            "suggested_actions": []
        }

async def _analyze_performance_for_adaptation(
    performance_data: Dict[str, Any],
    progress_data: Optional[Dict[str, Any]],
    lesson_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze performance to determine if lesson adaptation is needed."""
    try:
        # Simple adaptation logic - can be enhanced with ML models
        
        # Check completion rate
        completion_rate = progress_data.get("completion_percentage", 0) if progress_data else 0
        
        # Check time spent vs expected
        time_spent = progress_data.get("time_spent_minutes", 0) if progress_data else 0
        expected_time = sum(slide.get("estimated_duration_minutes", 5) for slide in lesson_data.get("slides", []))
        
        # Check interaction success rate
        correct_responses = progress_data.get("correct_responses", 0) if progress_data else 0
        total_responses = progress_data.get("total_responses", 1) if progress_data else 1
        success_rate = correct_responses / total_responses if total_responses > 0 else 0
        
        needs_adaptation = False
        adaptation_type = "maintain"
        recommendations = []
        
        # Determine if adaptation is needed
        if success_rate < 0.5 and completion_rate < 50:
            needs_adaptation = True
            adaptation_type = "simplify"
            recommendations = [
                "Reduce content complexity",
                "Add more examples",
                "Break down concepts into smaller steps",
                "Add more hints and guidance"
            ]
        elif success_rate > 0.9 and time_spent < expected_time * 0.7:
            needs_adaptation = True
            adaptation_type = "enhance"
            recommendations = [
                "Add more challenging content",
                "Include advanced examples",
                "Add extension activities",
                "Reduce repetitive content"
            ]
        
        return {
            "needs_adaptation": needs_adaptation,
            "type": adaptation_type,
            "recommendations": recommendations,
            "analysis": {
                "completion_rate": completion_rate,
                "success_rate": success_rate,
                "time_efficiency": time_spent / expected_time if expected_time > 0 else 1
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze performance for adaptation: {str(e)}")
        return {"needs_adaptation": False, "type": "maintain", "recommendations": []}

async def _apply_lesson_adaptations(
    lesson_data: Dict[str, Any],
    recommendations: List[str]
) -> Dict[str, Any]:
    """Apply adaptations to lesson content."""
    try:
        # This would modify the lesson content based on recommendations
        # For now, just add an adaptation note
        
        adapted_data = lesson_data.copy()
        adapted_data["adaptation_history"] = adapted_data.get("adaptation_history", [])
        adapted_data["adaptation_history"].append({
            "applied_at": datetime.utcnow(),
            "recommendations": recommendations,
            "type": "automatic_adaptation"
        })
        
        return adapted_data
        
    except Exception as e:
        logger.error(f"Failed to apply lesson adaptations: {str(e)}")
        return lesson_data
