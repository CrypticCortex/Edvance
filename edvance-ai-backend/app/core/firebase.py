# FILE: app/core/firebase.py

import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from app.core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK if it hasn't been initialized yet.
    """
    if not firebase_admin._apps:
        try:
            logger.info("Initializing Firebase Admin SDK...")
            cred = credentials.Certificate(settings.google_application_credentials)
            firebase_admin.initialize_app(cred, {
                'projectId': settings.firebase_project_id,
                'storageBucket': settings.firebase_storage_bucket
            })
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            raise

# Initialize Firebase on application startup
initialize_firebase()

# Create easy-to-import instances of Firebase services
db = firestore.client()
firebase_auth = auth
storage_bucket = storage.bucket()