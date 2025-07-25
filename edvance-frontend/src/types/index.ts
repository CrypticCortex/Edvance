// User and Authentication Types
export interface User {
  uid: string;
  email: string;
  created_at: string;
  subjects: string[];
  role: string;
  first_name?: string;
  last_name?: string;
}

export interface UserCreate {
  email: string;
  password: string;
  role?: string;
  first_name?: string;
  last_name?: string;
}

// Student Types
export interface Student {
  student_id: string;
  teacher_uid: string;
  first_name: string;
  last_name: string;
  grade: number;
  default_password: string;
  subjects: string[];
  created_at: string;
  last_login?: string;
  is_active: boolean;
  current_learning_paths: Record<string, string>;
  completed_assessments: string[];
  performance_metrics: Record<string, any>;
}

export interface StudentBatchUploadResponse {
  total_students: number;
  students_created: number;
  students_updated: number;
  students_failed: number;
  failed_students: Array<{
    row: number;
    data: Record<string, any>;
    error: string;
  }>;
  created_student_ids: string[];
  upload_summary: string;
}

// Learning Path Types
export interface LearningStep {
  step_id: string;
  step_number: number;
  title: string;
  description: string;
  subject: string;
  topic: string;
  subtopic?: string;
  difficulty_level: string;
  learning_objective: string;
  content_type: string;
  content_text?: string;
  estimated_duration_minutes: number;
  is_completed: boolean;
  completed_at?: string;
  performance_score?: number;
  has_viva?: boolean;
  viva_session_id?: string;
}

export interface LearningPath {
  path_id: string;
  student_id: string;
  teacher_uid: string;
  title: string;
  description: string;
  subject: string;
  target_grade: number;
  learning_goals: string[];
  steps: LearningStep[];
  completion_percentage: number;
  current_step: number;
  total_steps: number;
  created_at: string;
  estimated_duration_hours: number;
  status: 'not_started' | 'in_progress' | 'completed';
}

// Assessment Types
export interface AssessmentConfig {
  config_id: string;
  teacher_uid: string;
  name: string;
  subject: string;
  target_grade: number;
  difficulty_level: 'easy' | 'medium' | 'hard';
  topic: string;
  question_count: number;
  time_limit_minutes: number;
  created_at: string;
  is_active: boolean;
}

export interface AssessmentQuestion {
  question_id: string;
  question_text: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  difficulty: string;
  topic: string;
}

export interface Assessment {
  assessment_id: string;
  config_id: string;
  teacher_uid: string;
  title: string;
  subject: string;
  grade: number;
  difficulty: string;
  topic: string;
  questions: AssessmentQuestion[];
  time_limit_minutes: number;
  created_at: string;
  is_active: boolean;
}

// Lesson Types
export interface LessonSlide {
  slide_id: string;
  slide_number: number;
  slide_type: string;
  title: string;
  subtitle?: string;
  content_elements: any[];
  learning_objective: string;
  estimated_duration_minutes: number;
  is_interactive: boolean;
  is_completed: boolean;
  completed_at?: string;
}

export interface Lesson {
  lesson_id: string;
  learning_step_id: string;
  student_id: string;
  teacher_uid: string;
  title: string;
  description: string;
  subject: string;
  topic: string;
  grade_level: number;
  slides: LessonSlide[];
  total_slides: number;
  learning_objectives: string[];
  current_slide: number;
  completion_percentage: number;
  started_at?: string;
  completed_at?: string;
  total_time_spent_minutes: number;
}

// Document Types
export interface DocumentMetadata {
  document_id: string;
  teacher_uid: string;
  filename: string;
  file_type: string;
  file_size: number;
  subject: string;
  grade_level: number;
  storage_path: string;
  firebase_url: string;
  upload_date: string;
  indexing_status: 'pending' | 'processing' | 'completed' | 'failed';
  vertex_ai_index_id?: string;
  page_count?: number;
  text_content_preview?: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_size: number;
  file_type: string;
  subject: string;
  grade_level: number;
  upload_status: string;
  storage_url: string;
  created_at: string;
}

// Analytics Types
export interface StudentProgress {
  student_id: string;
  average_score: number;
  score_trend: string;
  total_assessments: number;
  active_knowledge_gaps: number;
  active_recommendations: number;
  subject_performance: Record<string, number>;
  recent_performances: any[];
  priority_gaps: any[];
  top_recommendations: any[];
  last_updated: string;
}

export interface TeacherAnalytics {
  teacher_uid: string;
  total_students_with_paths: number;
  total_active_paths: number;
  average_completion_rate: number;
  most_common_knowledge_gaps: string[];
  subject_performance_trends: Record<string, any>;
  learning_path_effectiveness: {
    paths_completed: number;
    average_improvement: number;
    student_satisfaction: number;
  };
  recommendations_for_teacher: string[];
}

// API Response Types
export interface ApiResponse<T> {
  success?: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Chat Types
export interface ChatMessage {
  message_id: string;
  sender: 'student' | 'agent';
  message: string;
  timestamp: string;
}

export interface ChatSession {
  session_id: string;
  lesson_id: string;
  student_id: string;
  messages: ChatMessage[];
  is_active: boolean;
  started_at: string;
}