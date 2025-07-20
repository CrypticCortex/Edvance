# FILE: app/agents/tools/onboarding_tools.py

from __future__ import annotations
from app.core.firebase import db
from typing import Dict, Any, List
import logging
from contextvars import ContextVar
from datetime import datetime

logger = logging.getLogger(__name__)

# Context variable to store the current user's UID
current_user_uid: ContextVar[str] = ContextVar('current_user_uid')

def create_teacher_profile(name: str, email: str, subjects: List[str]) -> str:
    """
    Creates a new teacher profile in Firestore with onboarding tracking.
    The user UID is automatically obtained from the authenticated session context.

    Args:
        name: Teacher's full name
        email: Teacher's email address
        subjects: Initial list of subjects the teacher handles

    Returns:
        A string confirming the successful profile creation.
    """
    try:
        # Get the user UID from context
        user_uid = current_user_uid.get()
        if not user_uid:
            return "Error: User authentication required to create profile."
        
        logger.info(f"Creating teacher profile for user {user_uid}")
        
        profile_data = {
            "name": name,
            "email": email,
            "subjects": subjects,
            "role": "teacher",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "onboarding": {
                "status": "in_progress",
                "steps_completed": ["profile_created"],
                "current_step": "subjects_setup",
                "started_at": datetime.utcnow()
            }
        }
        
        user_ref = db.collection("users").document(user_uid)
        user_ref.set(profile_data)
        
        return f"Successfully created teacher profile for {name}. Welcome to Edvance! Next step: Set up your subjects."
        
    except LookupError:
        return "Error: User authentication context not found."
    except Exception as e:
        logger.error(f"Failed to create teacher profile: {e}")
        return f"An error occurred while creating your profile: {e}"

def get_onboarding_status() -> str:
    """
    Retrieves the current onboarding status for the authenticated teacher.
    
    Returns:
        A string with the onboarding status and next steps.
    """
    try:
        # Get the user UID from context
        user_uid = current_user_uid.get()
        if not user_uid:
            return "Error: User authentication required to check onboarding status."
        
        logger.info(f"Getting onboarding status for user {user_uid}")
        user_ref = db.collection("users").document(user_uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return "No profile found. Let's start by creating your teacher profile!"
        
        user_data = user_doc.to_dict()
        onboarding = user_data.get("onboarding", {})
        
        status = onboarding.get("status", "not_started")
        steps_completed = onboarding.get("steps_completed", [])
        current_step = onboarding.get("current_step", "profile_creation")
        
        if status == "completed":
            return "🎉 Your onboarding is complete! You're all set to use Edvance."
        
        completed_count = len(steps_completed)
        total_steps = 3  # profile_created, subjects_setup, onboarding_complete
        
        progress_msg = f"Onboarding Progress: {completed_count}/{total_steps} steps completed.\n"
        progress_msg += f"Current step: {current_step}\n"
        progress_msg += f"Completed steps: {', '.join(steps_completed) if steps_completed else 'None'}"
        
        return progress_msg
        
    except LookupError:
        return "Error: User authentication context not found."
    except Exception as e:
        logger.error(f"Failed to get onboarding status: {e}")
        return f"An error occurred while checking onboarding status: {e}"

def complete_onboarding_step(step_name: str) -> str:
    """
    Marks an onboarding step as completed and updates the current step.
    
    Args:
        step_name: The name of the step to mark as completed
        
    Returns:
        A string confirming the step completion and next actions.
    """
    try:
        # Get the user UID from context
        user_uid = current_user_uid.get()
        if not user_uid:
            return "Error: User authentication required to complete onboarding step."
        
        logger.info(f"Completing onboarding step '{step_name}' for user {user_uid}")
        user_ref = db.collection("users").document(user_uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return "Error: User profile not found. Please create your profile first."
        
        user_data = user_doc.to_dict()
        onboarding = user_data.get("onboarding", {})
        steps_completed = onboarding.get("steps_completed", [])
        
        # Add step if not already completed
        if step_name not in steps_completed:
            steps_completed.append(step_name)
        
        # Determine next step
        next_step_map = {
            "profile_created": "subjects_setup",
            "subjects_setup": "onboarding_complete",
            "onboarding_complete": "completed"
        }
        
        next_step = next_step_map.get(step_name, "completed")
        status = "completed" if next_step == "completed" else "in_progress"
        
        # Update onboarding data
        updated_onboarding = {
            "status": status,
            "steps_completed": steps_completed,
            "current_step": next_step,
            "updated_at": datetime.utcnow()
        }
        
        if "started_at" not in onboarding:
            updated_onboarding["started_at"] = datetime.utcnow()
        else:
            updated_onboarding["started_at"] = onboarding["started_at"]
            
        if status == "completed":
            updated_onboarding["completed_at"] = datetime.utcnow()
        
        # Update the document
        user_ref.update({
            "onboarding": updated_onboarding,
            "updated_at": datetime.utcnow()
        })
        
        if status == "completed":
            return f"🎉 Congratulations! You've completed the '{step_name}' step. Your onboarding is now complete! Welcome to Edvance!"
        else:
            return f"✅ Step '{step_name}' completed successfully! Next step: {next_step}"
        
    except LookupError:
        return "Error: User authentication context not found."
    except Exception as e:
        logger.error(f"Failed to complete onboarding step: {e}")
        return f"An error occurred while completing the onboarding step: {e}"
