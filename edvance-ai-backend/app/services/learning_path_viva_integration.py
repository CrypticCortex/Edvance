# FILE: app/services/learning_path_viva_integration.py

import logging
from typing import Dict, Any, Optional
from app.services.learning_path_service import learning_path_service
from app.services.viva_service import viva_service
from app.agents.tools.viva_tools import start_viva_session

logger = logging.getLogger(__name__)

class LearningPathVivaIntegration:
    """Service to seamlessly integrate VIVA with learning path progression."""
    
    async def get_student_current_step_with_viva(
        self, 
        student_id: str, 
        path_id: str, 
        language: str = "english"
    ) -> Dict[str, Any]:
        """
        Get the current learning step for a student and automatically handle VIVA if needed.
        
        Args:
            student_id: The student's ID
            path_id: The learning path ID
            language: Language for VIVA session
            
        Returns:
            Complete step information with VIVA session if applicable
        """
        try:
            # Get the next step from learning path service
            step_info = await learning_path_service.get_next_step_for_student(student_id, path_id)
            
            if not step_info:
                return {"error": "No learning path or steps found"}
            
            if step_info.get("completed"):
                return step_info
            
            # If this step has VIVA, automatically prepare or retrieve session
            if step_info.get("has_viva"):
                logger.info(f"Step {step_info['step_id']} has VIVA - preparing session")
                
                # Check if there's already an active session
                if step_info.get("existing_viva_session"):
                    step_info["viva_status"] = "session_exists"
                    step_info["viva_session_id"] = step_info["existing_viva_session"]
                else:
                    # Automatically start a VIVA session
                    viva_result = await start_viva_session(
                        student_id, 
                        step_info["step_id"], 
                        language
                    )
                    
                    if "error" not in viva_result:
                        step_info["viva_status"] = "session_created"
                        step_info["viva_session_id"] = viva_result["session_id"]
                        step_info["viva_welcome_message"] = viva_result["welcome_message"]
                        
                        # Update the learning step with the session ID
                        await self._update_step_viva_session(
                            path_id, 
                            step_info["step_id"], 
                            viva_result["session_id"]
                        )
                    else:
                        step_info["viva_status"] = "session_failed"
                        step_info["viva_error"] = viva_result["error"]
            
            return step_info
            
        except Exception as e:
            logger.error(f"Error getting current step with VIVA for student {student_id}: {str(e)}")
            return {"error": f"Failed to get current step: {str(e)}"}
    
    async def complete_step_with_viva_score(
        self,
        student_id: str,
        path_id: str,
        step_id: str,
        viva_session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete a learning step, automatically incorporating VIVA score if applicable.
        
        Args:
            student_id: The student's ID
            path_id: The learning path ID
            step_id: The learning step ID
            viva_session_id: Optional VIVA session ID to get score from
            
        Returns:
            Completion result with next step information
        """
        try:
            performance_score = None
            
            # If there's a VIVA session, get the score
            if viva_session_id:
                viva_summary = await viva_service.end_viva(viva_session_id)
                if "score" in viva_summary:
                    performance_score = float(viva_summary["score"])
                    logger.info(f"VIVA score for step {step_id}: {performance_score}")
            
            # Update learning path progress
            updated_path = await learning_path_service.update_learning_path_progress(
                path_id, step_id, completed=True, performance_score=performance_score
            )
            
            # Get next step information
            next_step = await learning_path_service.get_next_step_for_student(student_id, path_id)
            
            return {
                "step_completed": True,
                "step_id": step_id,
                "performance_score": performance_score,
                "path_progress": updated_path.completion_percentage,
                "next_step": next_step
            }
            
        except Exception as e:
            logger.error(f"Error completing step with VIVA score: {str(e)}")
            return {"error": f"Failed to complete step: {str(e)}"}
    
    async def get_learning_path_with_viva_status(
        self, 
        student_id: str, 
        path_id: str
    ) -> Dict[str, Any]:
        """
        Get complete learning path information with VIVA status for each step.
        
        Args:
            student_id: The student's ID
            path_id: The learning path ID
            
        Returns:
            Learning path with VIVA status information
        """
        try:
            path = await learning_path_service.get_learning_path(path_id)
            
            if not path or path.student_id != student_id:
                return {"error": "Learning path not found or access denied"}
            
            # Enhance each step with VIVA status
            enhanced_steps = []
            for step in path.steps:
                step_data = {
                    "step_id": step.step_id,
                    "step_number": step.step_number,
                    "title": step.title,
                    "description": step.description,
                    "content_type": step.content_type,
                    "is_completed": step.is_completed,
                    "performance_score": step.performance_score,
                    "has_viva": step.content_type == "viva" or getattr(step, 'has_viva', False)
                }
                
                # Add VIVA-specific information
                if step_data["has_viva"]:
                    step_data["viva_topic"] = f"{step.topic} - {step.title}"
                    step_data["viva_difficulty"] = step.difficulty_level.value
                    step_data["viva_objective"] = step.learning_objective.value
                    
                    if hasattr(step, 'viva_session_id') and step.viva_session_id:
                        step_data["viva_session_id"] = step.viva_session_id
                        step_data["viva_status"] = "session_exists"
                    else:
                        step_data["viva_status"] = "needs_session"
                
                enhanced_steps.append(step_data)
            
            return {
                "path_id": path.path_id,
                "title": path.title,
                "description": path.description,
                "subject": path.subject,
                "completion_percentage": path.completion_percentage,
                "current_step": path.current_step,
                "total_steps": len(path.steps),
                "steps": enhanced_steps
            }
            
        except Exception as e:
            logger.error(f"Error getting learning path with VIVA status: {str(e)}")
            return {"error": f"Failed to get learning path: {str(e)}"}
    
    async def _update_step_viva_session(
        self, 
        path_id: str, 
        step_id: str, 
        viva_session_id: str
    ) -> None:
        """Update a learning step with its VIVA session ID."""
        try:
            path = await learning_path_service.get_learning_path(path_id)
            if path:
                for step in path.steps:
                    if step.step_id == step_id:
                        step.viva_session_id = viva_session_id
                        break
                
                await learning_path_service._save_learning_path(path)
                logger.info(f"Updated step {step_id} with VIVA session {viva_session_id}")
                
        except Exception as e:
            logger.error(f"Error updating step VIVA session: {str(e)}")

# Global instance
learning_path_viva_integration = LearningPathVivaIntegration()