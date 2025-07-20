# FILE: app/api/v1/auth.py

from fastapi import APIRouter, HTTPException, status, Depends
from app.models import UserCreate, UserInDB
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
            "created_at": datetime.utcnow()
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
    This is a protected endpoint.
    """
    user_uid = current_user["uid"]
    try:
        user_doc = db.collection("users").document(user_uid).get()
        if user_doc.exists:
            return user_doc.to_dict()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in database.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching user profile: {str(e)}"
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(current_user: dict = Depends(get_current_user)):
    """
    Logs out the user by revoking their refresh tokens.
    This is a protected endpoint.
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