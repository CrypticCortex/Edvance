"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import {
    BookOpen,
    Target,
    Clock,
    CheckCircle,
    AlertCircle,
    Play,
    Eye,
    User,
    TrendingUp,
    Award,
    Calendar,
    BarChart3,
    LogOut,
    BrainCircuit,
    BookMarked,
    GraduationCap,
    RefreshCw
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"
import { useLanguage } from "@/contexts/LanguageContext"
import { LanguageSelector } from "@/components/ui/language-selector"
import { apiService, handleApiError } from "@/lib/api"

interface StudentData {
    student_id: string
    first_name: string
    last_name: string
    grade: number
    email?: string
    subjects?: string[]
    current_learning_paths?: Record<string, string>
    completed_assessments?: string[]
    performance_metrics?: Record<string, any>
    created_at?: string
    last_login?: string
}

interface Assessment {
    assessment_id: string
    title: string
    subject: string
    grade: number
    difficulty: string
    topic: string
    questions: AssessmentQuestion[]
    time_limit_minutes: number
    created_at: string
    is_active: boolean
    result?: AssessmentResult
}

interface AssessmentQuestion {
    question_id: string
    question_text: string
    options: string[]
    correct_answer: number
    explanation: string
    difficulty: string
    topic: string
}

interface AssessmentResult {
    result_id: string
    student_id: string
    assessment_id: string
    answers: number[]
    score: number
    total_questions: number
    percentage: number
    time_taken_minutes: number
    submitted_at: string
    strengths: string[]
    weaknesses: string[]
    recommended_learning_path?: string
}

interface LearningPath {
    path_id: string
    title: string
    description: string
    subject: string
    target_grade: number
    learning_goals: string[]
    total_estimated_duration_minutes: number
    completion_percentage: number
    current_step: number
    steps: LearningStep[]
    started_at?: string
    completed_at?: string
    created_at: string
    last_updated: string
}

interface LearningStep {
    step_id: string
    title: string
    description: string
    content_type: string
    estimated_duration_minutes: number
    is_completed: boolean
    completed_at?: string
}

interface StudentProgress {
    student_id: string
    overall_progress: number
    subject_progress: Record<string, number>
    recent_activity: Activity[]
    learning_streaks: Record<string, number>
    total_study_time_minutes: number
    assessments_completed: number
    current_learning_paths: number
}

interface Activity {
    activity_id: string
    type: string
    title: string
    subject: string
    timestamp: string
    details: string
}

interface StudentInsights {
    student_id: string
    strengths: string[]
    areas_for_improvement: string[]
    learning_recommendations: string[]
    knowledge_gaps: KnowledgeGap[]
    performance_trends: Record<string, any>
    next_suggested_activities: string[]
}

interface KnowledgeGap {
    gap_id: string
    subject: string
    topic: string
    subtopic?: string
    severity_score: number
    confidence_score: number
}

