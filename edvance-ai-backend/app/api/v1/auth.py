# FILE: app/api/v1/auth.py

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status, Depends
import secrets
import hashlib
# Make sure to import UserProfileUpdate
from app.models import UserCreate, UserInDB, UserProfileUpdate
from app.models.requests import StudentLogin, StudentAuthResponse
from app.core.firebase import firebase_auth, db
from firebase_admin.auth import EmailAlreadyExistsError, UserNotFoundError
from app.core.auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate):
    """
    Create a new user in Firebase Authentication and a corresponding user document in Firestore.
    """
    try:
        user_record = firebase_auth.create_user(
            email=user_in.email,
            password=user_in.password
        )
        new_user_data = {
            "uid": user_record.uid,
            "email": user_record.email,
            "created_at": datetime.utcnow(),
            "subjects": [],
            "role": user_in.role or "student",
            "first_name": user_in.first_name or None,
            "last_name": user_in.last_name or None
        }
        db.collection("users").document(user_record.uid).set(new_user_data)
        return new_user_data
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email address is already in use by another account."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/me", response_model=UserInDB)
def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the profile of the currently authenticated user from Firestore.
    """
    user_uid = current_user["uid"]
    try:
        user_doc = db.collection("users").document(user_uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            # Ensure 'role' is always present in the response (default to 'student' if missing)
            if "role" not in user_data:
                user_data["role"] = "student"
            return user_data
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in database.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching user profile: {str(e)}"
        )

@router.put("/me/profile", response_model=UserInDB) # <-- ADD THIS NEW ENDPOINT
def update_user_profile(profile_data: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    """
    Update the profile of the currently authenticated user (e.g., their subjects).
    """
    user_uid = current_user["uid"]
    try:
        user_ref = db.collection("users").document(user_uid)
        
        # Using .update() will create the fields if they don't exist or overwrite them if they do.
        user_ref.update(profile_data.model_dump())
        
        # Retrieve the updated document to return it
        updated_doc = user_ref.get()
        if not updated_doc.exists:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found after update.")
        
        return updated_doc.to_dict()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating user profile: {str(e)}"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(current_user: dict = Depends(get_current_user)):
    """
    Logs out the user by revoking their refresh tokens.
    """
    user_uid = current_user["uid"]
    try:
        firebase_auth.revoke_refresh_tokens(user_uid)
        return {"message": f"Successfully logged out user {user_uid}"}
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during logout: {str(e)}"
        )
    

# ADD THIS ENDPOINT AT THE END OF THE FILE
@router.get("/verify-token", response_model=Dict[str, Any], tags=["Authentication"])
def verify_token_test(current_user: dict = Depends(get_current_user)):
    """
    A simple test endpoint to verify if a Firebase ID token is valid.
    This helps diagnose authentication and permission issues.
    """
    return {
        "status": "success",
        "message": "Token is valid.",
        "decoded_token": current_user
    }

@router.post("/student-login", response_model=StudentAuthResponse, tags=["Student Authentication"])
async def student_login(login_data: StudentLogin):
    """
    Authenticate a student using their student ID and password.
    
    This endpoint:
    1. Searches for a student with the provided student_id
    2. Validates the password against the default_password
    3. Returns a session token and user data if authentication succeeds
    
    Args:
        login_data: StudentLogin containing user_id and password
        
    Returns:
        StudentAuthResponse with token, user data, and session_id
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Search for student by student_id in Firestore
        students_ref = db.collection("students")
        query = students_ref.where("student_id", "==", login_data.user_id).limit(1)
        results = query.stream()
        
        student_doc = None
        for doc in results:
            student_doc = doc
            break
            
        if not student_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid student ID or password"
            )
            
        student_data = student_doc.to_dict()
        
        # Validate password (using simple string comparison for now)
        # In production, you might want to hash passwords
        if student_data.get("default_password") != login_data.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid student ID or password"
            )
            
        # Check if student is active
        if not student_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student account is deactivated. Please contact your teacher."
            )
            
        # Generate a simple session token (in production, use JWT or similar)
        session_token = secrets.token_urlsafe(32)
        session_id = f"student_session_{student_doc.id}_{int(datetime.utcnow().timestamp())}"
        
        # Update last login time
        student_doc.reference.update({
            "last_login": datetime.utcnow(),
            "current_session_token": session_token
        })
        
        # Remove sensitive data from response
        safe_user_data = {
            "student_id": student_data.get("student_id"),
            "first_name": student_data.get("first_name"),
            "last_name": student_data.get("last_name"),
            "grade": student_data.get("grade"),
            "subjects": student_data.get("subjects", []),
            "current_learning_paths": student_data.get("current_learning_paths", {}),
            "performance_metrics": student_data.get("performance_metrics", {}),
            "doc_id": student_doc.id
        }
        
        return StudentAuthResponse(
            token=session_token,
            user=safe_user_data,
            session_id=session_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during student authentication: {str(e)}"
        )