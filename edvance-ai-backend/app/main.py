# FILE: app/main.py

"""
Edvance AI Backend - Main Application Entry Point

A clean and modular FastAPI application for AI-powered educational content management.
"""

from app.core.app_factory import create_app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)