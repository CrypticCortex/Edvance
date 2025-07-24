# FILE: app/agents/tools/viva_tools.py

import logging
from typing import Dict, Any
from app.services.viva_service import viva_service # Assuming viva_service is created

logger = logging.getLogger(__name__)

async def get_viva_topic(learning_step_id: str) -> str:
    """
    Get the topic for the viva from the learning step.
    
    Args:
        learning_step_id: The ID of the learning step.
        
    Returns:
        The topic for the viva.
    """
    # In a real implementation, this would fetch the learning step from the learning_path_service
    # For now, we'll return a sample topic.
    logger.info(f"Getting viva topic for learning step: {learning_step_id}")
    return "Introduction to Algebra"

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
    logger.info(f"Starting viva session for student {student_id} in {language}")
    session = await viva_service.start_viva(student_id, learning_step_id, language)
    return {
        "session_id": session.session_id,
        "welcome_message": f"Hello! Welcome to your viva on {session.topic}. Are you ready to begin?"
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