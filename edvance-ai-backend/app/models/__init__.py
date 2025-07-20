# FILE: app/models/__init__.py

"""Request and response models for the application."""

from .requests import (
    # Authentication models
    UserCreate,
    UserLogin,
    Token,
    UserInDB,
    UserProfileUpdate,
    
    # Agent interaction models
    AgentPrompt,
    AgentResponse,
    HealthResponse,
    
    # Content generation models
    LocalContentRequest,
    GeneratedContentResponse,
)

__all__ = [
    # Authentication models
    "UserCreate",
    "UserLogin", 
    "Token",
    "UserInDB",
    "UserProfileUpdate",
    
    # Agent interaction models
    "AgentPrompt",
    "AgentResponse",
    "HealthResponse",
    
    # Content generation models
    "LocalContentRequest",
    "GeneratedContentResponse",
]
