# Edvance AI - Intelligent Teaching Assistant Platform

> 🎓 An AI-powered teaching assistant built with Google AI technologies to support teachers in multi-grade, low-resource classroom environments.

## 🌟 Overview

**Edvance AI** is a comprehensive web-based teaching assistant that leverages cutting-edge AI technologies to revolutionize education. Built using Google's Gemini AI, Vertex AI, and Firebase, it provides teachers with intelligent tools for content generation, personalized learning paths, automated assessments, and real-time student monitoring.

### ⚡ Key Features

- **🤖 AI Learning Path Generation** - Automated, personalized learning paths based on student performance
- **📚 Ultra-Fast Lesson Creation** - Generate complete lessons in ~27 seconds
- **💬 Intelligent Chatbot Tutoring** - Context-aware student support and guidance
- **👥 Student Management** - Bulk upload, profile management, and progress tracking
- **📊 Real-Time Analytics** - Teacher dashboards and student learning insights
- **🎯 Smart Assessment System** - Automated generation and analysis of assessments
- **📄 Document Processing** - RAG-powered content indexing and retrieval
- **🎙️ Voice-Interactive Viva** - Real-time speech assessment using Gemini Live
- **🔒 Secure Authentication** - Firebase-based user management and authorization

### 🏗️ Technology Stack

**Backend Architecture:**
- **FastAPI** - High-performance Python web framework
- **Google Agent Development Kit (ADK)** - AI agent orchestration
- **Firebase** - Authentication, database, and storage
- **Vertex AI** - RAG engine and vector embeddings
- **Gemini AI** - Text generation and multimodal processing
- **Gemini Live** - Real-time speech interaction

**AI Services:**
- **Gemini 2.5 Pro** - Advanced text generation and reasoning
- **Vertex AI Speech-to-Text** - Audio processing and transcription
- **Vertex AI Search** - Document indexing and retrieval
- **Vector Embeddings** - Semantic search and content matching

## 🚀 Quick Start Guide

### Prerequisites

Before testing the backend, ensure you have:

1. **Python 3.9+** installed
2. **Google Cloud Project** with the following APIs enabled:
   - Vertex AI API
   - Firebase Admin SDK
   - Cloud Speech-to-Text API
   - Cloud Document AI API
3. **Service Account Key** with appropriate permissions
4. **Firebase Project** configured

### 🛠️ Installation & Setup

1. **Clone and Navigate to Backend:**
   ```bash
   cd edvance-ai-backend
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables (.env inside edvance-ai-backend folder):**
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS="svc-acc-key.json"

   FIREBASE_PROJECT_ID=""

   FIREBASE_STORAGE_BUCKET=""

   GOOGLE_GENAI_USE_VERTEXAI=TRUE

   GEMINI_API_KEY=""

   GOOGLE_CLOUD_PROJECT=""

   GOOGLE_CLOUD_LOCATION=""
   ```

4. **Start the Development Server:**
   ```bash
   # Using uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   ```

5. **Verify Installation:**
   ```bash
   curl http://localhost:8000/health
   ```

### 📖 API Documentation

Once the server is running, access the interactive API documentation:

- **Core Teacher Workflow API**: http://localhost:8000/adk/docs
- **WebSocket & Advanced Features**: http://localhost:8000/docs

## 🧪 Testing the Backend Features

### 🔐 Authentication Testing

#### 1. Create a Test User Account
```bash
curl -X POST "http://localhost:8000/adk/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@test.com",
    "password": "teacher123",
    "role": "teacher",
    "first_name": "Test",
    "last_name": "Teacher"
  }'
```

#### 2. Get Firebase ID Token for Authentication

Open `app/get_id_token.html` in your browser:
1. Configure Firebase credentials in the HTML file
2. Use the test account credentials to get an ID token
3. Copy the generated token for API testing

#### 3. Verify Token
```bash
curl -X GET "http://localhost:8000/adk/v1/auth/verify-token" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

### 👥 Student Management Testing

#### 1. Upload Students via CSV
```bash
# Create a test CSV file
echo "first_name,last_name,grade,password" > test_students.csv
echo "Alice,Johnson,5,student123" >> test_students.csv
echo "Bob,Smith,5,student123" >> test_students.csv

# Upload the CSV
curl -X POST "http://localhost:8000/adk/v1/students/upload-csv" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -F "file=@test_students.csv"
```

#### 2. List Students
```bash
curl -X GET "http://localhost:8000/adk/v1/students/" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

### 📚 Assessment System Testing

#### 1. Create Assessment Configuration
```bash
curl -X POST "http://localhost:8000/adk/v1/assessments/configs" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Math Basics Test",
    "subject": "Mathematics",
    "target_grade": 5,
    "difficulty_level": "medium",
    "topic": "Addition and Subtraction"
  }'
```

#### 2. Generate Assessment from Config
```bash
curl -X POST "http://localhost:8000/adk/v1/assessments/configs/{config_id}/generate" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

### 🤖 AI Learning Path Testing

#### 1. Start Learning Path Monitoring
```bash
curl -X POST "http://localhost:8000/adk/v1/learning/start-monitoring" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 2. Analyze Student Assessment
```bash
curl -X POST "http://localhost:8000/adk/v1/learning/analyze-assessment" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STUDENT_ID",
    "assessment_data": {
      "subject": "Mathematics",
      "grade": 5,
      "score": 75,
      "total_questions": 10,
      "correct_answers": 7,
      "topics_covered": ["addition", "subtraction"],
      "time_taken": 300
    }
  }'
```

