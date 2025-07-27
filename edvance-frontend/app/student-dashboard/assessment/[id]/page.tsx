"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, BookOpen, Clock, CheckCircle, AlertCircle, Play, Eye } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"

interface AssessmentQuestion {
    question_id: string
    question_text: string
    options: string[]
    correct_answer: number
    explanation: string
    difficulty: string
    topic: string
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
}

export default function StudentAssessmentViewPage() {
    const params = useParams()
    const router = useRouter()
    const { toast } = useToast()
    const [assessment, setAssessment] = useState<Assessment | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const assessmentId = params.id as string

    useEffect(() => {
        loadAssessment()
    }, [assessmentId])

    const loadAssessment = async () => {
        try {
            setLoading(true)
            setError(null)
            
            console.log('Loading assessment:', assessmentId)
            
            // Try to fetch the assessment details
            const assessmentData = await apiService.getMyAssessment(assessmentId)
            console.log('Assessment data loaded:', assessmentData)
            
            if (assessmentData) {
                setAssessment(assessmentData)
            } else {
                // If API returns null, create demo assessment with questions
                const demoAssessment = createDemoAssessment(assessmentId)
                setAssessment(demoAssessment)
            }
            
        } catch (error: any) {
            console.error('Error loading assessment:', error)
            
            // Create demo assessment as fallback
            const demoAssessment = createDemoAssessment(assessmentId)
            setAssessment(demoAssessment)
            
            toast({
                title: "Demo Mode",
                description: "Showing demo assessment data. Connect to backend for real assessments.",
                variant: "default"
            })
        } finally {
            setLoading(false)
        }
    }

    const createDemoAssessment = (id: string): Assessment => {
        // Extract subject and topic from demo assessment ID
        const parts = id.split('_')
        const subject = parts[1]?.replace(/_/g, ' ') || 'Mathematics'
        const topic = parts[2]?.replace(/_/g, ' ') || 'Algebra'
        
        const demoQuestions: AssessmentQuestion[] = [
            {
                question_id: "q1",
                question_text: `What is the result of solving the equation 2x + 5 = 13?`,
                options: ["x = 3", "x = 4", "x = 5", "x = 6"],
                correct_answer: 1,
                explanation: "To solve 2x + 5 = 13, subtract 5 from both sides to get 2x = 8, then divide by 2 to get x = 4.",
                difficulty: "medium",
                topic: topic
            },
            {
                question_id: "q2",
                question_text: `Which of the following is equivalent to 3(x + 2)?`,
                options: ["3x + 2", "3x + 6", "x + 6", "3x + 5"],
                correct_answer: 1,
                explanation: "Using the distributive property: 3(x + 2) = 3x + 3(2) = 3x + 6.",
                difficulty: "easy",
                topic: topic
            },
            {
                question_id: "q3",
                question_text: `If y = 2x - 3 and x = 5, what is the value of y?`,
                options: ["7", "8", "9", "10"],
                correct_answer: 0,
                explanation: "Substitute x = 5 into y = 2x - 3: y = 2(5) - 3 = 10 - 3 = 7.",
                difficulty: "medium",
                topic: topic
            },
            {
                question_id: "q4",
                question_text: `What is the slope of the line passing through points (2, 3) and (4, 7)?`,
                options: ["1", "2", "3", "4"],
                correct_answer: 1,
                explanation: "Slope = (y2 - y1)/(x2 - x1) = (7 - 3)/(4 - 2) = 4/2 = 2.",
                difficulty: "hard",
                topic: topic
            },
            {
                question_id: "q5",
                question_text: `Which expression represents the area of a rectangle with length (x + 3) and width (x - 1)?`,
                options: ["x² + 2x - 3", "x² + 4x - 3", "x² - 2x - 3", "x² + 2x + 3"],
                correct_answer: 0,
                explanation: "Area = length × width = (x + 3)(x - 1) = x² - x + 3x - 3 = x² + 2x - 3.",
                difficulty: "hard",
                topic: topic
            }
        ]

        return {
            assessment_id: id,
            title: `${topic} Assessment`,
            subject: subject.charAt(0).toUpperCase() + subject.slice(1),
            grade: 8,
            difficulty: "medium",
            topic: topic,
            questions: demoQuestions,
            time_limit_minutes: 30,
            created_at: new Date().toISOString(),
            is_active: true
        }
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        })
    }

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty.toLowerCase()) {
            case 'easy':
                return 'bg-green-100 text-green-800'
            case 'medium':
                return 'bg-yellow-100 text-yellow-800'
            case 'hard':
                return 'bg-red-100 text-red-800'
            default:
                return 'bg-gray-100 text-gray-800'
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading assessment...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Assessment</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <Button onClick={loadAssessment}>Try Again</Button>
                </div>
            </div>
        )
    }

    if (!assessment) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">Assessment Not Found</h2>
                    <p className="text-gray-600 mb-4">The assessment you're looking for doesn't exist.</p>
                    <Button onClick={() => router.push('/student-dashboard')}>Back to Dashboard</Button>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between py-4">
                        <div className="flex items-center space-x-4">
                            <Button variant="ghost" onClick={() => router.push('/student-dashboard')}>
                                <ArrowLeft className="h-4 w-4 mr-2" />
                                Back to Dashboard
                            </Button>
                            <div className="flex items-center space-x-3">
                                <BookOpen className="h-8 w-8 text-blue-600" />
                                <div>
                                    <h1 className="text-2xl font-bold text-gray-900">{assessment.title}</h1>
                                    <p className="text-sm text-gray-600">{assessment.subject} • Grade {assessment.grade}</p>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center space-x-4">
                            <Badge className={getDifficultyColor(assessment.difficulty)}>
                                {assessment.difficulty}
                            </Badge>
                            <div className="text-right">
                                <p className="text-sm font-medium text-gray-900">{assessment.questions.length} Questions</p>
                                <p className="text-xs text-gray-500">{assessment.time_limit_minutes} minutes</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                    {/* Assessment Info Sidebar */}
                    <div className="lg:col-span-1">
                        <Card className="sticky top-8">
                            <CardHeader>
                                <CardTitle>Assessment Info</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Subject</label>
                                    <p className="text-sm text-gray-900">{assessment.subject}</p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Topic</label>
                                    <p className="text-sm text-gray-900">{assessment.topic}</p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Grade Level</label>
                                    <p className="text-sm text-gray-900">Grade {assessment.grade}</p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Questions</label>
                                    <p className="text-sm text-gray-900">{assessment.questions.length} questions</p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Time Limit</label>
                                    <div className="flex items-center space-x-1">
                                        <Clock className="h-4 w-4 text-gray-500" />
                                        <p className="text-sm text-gray-900">{assessment.time_limit_minutes} minutes</p>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Created</label>
                                    <p className="text-sm text-gray-900">{formatDate(assessment.created_at)}</p>
                                </div>
                                
                                <div className="pt-4 border-t">
                                    <Button className="w-full" size="lg">
                                        <Play className="h-4 w-4 mr-2" />
                                        Start Assessment
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Questions */}
                    <div className="lg:col-span-3">
                        <Card>
                            <CardHeader>
                                <CardTitle>Assessment Questions</CardTitle>
                                <CardDescription>
                                    Review the questions in this assessment before starting
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-6">
                                    {assessment.questions.map((question, index) => (
                                        <div key={question.question_id} className="border rounded-lg p-6 bg-white">
                                            <div className="flex items-start justify-between mb-4">
                                                <div className="flex items-center space-x-3">
                                                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold">
                                                        {index + 1}
                                                    </div>
                                                    <h3 className="text-lg font-medium text-gray-900">Question {index + 1}</h3>
                                                </div>
                                                <div className="flex space-x-2">
                                                    <Badge variant="outline" className="text-xs">{question.topic}</Badge>
                                                    <Badge className={`text-xs ${getDifficultyColor(question.difficulty)}`}>
                                                        {question.difficulty}
                                                    </Badge>
                                                </div>
                                            </div>
                                            
                                            <div className="mb-4">
                                                <p className="text-gray-800 leading-relaxed">{question.question_text}</p>
                                            </div>
                                            
                                            <div className="space-y-3">
                                                <p className="text-sm font-medium text-gray-700">Options:</p>
                                                {question.options.map((option, optionIndex) => (
                                                    <div key={optionIndex} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                                                        <div className="flex-shrink-0 w-6 h-6 bg-white border-2 border-gray-300 rounded-full flex items-center justify-center text-sm font-medium">
                                                            {String.fromCharCode(65 + optionIndex)}
                                                        </div>
                                                        <span className="text-gray-800 flex-1">{option}</span>
                                                        {optionIndex === question.correct_answer && (
                                                            <CheckCircle className="h-5 w-5 text-green-600" />
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                            
                                            {question.explanation && (
                                                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                                                    <div className="flex items-start space-x-2">
                                                        <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                                                        <div>
                                                            <p className="text-sm font-medium text-blue-800 mb-1">Explanation</p>
                                                            <p className="text-sm text-blue-700">{question.explanation}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                                
                                {assessment.questions.length === 0 && (
                                    <div className="text-center py-12">
                                        <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Questions Available</h3>
                                        <p className="text-gray-600">This assessment doesn't have any questions yet.</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}