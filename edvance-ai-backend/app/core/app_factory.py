# FILE: app/core/app_factory.py

from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

from app.core.firebase import initialize_firebase
from app.core.middleware import configure_middleware
from app.api.v1 import auth as auth_router
from app.api.v1 import agent as agent_router
from app.api.v1 import documents as documents_router
from app.api.v1 import students as students_router
from app.api.v1 import simple_assessments as assessments_router
from app.api.v1 import rag_assessments as rag_router
from app.api.v1 import personalized_learning as learning_router

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        The configured FastAPI application
    """
    # Initialize Firebase before anything else
    initialize_firebase()
    
    # Create the base FastAPI app from the orchestrator agent directory
    app = get_fast_api_app(agents_dir="./app/agents", web=True)
    
    # Configure middleware
    configure_middleware(app)
    
    # Include routers
    app.include_router(auth_router.router, prefix="/v1/auth", tags=["Authentication"])
    app.include_router(agent_router.router, prefix="/v1/agent", tags=["Agent"])
    app.include_router(documents_router.router, prefix="/v1/documents", tags=["Documents"])
    app.include_router(students_router.router, prefix="/v1/students", tags=["Students"])
    app.include_router(assessments_router.router, prefix="/v1/assessments", tags=["Assessments"])
    app.include_router(rag_router.router, prefix="/v1/assessments", tags=["RAG Assessments"])
    app.include_router(learning_router.router, prefix="/v1/learning", tags=["Personalized Learning"])
    
    # Add a root health check
    @app.get("/", tags=["Health"])
    async def root():
        return {
            "message": "Edvance AI Backend",
            "status": "running",
            "version": "1.0.0"
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "message": "Service is operational"
        }
    
    return app
