# FILE: app/agents/tools/viva_tools.py

import logging
from typing import Dict, Any, Optional
from app.services.viva_service import viva_service
from app.services.learning_path_service import learning_path_service

logger = logging.getLogger(__name__)

async def get_viva_topic(learning_step_id: str) -> str:
    """
    Get the topic for the viva from the learning step.
    
    Args:
        learning_step_id: The ID of the learning step.
        
    Returns:
        The topic for the viva.
    """
    try:
        logger.info(f"Getting viva topic for learning step: {learning_step_id}")
        
        # Get the learning step from the learning path service
        learning_step = await _get_learning_step_by_id(learning_step_id)
        
        if learning_step:
            # Create a comprehensive topic description
            topic = learning_step.title
            if learning_step.subtopic:
                topic = f"{learning_step.topic}: {learning_step.subtopic}"
            elif learning_step.topic != learning_step.title:
                topic = f"{learning_step.topic} - {learning_step.title}"
            
            logger.info(f"Found topic for learning step {learning_step_id}: {topic}")
            return topic
        else:
            logger.warning(f"Learning step {learning_step_id} not found, using default topic")
            return "General Review Topic"
            
    except Exception as e:
        logger.error(f"Error getting viva topic for learning step {learning_step_id}: {str(e)}")
        return "General Review Topic"

async def auto_start_viva_for_step(student_id: str, learning_step_id: str, language: str = "english") -> Dict[str, Any]:
    """
    Automatically start a VIVA session for a learning step if it's configured for VIVA.
    
    Args:
        student_id: The ID of the student.
        learning_step_id: The ID of the learning step.
        language: The language for the viva (default: english).
        
    Returns:
        VIVA session details if step has VIVA, or info about step content type.
    """
    try:
        logger.info(f"Checking if learning step {learning_step_id} has VIVA configured")
        
        # Get the learning step
        learning_step = await _get_learning_step_by_id(learning_step_id)
        
        if not learning_step:
            return {
                "error": f"Learning step {learning_step_id} not found",
                "has_viva": False
            }
        
        # Check if this step is configured for VIVA
        has_viva = (
            learning_step.content_type == "viva" or 
            getattr(learning_step, 'has_viva', False)
        )
        
        if has_viva:
            logger.info(f"Learning step {learning_step_id} has VIVA - starting session")
            return await start_viva_session(student_id, learning_step_id, language)
        else:
            return {
                "has_viva": False,
                "content_type": learning_step.content_type,
                "message": f"This learning step uses {learning_step.content_type} content, not VIVA",
                "step_title": learning_step.title,
                "step_description": learning_step.description
            }
            
    except Exception as e:
        logger.error(f"Error checking VIVA for learning step {learning_step_id}: {str(e)}")
        return {
            "error": f"Failed to check VIVA configuration: {str(e)}",
            "has_viva": False
        }

async def _get_learning_step_by_id(learning_step_id: str) -> Optional[Any]:
    """
    Helper function to find a learning step by ID across all learning paths.
    
    Args:
        learning_step_id: The ID of the learning step to find.
        
    Returns:
        The learning step if found, None otherwise.
    """
    try:
        # This is a simplified approach - in a real system you might want to index steps separately
        # For now, we'll search through learning paths to find the step
        from app.core.firebase import db
        
        # Query learning paths collection to find the step
        learning_paths_ref = db.collection("learning_paths")
        docs = learning_paths_ref.get()
        
        for doc in docs:
            path_data = doc.to_dict()
            if "steps" in path_data:
                for step_data in path_data["steps"]:
                    if step_data.get("step_id") == learning_step_id:
                        # Convert dict to LearningStep-like object
                        from app.models.learning_models import LearningStep, DifficultyLevel, LearningObjectiveType
                        return LearningStep(
                            step_id=step_data.get("step_id"),
                            step_number=step_data.get("step_number", 1),
                            title=step_data.get("title", "Learning Step"),
                            description=step_data.get("description", ""),
                            subject=step_data.get("subject", "General"),
                            topic=step_data.get("topic", "General"),
                            subtopic=step_data.get("subtopic"),
                            difficulty_level=DifficultyLevel(step_data.get("difficulty_level", "medium")),
                            learning_objective=LearningObjectiveType(step_data.get("learning_objective", "understand")),
                            content_type=step_data.get("content_type", "viva"),
                            content_text=step_data.get("content_text"),
                            estimated_duration_minutes=step_data.get("estimated_duration_minutes", 15),
                            prerequisites=step_data.get("prerequisites", []),
                            addresses_gaps=step_data.get("addresses_gaps", [])
                        )
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching for learning step {learning_step_id}: {str(e)}")
        return None

async def start_viva_session(student_id: str, learning_step_id: str, language: str) -> Dict[str, Any]:
    """
    Start a new viva session.
    
    Args:
        student_id: The ID of the student.
        learning_step_id: The ID of the learning step.
        language: The language for the viva.
        
    Returns:
        A dictionary with the new session details.
    """
    logger.info(f"Starting viva session for student {student_id} in {language} for learning step {learning_step_id}")
    
    try:
        session = await viva_service.start_viva(student_id, learning_step_id, language)
        
        # Get the actual welcome message from the session (generated by AI with learning step context)
        welcome_message = session.conversation_history[0].text if session.conversation_history else f"Hello! Welcome to your viva on {session.topic}. Are you ready to begin?"
        
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "welcome_message": welcome_message,
            "language": language,
            "learning_step_id": learning_step_id
        }
        
    except Exception as e:
        logger.error(f"Error starting viva session: {str(e)}")
        return {
            "error": f"Failed to start viva session: {str(e)}",
            "session_id": None
        }

async def process_student_response(session_id: str, student_speech: str) -> Dict[str, Any]:
    """
    Process the student's spoken response and get the agent's next question or comment.
    
    Args:
        session_id: The current viva session ID.
        student_speech: The transcribed text of the student's response.
        
    Returns:
        The agent's response and any feedback.
    """
    logger.info(f"Processing student response for session {session_id}")
    response = await viva_service.handle_student_speech(session_id, student_speech)
    return response

async def end_viva_session(session_id: str) -> Dict[str, Any]:
    """
    End the viva session and provide a summary.
    
    Args:
        session_id: The viva session ID.
        
    Returns:
        A summary of the viva session.
    """
    logger.info(f"Ending viva session {session_id}")
    summary = await viva_service.end_viva(session_id)
    return summary