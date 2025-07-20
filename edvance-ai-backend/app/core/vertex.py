# FILE: app/core/vertex.py

import logging
from typing import Optional
import vertexai
from vertexai.generative_models import GenerativeModel

from app.core.config import settings

logger = logging.getLogger(__name__)

def get_vertex_model(model_name: str = "gemini-1.5-flash") -> GenerativeModel:
    """
    Initialize and return a Vertex AI model instance.
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        Configured Vertex AI GenerativeModel instance
    """
    try:
        # Initialize Vertex AI
        vertexai.init(
            project=settings.google_cloud_project,
            location=settings.google_cloud_location or "us-central1"
        )
        
        # Create and return the model
        model = GenerativeModel(model_name)
        
        logger.info(f"Vertex AI model '{model_name}' initialized successfully")
        return model
        
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI model: {e}")
        raise

def get_vertex_model_async(model_name: str = "gemini-1.5-flash") -> GenerativeModel:
    """
    Get a Vertex AI Generative Model instance for async operations.
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        GenerativeModel instance configured for async use
    """
    return get_vertex_model(model_name)
