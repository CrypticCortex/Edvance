# Core API Endpoints Configuration
# This file defines which endpoints should be visible in the API documentation
# for the essential teacher workflow

CORE_TEACHER_WORKFLOW_ENDPOINTS = {
    # Authentication (Essential)
    "/v1/auth/signup": ["POST"],
    "/v1/auth/me": ["GET"],
    "/v1/auth/me/profile": ["PUT"],
    
    # Student Management (Essential)
    "/v1/students/upload-csv": ["POST"],
    "/v1/students/": ["GET"],
    "/v1/students/{student_id}": ["GET"],
    
    # Assessment Analysis (Essential) 
    "/v1/learning/analyze-assessment": ["POST"],
    "/v1/learning/student/{student_id}/progress": ["GET"],
    
    # Learning Path Management (Essential)
    "/v1/learning/start-monitoring": ["POST"],
    "/v1/learning/generate-learning-path": ["POST"],
    "/v1/learning/student/{student_id}/learning-paths": ["GET"],
    "/v1/learning/learning-path/{path_id}": ["GET"],
    "/v1/learning/adapt-learning-path/{path_id}": ["POST"],
    
    # Lesson Generation (Essential)
    "/v1/lessons/lessons/create-from-step": ["POST"],
    "/v1/lessons/lessons/{lesson_id}": ["GET"],
    "/v1/lessons/lessons/{lesson_id}/progress": ["POST"],
    
    # Chatbot Support (Essential)
    "/v1/lessons/lessons/{lesson_id}/chat/start": ["POST"],
    "/v1/lessons/lessons/chat/{session_id}/message": ["POST"],
    
    # Analytics & Insights (Essential)
    "/v1/learning/teacher/learning-analytics": ["GET"],
    "/v1/learning/student/{student_id}/learning-insights": ["GET"],
    
    # Health Check (Utility)
    "/": ["GET"],
    "/health": ["GET"]
}

# Optional endpoints for advanced users
ADVANCED_ENDPOINTS = {
    "/v1/learning/monitoring-status": ["GET"],
    "/v1/learning/learning-path/{path_id}/update-progress": ["POST"],
    "/v1/lessons/lessons/student/{student_id}": ["GET"],
    "/v1/lessons/lessons/{lesson_id}/analytics": ["GET"],
    "/v1/lessons/lessons/{lesson_id}/regenerate-slide": ["POST"],
    "/v1/students/stats/summary": ["GET"],
    "/v1/students/{student_id}": ["DELETE", "PUT"]
}

# Document generation and assessment creation (Optional)
CONTENT_CREATION_ENDPOINTS = {
    "/v1/documents/upload": ["POST"],
    "/v1/documents/list": ["GET"],
    "/v1/assessments/configs": ["POST", "GET"],
    "/v1/assessments/configs/{config_id}/generate": ["POST"]
}

# All agent/debug endpoints (Hidden by default)
HIDDEN_ENDPOINTS = {
    # Agent framework endpoints
    "/list-apps",
    "/debug/*",
    "/apps/*",
    "/builder/*",
    "/run",
    "/run_sse",
    "/dev-ui",
    
    # Agent specific
    "/v1/agent/*",
    
    # RAG assessments (advanced feature)
    "/v1/assessments/rag/*",
    
    # Basic assessments (if using enhanced learning paths)
    "/v1/assessments/*"
}
