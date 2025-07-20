# FILE: app/agents/tools/profile_tools.py

from __future__ import annotations
from app.core.firebase import db
from typing import List
import logging
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Context variable to store the current user's UID
current_user_uid: ContextVar[str] = ContextVar('current_user_uid')

def get_teacher_subjects() -> str:
    """
    Retrieves the current list of subjects for the authenticated teacher from Firestore.
    The user UID is automatically obtained from the authenticated session context.

    Returns:
        A string with the current subjects or an error message.
    """
    try:
        # Get the user UID from context
        user_uid = current_user_uid.get()
        if not user_uid:
            return "Error: User authentication required to get subjects."
        
        logger.info(f"Getting subjects for user {user_uid}")
        user_ref = db.collection("users").document(user_uid)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            subjects = user_data.get("subjects", [])
            if subjects:
                return f"Your current subjects are: {', '.join(subjects)}"
            else:
                return "You don't have any subjects set yet."
        else:
            return "User profile not found. Please create your profile first."
            
    except LookupError:
        return "Error: User authentication context not found."
    except Exception as e:
        logger.error(f"Failed to get subjects for user: {e}")
        return f"An error occurred while retrieving subjects: {e}"

def update_teacher_subjects(subjects: List[str]) -> str:
    """
    Updates the list of subjects for the authenticated teacher in the Firestore database.
    The user UID is automatically obtained from the authenticated session context.

    Args:
        subjects: The new list of subjects for the teacher.

    Returns:
        A string confirming the successful update.
    """
    try:
        # Get the user UID from context
        user_uid = current_user_uid.get()
        if not user_uid:
            return "Error: User authentication required to update subjects."
        
        logger.info(f"Updating subjects for user {user_uid} to {subjects}")
        user_ref = db.collection("users").document(user_uid)
        user_ref.update({"subjects": subjects})
        return f"Successfully updated subjects to: {', '.join(subjects)}."
    except LookupError:
        return "Error: User authentication context not found."
    except Exception as e:
        logger.error(f"Failed to update subjects for user: {e}")
        return f"An error occurred: {e}"

# Keep the original function for backwards compatibility if needed
def update_teacher_subjects_with_uid(user_uid: str, subjects: List[str]) -> str:
    """
    Updates the list of subjects for a given teacher in the Firestore database.

    Args:
        user_uid: The unique ID of the teacher to update.
        subjects: The new list of subjects for the teacher.

    Returns:
        A string confirming the successful update.
    """
    if not user_uid:
        return "Error: User ID is required to update subjects."
    
    try:
        logger.info(f"Updating subjects for user {user_uid} to {subjects}")
        user_ref = db.collection("users").document(user_uid)
        user_ref.update({"subjects": subjects})
        return f"Successfully updated subjects to: {', '.join(subjects)}."
    except Exception as e:
        logger.error(f"Failed to update subjects for user {user_uid}: {e}")
        return f"An error occurred: {e}"