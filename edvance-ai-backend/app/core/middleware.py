# FILE: app/core/middleware.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def configure_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI application."""
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add other middleware here as needed
    # Example: app.add_middleware(SomeOtherMiddleware)
