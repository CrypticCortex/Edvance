# FILE: app/core/config.py

from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Manages application settings and environment variables.
    """
    # Firebase/Google Cloud Settings
    # The GOOGLE_APPLICATION_CREDENTIALS is automatically used by Google Cloud libraries.
    # We just need to ensure it's set in the environment.
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    firebase_project_id: str
    firebase_storage_bucket: str

    # Gemini Model Settings
    gemini_model_name: str = "gemini-1.5-flash-latest"

    class Config:
        # This tells Pydantic to load variables from a .env file
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a single, reusable instance of the settings
settings = Settings()