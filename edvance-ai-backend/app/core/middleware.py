# FILE: app/core/middleware.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def configure_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI application."""
    
    # For development, this is your local web server.
    # For production, you must add your deployed frontend's URL.
    origins = [
        "http://localhost:3000",  # Next.js default port
        "http://localhost:8080",
        "http://localhost",
        "http://127.0.0.1:3000",  # Alternative localhost format
        "http://127.0.0.1:8080",
        # "https://your-production-frontend.com", # Add your production URL here
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins, # Use the specific list instead of "*"
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )