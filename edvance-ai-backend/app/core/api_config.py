"""
Production API Configuration
Controls which endpoints are exposed in production vs development environments
"""

import os
from typing import Dict, Set

# Environment-based endpoint control
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

class APIConfig:
    """Configuration class for controlling API endpoint visibility"""
    
    @staticmethod
    def get_core_teacher_endpoints() -> Set[str]:
        """Get the core endpoints needed for teacher workflow"""
        return {
            # Authentication
            "/v1/auth/signup",
            "/v1/auth/me", 
            "/v1/auth/me/profile",
            
            # Student Management
            "/v1/students/upload-csv",
            "/v1/students/",
            "/v1/students/{student_id}",
            
            # Learning Path & Assessment
            "/v1/learning/start-monitoring",
            "/v1/learning/analyze-assessment", 
            "/v1/learning/generate-learning-path",
            "/v1/learning/student/{student_id}/progress",
            "/v1/learning/student/{student_id}/learning-paths",
            "/v1/learning/learning-path/{path_id}",
            "/v1/learning/adapt-learning-path/{path_id}",
            
            # Lesson Management
            "/v1/lessons/lessons/create-from-step",
            "/v1/lessons/lessons/{lesson_id}",
            "/v1/lessons/lessons/{lesson_id}/progress",
            
            # Chatbot
            "/v1/lessons/lessons/{lesson_id}/chat/start",
            "/v1/lessons/lessons/chat/{session_id}/message",
            
            # Analytics
            "/v1/learning/teacher/learning-analytics", 
            "/v1/learning/student/{student_id}/learning-insights",
            
            # Document Upload
            "/v1/documents/upload",
            "/v1/documents/list",
            
            # Health
            "/",
            "/health"
        }
    
    @staticmethod
    def get_advanced_endpoints() -> Set[str]:
        """Get advanced endpoints for power users"""
        return {
            "/v1/learning/monitoring-status",
            "/v1/learning/learning-path/{path_id}/update-progress",
            "/v1/lessons/lessons/student/{student_id}",
            "/v1/lessons/lessons/{lesson_id}/analytics",
            "/v1/lessons/lessons/{lesson_id}/regenerate-slide",
            "/v1/students/stats/summary"
        }
    
    @staticmethod
    def get_development_endpoints() -> Set[str]:
        """Get development/debugging endpoints"""
        return {
            "/v1/agent/invoke",
            "/v1/agent/health",
            "/v1/assessments/configs",
            "/v1/assessments/rag/documents/upload",
            "/debug/trace/{event_id}",
            "/list-apps"
        }
    
    @staticmethod
    def should_include_endpoint(path: str) -> bool:
        """Determine if an endpoint should be included based on environment"""
        core_endpoints = APIConfig.get_core_teacher_endpoints()
        advanced_endpoints = APIConfig.get_advanced_endpoints()
        dev_endpoints = APIConfig.get_development_endpoints()
        
        # Always include core endpoints
        if path in core_endpoints:
            return True
            
        # Include advanced endpoints in development
        if ENVIRONMENT == "development" and path in advanced_endpoints:
            return True
            
        # Include dev endpoints only in development
        if ENVIRONMENT == "development" and path in dev_endpoints:
            return True
            
        return False

# Create different configurations for different use cases
TEACHER_WORKFLOW_CONFIG = {
    "title": "Edvance AI - Teacher Workflow API",
    "description": """
    ## 🎓 Core Teacher Workflow API
    
    **Streamlined documentation showing only essential endpoints for the teacher journey.**
    
    ### 🚀 Complete Teacher Workflow (22 Core Endpoints)
    
    1. **👤 Authentication** (3 endpoints)
       - Sign up, profile management, authentication
    
    2. **👥 Student Management** (3 endpoints) 
       - Upload student data, view student profiles
    
    3. **🤖 AI Learning Paths** (7 endpoints)
       - Automated monitoring, assessment analysis, path generation
    
    4. **📚 Lesson Generation** (3 endpoints)
       - Ultra-fast lesson creation (~27 seconds), progress tracking
    
    5. **💬 Chatbot Support** (2 endpoints)
       - Intelligent tutoring, context-aware responses
    
    6. **📊 Analytics & Insights** (2 endpoints)
       - Teacher dashboard, student learning insights
    
    7. **⚕️ Health Checks** (2 endpoints)
       - System status and health monitoring
    
    ### ⚡ Key Features
    - **Ultra-Fast**: Lessons generated in ~27 seconds
    - **Automated**: 95% of tasks handled by AI agents  
    - **Intelligent**: Context-aware chatbot support
    - **Adaptive**: Learning paths adjust to student progress
    - **Scalable**: Handle 30+ students effortlessly
    
    ### 📚 Full Documentation
    See `COMPLETE_TEACHER_JOURNEY.md` for the complete teacher workflow guide.
    
    ---
    *Showing {count} core endpoints (filtered from 73+ total)*
    """,
    "version": "1.0.0",
    "contact": {
        "name": "Edvance AI Support",
        "email": "support@edvance.ai"
    }
}

FULL_API_CONFIG = {
    "title": "Edvance AI - Complete API",
    "description": "Full API documentation with all available endpoints",
    "version": "1.0.0"
}
