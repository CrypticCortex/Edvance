// API Configuration
export const API_BASE_URL = 'http://localhost:8000/adk';

export const API_ENDPOINTS = {
  // Authentication
  auth: {
    signup: '/v1/auth/signup',
    me: '/v1/auth/me',
    updateProfile: '/v1/auth/me/profile',
    verifyToken: '/v1/auth/verify-token'
  },
  
  // Students
  students: {
    uploadCsv: '/v1/students/upload-csv',
    list: '/v1/students/',
    getById: (id: string) => `/v1/students/${id}`,
    updateSubjects: (id: string) => `/v1/students/${id}/subjects`,
    delete: (id: string) => `/v1/students/${id}`,
    stats: '/v1/students/stats/summary'
  },
  
  // Learning Paths & Assessment Analysis
  learning: {
    startMonitoring: '/v1/learning/start-monitoring',
    analyzeAssessment: '/v1/learning/analyze-assessment',
    generatePath: '/v1/learning/generate-learning-path',
    studentProgress: (id: string) => `/v1/learning/student/${id}/progress`,
    studentPaths: (id: string) => `/v1/learning/student/${id}/learning-paths`,
    pathDetails: (id: string) => `/v1/learning/learning-path/${id}`,
    adaptPath: (id: string) => `/v1/learning/adapt-learning-path/${id}`,
    teacherAnalytics: '/v1/learning/teacher/learning-analytics',
    studentInsights: (id: string) => `/v1/learning/student/${id}/learning-insights`
  },
  
  // Lessons
  lessons: {
    createFromStep: '/v1/lessons/lessons/create-from-step',
    getLesson: (id: string) => `/v1/lessons/lessons/${id}`,
    updateProgress: (id: string) => `/v1/lessons/lessons/${id}/progress`,
    startChat: (id: string) => `/v1/lessons/lessons/${id}/chat/start`,
    sendMessage: (sessionId: string) => `/v1/lessons/lessons/chat/${sessionId}/message`,
    studentLessons: (id: string) => `/v1/lessons/lessons/student/${id}`,
    analytics: (id: string) => `/v1/lessons/lessons/${id}/analytics`,
    regenerateSlide: (id: string) => `/v1/lessons/lessons/${id}/regenerate-slide`
  },
  
  // Documents
  documents: {
    upload: '/v1/documents/upload',
    status: (id: string) => `/v1/documents/status/${id}`,
    list: '/v1/documents/list',
    delete: (id: string) => `/v1/documents/${id}`,
    organized: '/v1/documents/organized'
  },
  
  // Assessments
  assessments: {
    createConfig: '/v1/assessments/configs',
    getConfigs: '/v1/assessments/configs',
    generateFromConfig: (id: string) => `/v1/assessments/configs/${id}/generate`,
    getAssessment: (id: string) => `/v1/assessments/${id}`,
    getTopics: (subject: string, grade: number) => `/v1/assessments/topics/${subject}/${grade}`
  },
  
  // Agent
  agent: {
    invoke: '/v1/agent/invoke',
    health: '/v1/agent/health'
  },
  
  // Health
  health: '/health'
};

export default API_ENDPOINTS;