#### 3. Generate Learning Path
```bash
curl -X POST "http://localhost:8000/adk/v1/learning/generate-learning-path" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STUDENT_ID",
    "target_subject": "Mathematics",
    "target_grade": 5,
    "identified_gaps": ["multiplication", "division"],
    "learning_style": "visual",
    "time_constraint_weeks": 4
  }'
```

### 📄 Document Processing Testing

#### 1. Upload Document for RAG Indexing
```bash
curl -X POST "http://localhost:8000/adk/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -F "file=@sample_textbook.pdf" \
  -F "subject=Mathematics" \
  -F "grade_level=5"
```

#### 2. Check Document Indexing Status
```bash
curl -X GET "http://localhost:8000/adk/v1/documents/status/{document_id}" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

#### 3. List Uploaded Documents
```bash
curl -X GET "http://localhost:8000/adk/v1/documents/list" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

### 📖 Lesson Generation Testing

#### 1. Create Lesson from Learning Step
```bash
curl -X POST "http://localhost:8000/adk/v1/lessons/lessons/create-from-step" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STUDENT_ID",
    "learning_step_id": "LEARNING_STEP_ID",
    "lesson_request": {
      "topic": "Multiplication Tables",
      "grade_level": 5,
      "duration_minutes": 30,
      "learning_objectives": ["Master 5x table", "Understand patterns"]
    }
  }'
```

#### 2. Get Lesson Content
```bash
curl -X GET "http://localhost:8000/adk/v1/lessons/lessons/{lesson_id}" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

### 🎙️ Voice Interactive Viva Testing

#### 1. Test WebSocket Connection
Use a WebSocket client or browser JavaScript:

```javascript
const ws = new WebSocket('ws://localhost:8000/viva/test-session/speak?token=YOUR_ID_TOKEN&language=english&topic=algebra');

ws.onopen = function() {
    console.log('Connected to Viva WebSocket');
    
    // Send audio data (simulated)
    ws.send(JSON.stringify({
        type: 'audio',
        data: 'base64-encoded-audio-data'
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('Received:', response);
};
```

#### 2. Start Viva Session
```bash
curl -X POST "http://localhost:8000/viva/test-session/start?token=YOUR_ID_TOKEN" \
  -H "Content-Type: application/json"
```

### 🤖 Agent Interaction Testing

#### 1. Invoke Teacher Agent
```bash
curl -X POST "http://localhost:8000/adk/v1/agent/invoke" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Help me create a learning plan for my Grade 5 mathematics class focusing on multiplication"
  }'
```

### 📊 Analytics and Health Checks

#### 1. Get Student Progress Summary
```bash
curl -X GET "http://localhost:8000/adk/v1/students/stats/summary" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

#### 2. Check Service Health
```bash
# Main health check
curl -X GET "http://localhost:8000/health"

# ADK app health check
curl -X GET "http://localhost:8000/adk/health"

# Agent service health
curl -X GET "http://localhost:8000/adk/v1/agent/health"
```

## 🧩 Core API Modules

### 1. Authentication (`/v1/auth`)
- User signup, profile management
- Firebase token validation
- Role-based access control

### 2. Student Management (`/v1/students`)
- Bulk CSV upload
- Individual student profiles
- Progress tracking

### 3. Assessment System (`/v1/assessments`)
- Configuration management
- Question generation
- Performance analysis

### 4. Learning Paths (`/v1/learning`)
- AI-powered path generation
- Progress monitoring
- Adaptive recommendations

### 5. Lesson Management (`/v1/lessons`)
- Rapid lesson creation
- Content delivery
- Interactive chatbots

### 6. Document Processing (`/v1/documents`)
- RAG-powered indexing
- Multi-format support
- Content retrieval

### 7. Voice Interaction (`/viva`)
- Real-time WebSocket communication
- Speech recognition and generation
- Interactive assessment

## 🛡️ Security Features

- **Firebase Authentication** - Secure user management
- **Token-based Authorization** - JWT validation for all endpoints
- **Role-based Access Control** - Teacher/student permissions
- **Data Isolation** - User-specific data access
- **Input Validation** - Comprehensive request validation
- **Rate Limiting** - API abuse prevention

## 🔧 Development Tools

### Environment Management
```bash
# Development mode
export ENVIRONMENT=development

# Production mode
export ENVIRONMENT=production
```

### Database Management
```bash
# Check Firestore connection
python -c "from app.core.firebase import db; print(db.collection('users').limit(1).get())"
```

### Service Testing
```bash
# Test Gemini Live service
python test_gemini_live.py

# Test Viva learning steps
python test_viva_learning_steps.py
```

## 📁 Project Structure

```
edvance-ai-backend/
├── app/
│   ├── main.py                 # Application entry point
│   ├── agents/                 # AI agent implementations
│   ├── api/v1/                # REST API endpoints
│   ├── core/                  # Core configuration and utilities
│   ├── models/                # Data models and schemas
│   └── services/              # Business logic services
├── chroma_db/                 # Vector database storage
├── requirements.txt           # Python dependencies
├── svc-acc-key.json          # Google Cloud service account
└── test_*.py                 # Test scripts
```

## 📞 Support

For technical support or questions about the Edvance AI platform:

- **Documentation**: http://localhost:8000/adk/docs
- **Health Status**: http://localhost:8000/health
- **Service Status**: All endpoints include health check capabilities

---

*Built with ❤️ using Google AI technologies for the future of education*
