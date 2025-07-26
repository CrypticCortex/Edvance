// API service layer for Edvance backend integration
interface ApiResponse<T = any> {
    success?: boolean;
    data?: T;
    message?: string;
    error?: string;
}

interface AuthTokens {
    idToken: string;
    refreshToken?: string;
}

class ApiService {
    private baseUrl: string;
    private authTokens: AuthTokens | null = null;

    constructor() {
        this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    }

    // Set authentication tokens
    setAuthTokens(tokens: AuthTokens) {
        this.authTokens = tokens;
        if (typeof window !== 'undefined') {
            localStorage.setItem('auth_tokens', JSON.stringify(tokens));
        }
    }

    // Get authentication tokens
    getAuthTokens(): AuthTokens | null {
        if (this.authTokens) return this.authTokens;

        if (typeof window !== 'undefined') {
            const stored = localStorage.getItem('auth_tokens');
            if (stored) {
                this.authTokens = JSON.parse(stored);
                return this.authTokens;
            }
        }
        return null;
    }

    // Clear authentication tokens
    clearAuthTokens() {
        this.authTokens = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_tokens');
            localStorage.removeItem('teacher_data');
            localStorage.removeItem('teacher_token');
        }
    }

    // Make authenticated API request
    private async makeRequest<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const tokens = this.getAuthTokens();
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string>),
        };

        if (tokens?.idToken) {
            headers['Authorization'] = `Bearer ${tokens.idToken}`;
        }

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                this.clearAuthTokens();
                throw new Error('Authentication required');
            }

            const errorData = await response.json().catch(() => ({}));
            console.error('API Error:', {
                status: response.status,
                statusText: response.statusText,
                errorData,
                endpoint
            });
            throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    }

    // =================================================================
    // AUTHENTICATION APIS
    // =================================================================

    async signup(userData: {
        email: string;
        password: string;
        role: 'teacher' | 'student';
        first_name: string;
        last_name: string;
    }) {
        return this.makeRequest<{
            uid: string;
            email: string;
            created_at: string;
            subjects: string[];
            role: string;
            first_name: string;
            last_name: string;
        }>('/adk/v1/auth/signup', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async getProfile() {
        return this.makeRequest<{
            uid: string;
            email: string;
            created_at: string;
            subjects: string[];
            role: string;
            first_name: string;
            last_name: string;
        }>('/adk/v1/auth/me');
    }

    async updateProfile(profileData: {
        subjects?: string[];
        first_name?: string;
        last_name?: string;
        role?: string;
    }) {
        return this.makeRequest('/adk/v1/auth/me/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData),
        });
    }

    async logout() {
        try {
            await this.makeRequest('/adk/v1/auth/logout', {
                method: 'POST',
            });
        } finally {
            this.clearAuthTokens();
        }
    }

    // =================================================================
    // ASSESSMENT APIS
    // =================================================================

    async createAssessment(assessmentData: {
        title: string;
        subject: string;
        grade: number;
        topics: string[];
        questions: Array<{
            question_text: string;
            options: string[];
            correct_answer: number;
            topic: string;
            difficulty: string;
        }>;
        estimated_duration_minutes: number;
    }) {
        return this.makeRequest('/adk/v1/assessments/enhanced/create', {
            method: 'POST',
            body: JSON.stringify(assessmentData),
        });
    }

    async analyzeAssessment(analysisData: {
        student_id: string;
        assessment_id: string;
        student_answers: number[];
        time_taken_minutes: number;
        submission_timestamp: string;
    }) {
        return this.makeRequest('/adk/v1/learning/analyze-assessment', {
            method: 'POST',
            body: JSON.stringify(analysisData),
        });
    }

    // =================================================================
    // LEARNING PATH APIS
    // =================================================================

    async startMonitoring(teacherUid: string) {
        return this.makeRequest('/adk/v1/learning/start-monitoring', {
            method: 'POST',
            body: JSON.stringify({
                teacher_uid: teacherUid,
                monitoring_activated: true,
                agent_status: 'active',
                automation_features: [
                    'Assessment completion detection',
                    'Automatic performance analysis',
                    'Personalized learning path generation',
                    'Progress monitoring and adaptation',
                    'Real-time intervention recommendations'
                ]
            }),
        });
    }

    async generateLearningPath(pathData: {
        student_id: string;
        target_subject: string;
        target_grade: number;
        learning_goals: string[];
        include_recent_assessments?: number;
    }) {
        return this.makeRequest('/adk/v1/learning/generate-learning-path', {
            method: 'POST',
            body: JSON.stringify(pathData),
        });
    }

    async getLearningPath(pathId: string) {
        return this.makeRequest(`/adk/v1/learning/learning-path/${pathId}`);
    }

    async adaptLearningPath(pathId: string, adaptationData: {
        new_assessment_id: string;
        student_answers: number[];
        time_taken_minutes: number;
    }) {
        return this.makeRequest(`/adk/v1/learning/adapt-learning-path/${pathId}`, {
            method: 'POST',
            body: JSON.stringify(adaptationData),
        });
    }

    // =================================================================
    // LESSON APIS
    // =================================================================

    async createLessonFromStep(lessonData: {
        learning_step_id: string;
        student_id: string;
        customizations: {
            difficulty_adjustment?: 'easier' | 'normal' | 'harder';
            focus_areas?: string[];
            learning_style?: 'visual' | 'auditory' | 'kinesthetic';
            include_interactive?: boolean;
            slide_count_preference?: 'short' | 'medium' | 'long';
            learning_path_context?: {
                path_id: string;
                step_number: number;
                total_steps: number;
                subject: string;
                target_grade: number;
            };
        };
    }) {
        return this.makeRequest('/adk/v1/lessons/create-from-step', {
            method: 'POST',
            body: JSON.stringify(lessonData),
        });
    }

    // =================================================================
    // CHATBOT APIS
    // =================================================================

    async startChatSession(lessonId: string, studentId: string, initialMessage?: string) {
        return this.makeRequest(`/adk/v1/lessons/${lessonId}/chat/start`, {
            method: 'POST',
            body: JSON.stringify({
                student_id: studentId,
                initial_message: initialMessage || 'Hi! I\'m ready to learn.',
            }),
        });
    }

    async sendChatMessage(lessonId: string, messageData: {
        student_id: string;
        session_id: string;
        message: string;
    }) {
        return this.makeRequest(`/adk/v1/lessons/${lessonId}/chat/message`, {
            method: 'POST',
            body: JSON.stringify(messageData),
        });
    }

    // =================================================================
    // PROGRESS & ANALYTICS APIS
    // =================================================================

    async getStudentProgress(studentId: string) {
        return this.makeRequest(`/adk/v1/learning/student/${studentId}/progress`);
    }

    async getTeacherAnalytics() {
        return this.makeRequest('/adk/v1/learning/teacher/learning-analytics');
    }

    async getStudentInsights(studentId: string) {
        return this.makeRequest(`/adk/v1/learning/student/${studentId}/learning-insights`);
    }

    async submitTeacherFeedback(feedbackData: {
        lesson_id: string;
        student_id: string;
        feedback_type: string;
        rating: number;
        comments: string;
        suggestions: string[];
    }) {
        return this.makeRequest('/adk/v1/learning/teacher-feedback', {
            method: 'POST',
            body: JSON.stringify(feedbackData),
        });
    }

    // Health check endpoint
    async checkHealth() {
        return this.makeRequest('/adk/health');
    }

    // Check API status
    async checkApiStatus() {
        try {
            const health = await this.checkHealth();
            return { status: 'connected', health };
        } catch (error: any) {
            return { status: 'disconnected', error: error.message || 'Unknown error' };
        }
    }

    // Document upload (single file with metadata)
    async uploadDocument(file: File, subject: string, gradeLevel: number) {
        const formData = new FormData();

        // Add file and metadata to form data
        formData.append('file', file);
        formData.append('subject', subject);
        formData.append('grade_level', gradeLevel.toString());

        const tokens = this.getAuthTokens();
        const headers: Record<string, string> = {};

        if (tokens?.idToken) {
            headers['Authorization'] = `Bearer ${tokens.idToken}`;
        }

        const response = await fetch(`${this.baseUrl}/adk/v1/documents/upload`, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.clearAuthTokens();
                throw new Error('Authentication required');
            }

            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // Document upload (multiple files - deprecated, keeping for compatibility)
    async uploadDocuments(files: File[]) {
        const formData = new FormData();

        // Add each file to the form data
        files.forEach((file, index) => {
            formData.append(`files`, file);
        });

        const tokens = this.getAuthTokens();
        const headers: Record<string, string> = {};

        if (tokens?.idToken) {
            headers['Authorization'] = `Bearer ${tokens.idToken}`;
        }

        const response = await fetch(`${this.baseUrl}/adk/v1/documents/upload`, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.clearAuthTokens();
                throw new Error('Authentication required');
            }

            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // List uploaded documents
    async listDocuments() {
        return this.makeRequest('/adk/v1/documents/list');
    }

    // =================================================================
    // ASSESSMENT APIS
    // =================================================================

    // Create assessment configuration
    async createAssessmentConfig(configData: {
        name: string;
        subject: string;
        target_grade: number;
        difficulty_level: 'easy' | 'medium' | 'hard';
        topic: string;
        question_count?: number;
        time_limit_minutes?: number;
    }) {
        return this.makeRequest('/adk/v1/assessments/configs', {
            method: 'POST',
            body: JSON.stringify(configData),
        });
    }

    // Generate assessment from configuration
    async generateAssessmentFromConfig(configId: string) {
        return this.makeRequest(`/adk/v1/assessments/configs/${configId}/generate`, {
            method: 'POST',
        });
    }

    // Get assessment configurations
    async getAssessmentConfigs(teacherId?: string) {
        const params = new URLSearchParams();
        if (teacherId) {
            params.append('teacher_id', teacherId);
        }

        const queryString = params.toString();
        const endpoint = queryString ? `/adk/v1/assessments/configs?${queryString}` : '/adk/v1/assessments/configs';

        return this.makeRequest(endpoint);
    }

    // =================================================================
    // STUDENT APIS
    // =================================================================

    // Upload students from CSV file
    async uploadStudentsCSV(file: File): Promise<{
        total_students: number;
        students_created: number;
        students_updated: number;
        students_failed: number;
        failed_students: any[];
        created_student_ids: string[];
        upload_summary: string;
    }> {
        const formData = new FormData();
        formData.append('file', file);

        const tokens = this.getAuthTokens();
        const headers: Record<string, string> = {};

        if (tokens?.idToken) {
            headers['Authorization'] = `Bearer ${tokens.idToken}`;
        }

        const response = await fetch(`${this.baseUrl}/adk/v1/students/upload-csv`, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.clearAuthTokens();
                throw new Error('Authentication required');
            }

            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // Get list of students
    async getStudents(grade?: number, subject?: string) {
        const params = new URLSearchParams();
        if (grade) params.append('grade', grade.toString());
        if (subject) params.append('subject', subject);

        const queryString = params.toString();
        const endpoint = queryString ? `/adk/v1/students/?${queryString}` : '/adk/v1/students/';

        return this.makeRequest(endpoint);
    }

    // Get individual student details
    async getStudent(studentId: string) {
        return this.makeRequest(`/adk/v1/students/${studentId}`);
    }

    // Get student learning paths
    async getStudentLearningPaths(studentId: string) {
        return this.makeRequest(`/adk/v1/learning/student/${studentId}/learning-paths`);
    }

    // Delete student
    async deleteStudent(studentId: string) {
        return this.makeRequest(`/adk/v1/students/${studentId}`, {
            method: 'DELETE',
        });
    }

    // =================================================================
    // AI AGENT APIS
    // =================================================================

    // Invoke AI agent with a message
    async invokeAgent(message: string): Promise<{
        response: string;
        session_id?: string;
        metadata?: any;
    }> {
        return this.makeRequest('/adk/v1/agent/invoke', {
            method: 'POST',
            body: JSON.stringify({
                prompt: message
            }),
        });
    }

    // =================================================================
    // DOCUMENT APIS
    // =================================================================
}

// Create and export singleton instance
export const apiService = new ApiService();

// Helper function to handle API errors
export const handleApiError = (error: any): string => {
    if (error.message === 'Authentication required') {
        // Redirect to login
        if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
        }
        return 'Please log in to continue';
    }

    return error.message || 'An unexpected error occurred';
};

// Helper function to get user data from token
export const getUserFromStorage = () => {
    if (typeof window !== 'undefined') {
        const stored = localStorage.getItem('teacher_data');
        return stored ? JSON.parse(stored) : null;
    }
    return null;
};
