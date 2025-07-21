"""
Core Teacher Workflow API
Streamlined API documentation showing only essential endpoints for the teacher journey
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any
from app.core.api_config import APIConfig, TEACHER_WORKFLOW_CONFIG

def create_streamlined_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """Create a streamlined OpenAPI schema with only core teacher workflow endpoints."""
    
    # Get core endpoints for the essential teacher workflow
    core_endpoints = APIConfig.get_core_teacher_endpoints()
    
    # Get the full OpenAPI schema
    full_schema = get_openapi(
        title=TEACHER_WORKFLOW_CONFIG["title"],
        version=TEACHER_WORKFLOW_CONFIG["version"],
        description=TEACHER_WORKFLOW_CONFIG["description"].format(count=len(core_endpoints)),
        routes=app.routes,
        contact=TEACHER_WORKFLOW_CONFIG.get("contact")
    )
    
    # Filter paths to only include core endpoints
    filtered_paths = {}
    for path, path_info in full_schema.get("paths", {}).items():
        # Check if this path matches any of our core endpoints
        if any(core_path == path or ('{' in core_path and _path_matches_pattern(path, core_path)) 
               for core_path in core_endpoints):
            filtered_paths[path] = path_info
    
    # Update the schema with filtered paths
    full_schema["paths"] = filtered_paths
    
    # Add custom tags for better organization
    full_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "👤 Teacher account creation and profile management",
            "externalDocs": {
                "description": "Authentication Guide",
                "url": "#phase-1-teacher-authentication--setup"
            }
        },
        {
            "name": "Students", 
            "description": "👥 Student data management and upload",
            "externalDocs": {
                "description": "Student Management Guide", 
                "url": "#phase-2-student-assessment--performance-analysis"
            }
        },
        {
            "name": "Personalized Learning",
            "description": "🤖 AI-powered learning path generation and monitoring (Ultra-fast ~27s generation)",
            "externalDocs": {
                "description": "Learning Path Guide",
                "url": "#phase-4-personalized-learning-path-creation"
            }
        },
        {
            "name": "Lessons",
            "description": "📚 Ultra-fast lesson creation and chatbot support",
            "externalDocs": {
                "description": "Lesson Generation Guide",
                "url": "#phase-5-ultra-fast-ai-lesson-generation"
            }
        },
        {
            "name": "Health",
            "description": "⚕️ System health and status checks"
        }
    ]
    
    # Add info about the streamlined nature
    full_schema["info"]["x-streamlined"] = {
        "core_endpoints_count": len(core_endpoints),
        "total_available_endpoints": "73+",
        "filtering_applied": True,
        "workflow_focus": "Essential teacher journey only"
    }
    
    return full_schema

def _path_matches_pattern(actual_path: str, pattern_path: str) -> bool:
    """Check if an actual path matches a pattern with path parameters."""
    if '{' not in pattern_path:
        return actual_path == pattern_path
    
    # Simple pattern matching for path parameters
    pattern_parts = pattern_path.split('/')
    actual_parts = actual_path.split('/')
    
    if len(pattern_parts) != len(actual_parts):
        return False
    
    for pattern_part, actual_part in zip(pattern_parts, actual_parts):
        if pattern_part.startswith('{') and pattern_part.endswith('}'):
            # This is a path parameter, it matches any value
            continue
        elif pattern_part != actual_part:
            return False
    
    return True

def configure_streamlined_docs(app: FastAPI):
    """Configure the FastAPI app to show only core teacher workflow endpoints."""
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        app.openapi_schema = create_streamlined_openapi_schema(app)
        return app.openapi_schema
    
    app.openapi = custom_openapi