export default function StudentDashboard() {
    const [activeTab, setActiveTab] = useState("overview")
    const [studentData, setStudentData] = useState<StudentData | null>(null)
    const [progress, setProgress] = useState<StudentProgress | null>(null)
    const [learningPaths, setLearningPaths] = useState<LearningPath[]>([])
    const [insights, setInsights] = useState<StudentInsights | null>(null)
    const [assessments, setAssessments] = useState<Assessment[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const { toast } = useToast()
    const { currentLanguage } = useLanguage()
    const router = useRouter()

    useEffect(() => {
        // Debug: Check auth state on mount
        apiService.debugAuthState();

        // Check if user is authenticated as student
        const studentToken = localStorage.getItem('student_token')
        if (!studentToken) {
            console.warn('No student token found, redirecting to login');
            router.push('/auth/login')
            return
        }

        loadStudentData()
    }, [router])

    const loadStudentData = async () => {
        try {
            setLoading(true)
            setError(null)

            console.log('Loading student data...');
            apiService.debugAuthState();

            // Get student data from localStorage
            const storedData = localStorage.getItem('student_data')
            if (!storedData) {
                console.error('No student data found in localStorage');
                router.push('/auth/login')
                return
            }

            const student = JSON.parse(storedData)
            const studentId = student.student_id
            console.log('Student ID:', studentId);

            // Fetch all student dashboard data from the backend
            const dashboardData = await apiService.getStudentDashboardData(studentId)

            console.log('Dashboard data loaded:', dashboardData);

            setStudentData(dashboardData.student as StudentData)
            setProgress(dashboardData.progress as StudentProgress)
            setLearningPaths(dashboardData.learningPaths as LearningPath[] || [])
            setInsights(dashboardData.insights as StudentInsights)

            // Load assessments using the new student assessment endpoints
            await loadStudentAssessments()

        } catch (error: any) {
            console.error('Error loading student data:', error)
            setError('Failed to load student data. Please try again.')

            toast({
                title: "Error",
                description: "Failed to load student data from server",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    const loadStudentAssessments = async () => {
        try {
            console.log('Loading student assessments...')

            // Get student data from localStorage to check subjects and grade
            const storedData = localStorage.getItem('student_data')
            if (!storedData) {
                setAssessments([])
                return
            }

            const student = JSON.parse(storedData)

            try {
                // Try to fetch assessments using the new student assessment endpoint
                console.log('Attempting to fetch assessments from API...')
                const assessments = await apiService.getMyAssessments()
                console.log('Loaded assessments from API:', assessments)

                // Ensure we have an array of assessments
                if (Array.isArray(assessments)) {
                    setAssessments(assessments as Assessment[])
                    return
                } else {
                    console.warn('Assessments response is not an array:', assessments)
                }
            } catch (apiError: any) {
                console.warn('API call failed:', apiError.message)

                // Show specific error messages based on the error type
                if (apiError.message.includes('Authentication required') ||
                    apiError.message.includes('401') ||
                    apiError.message.includes('403') ||
                    apiError.message.includes('Forbidden')) {

                    toast({
                        title: "Authentication Issue",
                        description: "Student assessment API requires authentication setup. Using demo data for now.",
                        variant: "default"
                    })
                } else {
                    toast({
                        title: "API Connection Issue",
                        description: "Could not connect to assessment service. Using demo data.",
                        variant: "default"
                    })
                }
            }

            // Create demo assessments based on student's subjects
            console.log('Using demo assessments based on student data:', student)
            const subjects = student.subjects || []
            const grade = student.grade

            if (!subjects.length || !grade) {
                console.warn('No subjects or grade found for student:', student)
                setAssessments([])
                return
            }

            // Create demo assessments based on student's subjects
            const subjectTopics: Record<string, string[]> = {
                'Mathematics': ['Algebra', 'Geometry', 'Calculus', 'Statistics', 'Trigonometry'],
                'Science': ['Physics', 'Chemistry', 'Biology', 'Earth Science', 'Astronomy'],
                'English': ['Literature', 'Grammar', 'Writing', 'Reading Comprehension', 'Poetry'],
                'History': ['World History', 'Ancient Civilizations', 'Modern History', 'Geography', 'Social Studies'],
                'Computer Science': ['Programming', 'Algorithms', 'Data Structures', 'Web Development', 'Databases']
            }

            const demoAssessments: Assessment[] = subjects.flatMap((subject: string) => {
                const topics = subjectTopics[subject] || ['General Topics', 'Practice Test', 'Review']

                return topics.map((topic: string, index: number) => ({
                    assessment_id: `demo_${subject.toLowerCase().replace(/\s+/g, '_')}_${topic.toLowerCase().replace(/\s+/g, '_')}_${index}`,
                    title: `${topic} Assessment`,
                    subject: subject,
                    grade: grade,
                    difficulty: index % 3 === 0 ? 'easy' : index % 3 === 1 ? 'medium' : 'hard',
                    topic: topic,
                    questions: [], // Empty for now, would be filled when student takes the assessment
                    time_limit_minutes: 30 + (index * 10), // Vary time limits
                    created_at: new Date().toISOString(),
                    is_active: true
                }))
            })

            console.log('Using demo assessments:', demoAssessments)
            setAssessments(demoAssessments)

        } catch (error: any) {
            console.error('Error loading student assessments:', error)

            // If everything fails, show empty state
            setAssessments([])

            toast({
                title: "Error",
                description: "Could not load assessments. Please try refreshing.",
                variant: "destructive"
            })
        }
    }

    const handleLogout = async () => {
        try {
            await apiService.logout();
            toast({
                title: "Logged Out",
                description: "You have been successfully logged out",
            })
        } catch (error) {
            console.error('Logout error:', error);
            // Clear local storage manually if API logout fails
            apiService.clearStudentAuth();
        } finally {
            router.push('/auth/login')
        }
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="h-4 w-4 text-green-600" />
            case 'in_progress':
                return <Play className="h-4 w-4 text-blue-600" />
            default:
                return <AlertCircle className="h-4 w-4 text-gray-400" />
        }
    }

    const getStatusBadge = (completionPercentage: number) => {
        if (completionPercentage >= 100) {
            return <Badge className="bg-green-100 text-green-800">Completed</Badge>
        } else if (completionPercentage > 0) {
            return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>
        } else {
            return <Badge variant="outline">Not Started</Badge>
        }
    }

    const formatDuration = (minutes: number): string => {
        if (minutes < 60) {
            return `${minutes} min`
        }
        const hours = Math.floor(minutes / 60)
        const remainingMinutes = minutes % 60
        return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
    }

    const formatDate = (dateString: string): string => {
        try {
            return new Date(dateString).toLocaleDateString()
        } catch {
            return 'N/A'
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading your dashboard...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Dashboard</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <Button onClick={loadStudentData}>Try Again</Button>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-4">
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <User className="h-8 w-8 text-blue-600" />
                                <div>
                                    <h1 className="text-2xl font-bold text-gray-900">Student Dashboard</h1>
                                    <p className="text-sm text-gray-600">
                                        Welcome back, {studentData?.first_name} {studentData?.last_name}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4">
                            <LanguageSelector variant="compact" />
                            <div className="text-right">
                                <p className="text-sm font-medium text-gray-900">Grade {studentData?.grade}</p>
                                <p className="text-xs text-gray-500">ID: {studentData?.student_id}</p>
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleLogout}
                            >
                                <LogOut className="h-4 w-4 mr-2" />
                                Logout
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="overview" className="flex items-center space-x-2">
                            <BarChart3 className="h-4 w-4" />
                            <span>Overview</span>
                        </TabsTrigger>
                        <TabsTrigger value="learning-paths" className="flex items-center space-x-2">
                            <Target className="h-4 w-4" />
                            <span>Learning Paths</span>
                        </TabsTrigger>
                        <TabsTrigger value="assessments" className="flex items-center space-x-2">
                            <BookMarked className="h-4 w-4" />
                            <span>Assessments</span>
                        </TabsTrigger>
                    </TabsList>

                    {/* Overview Tab */}
                    <TabsContent value="overview" className="space-y-6">
                        {/* Stats Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm font-medium text-gray-600">Learning Paths</p>
                                            <p className="text-3xl font-bold">{learningPaths?.length || 0}</p>
                                            <p className="text-sm text-gray-500">Total enrolled</p>
                                        </div>
                                        <Target className="h-8 w-8 text-blue-600" />
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm font-medium text-gray-600">Overall Progress</p>
                                            <p className="text-3xl font-bold">{Math.round(progress?.overall_progress || 0)}%</p>
                                            <p className="text-sm text-gray-500">Completion rate</p>
                                        </div>
                                        <TrendingUp className="h-8 w-8 text-green-600" />
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm font-medium text-gray-600">Study Time</p>
                                            <p className="text-3xl font-bold">
                                                {formatDuration(progress?.total_study_time_minutes || 0)}
                                            </p>
                                            <p className="text-sm text-gray-500">Total time</p>
                                        </div>
                                        <Clock className="h-8 w-8 text-purple-600" />
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm font-medium text-gray-600">Assessments</p>
                                            <p className="text-3xl font-bold">{progress?.assessments_completed || 0}</p>
                                            <p className="text-sm text-gray-500">Completed</p>
                                        </div>
                                        <Award className="h-8 w-8 text-yellow-600" />
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Subject Progress */}
                        {progress?.subject_progress && Object.keys(progress.subject_progress).length > 0 && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Subject Progress</CardTitle>
                                    <CardDescription>Your progress across different subjects</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {Object.entries(progress.subject_progress).map(([subject, progressValue]) => (
                                            <div key={subject} className="space-y-2">
                                                <div className="flex justify-between text-sm">
                                                    <span className="font-medium">{subject}</span>
                                                    <span className="text-gray-500">{Math.round(progressValue)}%</span>
                                                </div>
                                                <Progress value={progressValue} className="h-2" />
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Recent Activity */}
                        {progress?.recent_activity && progress.recent_activity.length > 0 && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Recent Activity</CardTitle>
                                    <CardDescription>Your latest learning activities</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        {progress.recent_activity.slice(0, 5).map((activity) => (
                                            <div key={activity.activity_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                                <div className="flex items-center space-x-3">
                                                    <BookOpen className="h-5 w-5 text-blue-600" />
                                                    <div>
                                                        <p className="font-medium text-sm">{activity.title}</p>
                                                        <p className="text-xs text-gray-500">{activity.subject} • {activity.details}</p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-xs text-gray-500">{formatDate(activity.timestamp)}</p>
                                                    <Badge variant="outline" className="text-xs">{activity.type}</Badge>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </TabsContent>

                    {/* Learning Paths Tab */}
                    <TabsContent value="learning-paths" className="space-y-6">
                        {learningPaths && learningPaths.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {learningPaths.map((path) => (
                                    <Card key={path.path_id} className="hover:shadow-lg transition-shadow">
                                        <CardHeader>
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <CardTitle className="text-lg">{path.title}</CardTitle>
                                                    <CardDescription className="mt-1">{path.description}</CardDescription>
                                                </div>
                                                {getStatusBadge(path.completion_percentage)}
                                            </div>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="space-y-4">
                                                <div className="flex items-center justify-between text-sm">
                                                    <span className="text-gray-600">Progress</span>
                                                    <span className="font-medium">{Math.round(path.completion_percentage)}%</span>
                                                </div>
                                                <Progress value={path.completion_percentage} className="h-2" />

                                                <div className="grid grid-cols-2 gap-4 text-sm">
                                                    <div>
                                                        <p className="text-gray-600">Subject</p>
                                                        <p className="font-medium">{path.subject}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-gray-600">Duration</p>
                                                        <p className="font-medium">{formatDuration(path.total_estimated_duration_minutes)}</p>
                                                    </div>
                                                </div>

                                                <div className="flex items-center justify-between text-sm">
                                                    <span className="text-gray-600">Steps</span>
                                                    <span className="font-medium">{path.current_step + 1} of {path.steps?.length || 0}</span>
                                                </div>

                                                {path.learning_goals && path.learning_goals.length > 0 && (
                                                    <div>
                                                        <p className="text-sm text-gray-600 mb-2">Learning Goals:</p>
                                                        <div className="space-y-1">
                                                            {path.learning_goals.slice(0, 2).map((goal, index) => (
                                                                <p key={index} className="text-xs text-gray-500">• {goal}</p>
                                                            ))}
                                                            {path.learning_goals.length > 2 && (
                                                                <p className="text-xs text-gray-400">+ {path.learning_goals.length - 2} more goals</p>
                                                            )}
                                                        </div>
                                                    </div>
                                                )}

                                                <div className="flex space-x-2 pt-2">
                                                    <Button size="sm" className="flex-1">
                                                        <Play className="h-3 w-3 mr-1" />
                                                        Continue
                                                    </Button>
                                                    <Button size="sm" variant="outline">
                                                        <Eye className="h-3 w-3" />
                                                    </Button>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        ) : (
                            <Card>
                                <CardContent className="p-12 text-center">
                                    <BookMarked className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Learning Paths Yet</h3>
                                    <p className="text-gray-500 mb-4">
                                        Your teacher hasn't assigned any learning paths yet, or they haven't been generated based on your assessments.
                                    </p>
                                    <Button variant="outline">
                                        <Target className="h-4 w-4 mr-2" />
                                        Request Learning Path
                                    </Button>
                                </CardContent>
                            </Card>
                        )}
                    </TabsContent>

                    {/* Assessments Tab */}
                    <TabsContent value="assessments" className="space-y-6">
                        {assessments && assessments.length > 0 ? (
                            <>
                                {/* Demo Data Notice */}
                                {assessments.some(a => a.assessment_id.startsWith('demo_')) && (
                                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                        <div className="flex items-center">
                                            <BrainCircuit className="h-5 w-5 text-blue-600 mr-2" />
                                            <div>
                                                <h3 className="text-sm font-medium text-blue-800">Demo Assessment Data</h3>
                                                <p className="text-sm text-blue-700 mt-1">
                                                    These are demonstration assessments based on your enrolled subjects.
                                                    Your teacher can create real assessments through the teacher dashboard.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Assessment Statistics */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    <Card>
                                        <CardHeader className="pb-2">
                                            <CardTitle className="text-lg">Total Assessments</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="text-3xl font-bold text-blue-600">{assessments.length}</div>
                                            <p className="text-sm text-gray-600">Available for you</p>
                                        </CardContent>
                                    </Card>

                                    <Card>
                                        <CardHeader className="pb-2">
                                            <CardTitle className="text-lg">Completed</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="text-3xl font-bold text-green-600">
                                                {assessments.filter(a => a.result).length}
                                            </div>
                                            <p className="text-sm text-gray-600">Assessments finished</p>
                                        </CardContent>
                                    </Card>

                                    <Card>
                                        <CardHeader className="pb-2">
                                            <CardTitle className="text-lg">Average Score</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="text-3xl font-bold text-purple-600">
                                                {assessments.filter(a => a.result).length > 0
                                                    ? Math.round(assessments
                                                        .filter(a => a.result)
                                                        .reduce((sum, a) => sum + (a.result?.percentage || 0), 0) /
                                                        assessments.filter(a => a.result).length)
                                                    : 0}%
                                            </div>
                                            <p className="text-sm text-gray-600">Overall performance</p>
                                        </CardContent>
                                    </Card>
                                </div>

                                {/* Assessments List */}
                                <Card>
                                    <CardHeader>
                                        <CardTitle>Your Assessments</CardTitle>
                                        <CardDescription>Track your progress and scores across all assessments</CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        {/* Group assessments by subject */}
                                        {Object.entries(
                                            assessments.reduce((acc, assessment) => {
                                                if (!acc[assessment.subject]) {
                                                    acc[assessment.subject] = []
                                                }
                                                acc[assessment.subject].push(assessment)
                                                return acc
                                            }, {} as Record<string, Assessment[]>)
                                        ).map(([subject, subjectAssessments]) => (
                                            <div key={subject} className="mb-8">
                                                <div className="flex items-center mb-4">
                                                    <GraduationCap className="h-5 w-5 text-blue-600 mr-2" />
                                                    <h3 className="text-lg font-semibold text-gray-900">{subject}</h3>
                                                    <Badge variant="secondary" className="ml-2">
                                                        {subjectAssessments.length} assessments
                                                    </Badge>
                                                </div>

                                                <div className="space-y-4 pl-4">
                                                    {subjectAssessments.map((assessment) => (
                                                        <div key={assessment.assessment_id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                                                            <div className="flex items-start justify-between">
                                                                <div className="flex-1">
                                                                    <div className="flex items-center space-x-3 mb-2">
                                                                        <BookMarked className="h-5 w-5 text-blue-600" />
                                                                        <h4 className="font-semibold text-lg">{assessment.title}</h4>
                                                                        {assessment.result ? (
                                                                            <Badge className="bg-green-100 text-green-800">
                                                                                <CheckCircle className="h-3 w-3 mr-1" />
                                                                                Completed
                                                                            </Badge>
                                                                        ) : (
                                                                            <Badge variant="outline">
                                                                                <Clock className="h-3 w-3 mr-1" />
                                                                                Available
                                                                            </Badge>
                                                                        )}
                                                                    </div>

                                                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-3">
                                                                        <div>
                                                                            <p className="text-sm font-medium text-gray-600">Topic</p>
                                                                            <p className="text-sm text-gray-900">{assessment.topic}</p>
                                                                        </div>
                                                                        <div>
                                                                            <p className="text-sm font-medium text-gray-600">Difficulty</p>
                                                                            <Badge variant={assessment.difficulty === 'easy' ? 'default' : assessment.difficulty === 'medium' ? 'secondary' : 'destructive'}>
                                                                                {assessment.difficulty}
                                                                            </Badge>
                                                                        </div>
                                                                        <div>
                                                                            <p className="text-sm font-medium text-gray-600">Time Limit</p>
                                                                            <p className="text-sm text-gray-900">{assessment.time_limit_minutes} min</p>
                                                                        </div>
                                                                    </div>

                                                                    {assessment.result && (
                                                                        <div className="bg-blue-50 rounded-lg p-3 mb-3">
                                                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                                                <div>
                                                                                    <p className="text-sm font-medium text-blue-700">Score</p>
                                                                                    <p className="text-lg font-bold text-blue-900">
                                                                                        {assessment.result.score}/{assessment.result.total_questions}
                                                                                    </p>
                                                                                </div>
                                                                                <div>
                                                                                    <p className="text-sm font-medium text-blue-700">Percentage</p>
                                                                                    <p className="text-lg font-bold text-blue-900">{assessment.result.percentage}%</p>
                                                                                </div>
                                                                                <div>
                                                                                    <p className="text-sm font-medium text-blue-700">Time Taken</p>
                                                                                    <p className="text-lg font-bold text-blue-900">{assessment.result.time_taken_minutes} min</p>
                                                                                </div>
                                                                                <div>
                                                                                    <p className="text-sm font-medium text-blue-700">Completed</p>
                                                                                    <p className="text-sm text-blue-900">
                                                                                        {new Date(assessment.result.submitted_at).toLocaleDateString()}
                                                                                    </p>
                                                                                </div>
                                                                            </div>

                                                                            {/* Strengths and Weaknesses */}
                                                                            {(assessment.result.strengths.length > 0 || assessment.result.weaknesses.length > 0) && (
                                                                                <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                                                                                    {assessment.result.strengths.length > 0 && (
                                                                                        <div>
                                                                                            <p className="text-sm font-medium text-green-700 mb-1">Strengths</p>
                                                                                            <div className="space-y-1">
                                                                                                {assessment.result.strengths.map((strength, idx) => (
                                                                                                    <div key={idx} className="flex items-center text-sm text-green-800">
                                                                                                        <CheckCircle className="h-3 w-3 mr-1" />
                                                                                                        {strength}
                                                                                                    </div>
                                                                                                ))}
                                                                                            </div>
                                                                                        </div>
                                                                                    )}

                                                                                    {assessment.result.weaknesses.length > 0 && (
                                                                                        <div>
                                                                                            <p className="text-sm font-medium text-orange-700 mb-1">Areas to Improve</p>
                                                                                            <div className="space-y-1">
                                                                                                {assessment.result.weaknesses.map((weakness, idx) => (
                                                                                                    <div key={idx} className="flex items-center text-sm text-orange-800">
                                                                                                        <AlertCircle className="h-3 w-3 mr-1" />
                                                                                                        {weakness}
                                                                                                    </div>
                                                                                                ))}
                                                                                            </div>
                                                                                        </div>
                                                                                    )}
                                                                                </div>
                                                                            )}
                                                                        </div>
                                                                    )}
                                                                </div>

                                                                <div className="flex flex-col space-y-2 ml-4">
                                                                    {assessment.result ? (
                                                                        <Button variant="outline" size="sm">
                                                                            <Eye className="h-4 w-4 mr-2" />
                                                                            Review
                                                                        </Button>
                                                                    ) : (
                                                                        <Button
                                                                            size="sm"
                                                                            onClick={async () => {
                                                                                try {
                                                                                    toast({
                                                                                        title: "Loading Assessment",
                                                                                        description: `Preparing ${assessment.title}...`,
                                                                                    })

                                                                                    // Fetch the full assessment details
                                                                                    const fullAssessment = await apiService.getMyAssessment(assessment.assessment_id)
                                                                                    console.log('Full assessment details:', fullAssessment)

                                                                                    // TODO: Navigate to assessment taking page
                                                                                    // router.push(`/assessment/${assessment.assessment_id}`)

                                                                                    toast({
                                                                                        title: "Assessment Ready",
                                                                                        description: `${assessment.title} is ready to start.`,
                                                                                    })
                                                                                } catch (error: any) {
                                                                                    toast({
                                                                                        title: "Error",
                                                                                        description: "Failed to load assessment details",
                                                                                        variant: "destructive"
                                                                                    })
                                                                                }
                                                                            }}
                                                                        >
                                                                            <Play className="h-4 w-4 mr-2" />
                                                                            Start
                                                                        </Button>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </CardContent>
                                </Card>
                            </>
                        ) : (
                            <Card>
                                <CardContent className="p-12 text-center">
                                    <BookMarked className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Assessments Available</h3>
                                    <p className="text-gray-500 mb-4">
                                        No assessments have been assigned to you yet.
                                    </p>
                                    <Button variant="outline" onClick={loadStudentAssessments}>
                                        <RefreshCw className="h-4 w-4 mr-2" />
                                        Refresh Assessments
                                    </Button>
                                </CardContent>
                            </Card>
                        )}
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    )
}
