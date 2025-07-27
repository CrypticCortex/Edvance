# FILE: app/core/auth.py

from fastapi import Depends, HTTPException, status
# === CHANGE 1: Import HTTPBearer and HTTPAuthorizationCredentials ===
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.firebase import firebase_auth, db
from firebase_admin import auth
import logging

# Set up logging
logger = logging.getLogger(__name__)

# === CHANGE 2: Create an instance of HTTPBearer ===
# This scheme is simpler and expects a token to be provided directly.
bearer_scheme = HTTPBearer()

# === CHANGE 3: Update the function signature to use the new scheme ===
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Dependency to verify Firebase ID token and get the current user.

    Args:
        credentials (HTTPAuthorizationCredentials): The bearer token from the Authorization header,
                                                    handled by FastAPI's HTTPBearer scheme.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid, expired, or revoked.
        HTTPException: 500 Internal Server Error for other verification failures.

    Returns:
        dict: The decoded token payload, containing user info like uid, email, etc.
    """
    # === CHANGE 4: Get the token from the credentials object ===
    token = credentials.credentials
    
    try:
        # Verify the token against the Firebase Auth service.
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)
        return decoded_token
    except auth.RevokedIdTokenError:
        logger.warning("Authentication failed: Token has been revoked.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError as e:
        logger.warning(f"Authentication failed: Invalid token. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_student(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Dependency to verify student session token and get the current student.

    Args:
        credentials (HTTPAuthorizationCredentials): The session token from the Authorization header.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid or student not found.
        HTTPException: 500 Internal Server Error for other verification failures.

    Returns:
        dict: The student data including student_id, doc_id, and other profile info.
    """
    token = credentials.credentials
    
    try:
        # Search for student with matching session token
        students_ref = db.collection("students")
        query = students_ref.where("current_session_token", "==", token).limit(1)
        results = query.stream()
        
        student_doc = None
        for doc in results:
            student_doc = doc
            break
            
        if not student_doc:
            logger.warning("Authentication failed: Invalid student session token.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        student_data = student_doc.to_dict()
        
        # Check if student is active
        if not student_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student account is deactivated. Please contact your teacher."
            )
        
        # Add document ID to the data
        student_data["doc_id"] = student_doc.id
        
        return student_data
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during student token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )