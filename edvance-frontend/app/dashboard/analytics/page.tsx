"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import {
    TrendingUp,
    Users,
    BookOpen,
    Target,
    Award,
    Brain,
    BarChart3,
    PieChart,
    Activity,
    CheckCircle,
    AlertCircle,
    Clock,
    RefreshCw,
    ArrowUpRight,
    ArrowDownRight,
    Minus
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"

interface AnalyticsData {
    // Overview metrics
    total_students: number
    active_learning_paths: number
    completed_assessments_this_week: number
    average_class_progress: number

    // Student performance
    students_needing_support: number
    students_ready_for_enrichment: number
    average_assessment_score: number

    // Learning paths analytics
    learning_paths_generated: number
    most_common_learning_goals: string[]
    path_completion_rate: number

    // Assessment analytics
    total_assessments: number
    assessment_subjects: Record<string, number>
    difficulty_distribution: Record<string, number>
    average_completion_time: number

    // AI agent activity
    ai_interventions_this_week: number
    automated_paths_created: number
    chatbot_interactions: number

    // Trends and insights
    weekly_progress_trend: Array<{ week: string, progress: number }>
    subject_performance: Array<{ subject: string, average_score: number, student_count: number }>
    recent_activities: Array<{
        type: string
        description: string
        timestamp: string
        student_name?: string
    }>
}

export default function AnalyticsPage() {
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
    const [loading, setLoading] = useState(true)
    const [refreshing, setRefreshing] = useState(false)
    const { toast } = useToast()

    const loadAnalytics = async (isRefresh = false) => {
        if (isRefresh) {
            setRefreshing(true)
        } else {
            setLoading(true)
        }

        try {
            const response = await apiService.getTeacherAnalytics()
            console.log('Analytics API response:', response)

            if (response) {
                setAnalytics(response as AnalyticsData)

                if (isRefresh) {
                    toast({
                        title: "Analytics Refreshed",
                        description: "Latest data has been loaded",
                    })
                }
            }
        } catch (error: any) {
            console.error('Error loading analytics:', error)

            // Mock data for demonstration if API fails
            if (!isRefresh) {
                const mockAnalytics: AnalyticsData = {
                    total_students: 24,
                    active_learning_paths: 18,
                    completed_assessments_this_week: 12,
                    average_class_progress: 78.5,
                    students_needing_support: 3,
                    students_ready_for_enrichment: 7,
                    average_assessment_score: 82.3,
                    learning_paths_generated: 45,
                    most_common_learning_goals: ["Problem Solving", "Reading Comprehension", "Mathematical Reasoning"],
                    path_completion_rate: 85.2,
                    total_assessments: 156,
                    assessment_subjects: {
                        "Mathematics": 68,
                        "Science": 45,
                        "English": 32,
                        "History": 11
                    },
                    difficulty_distribution: {
                        "easy": 45,
                        "medium": 78,
                        "hard": 33
                    },
                    average_completion_time: 23.7,
                    ai_interventions_this_week: 8,
                    automated_paths_created: 12,
                    chatbot_interactions: 234,
                    weekly_progress_trend: [
                        { week: "Week 1", progress: 65 },
                        { week: "Week 2", progress: 72 },
                        { week: "Week 3", progress: 75 },
                        { week: "Week 4", progress: 78.5 }
                    ],
                    subject_performance: [
                        { subject: "Mathematics", average_score: 85.2, student_count: 24 },
                        { subject: "Science", average_score: 81.7, student_count: 20 },
                        { subject: "English", average_score: 79.3, student_count: 18 }
                    ],
                    recent_activities: [
                        {
                            type: "assessment_completed",
                            description: "Completed Mathematics Assessment",
                            timestamp: "2025-01-27T10:30:00Z",
                            student_name: "Sarah Johnson"
                        },
                        {
                            type: "learning_path_generated",
                            description: "AI generated new learning path for struggling concepts",
                            timestamp: "2025-01-27T09:15:00Z",
                            student_name: "Mike Chen"
                        },
                        {
                            type: "intervention_triggered",
                            description: "Automated support intervention activated",
                            timestamp: "2025-01-27T08:45:00Z",
                            student_name: "Emma Davis"
                        }
                    ]
                }
                setAnalytics(mockAnalytics)
            }

            toast({
                title: "Error Loading Analytics",
                description: handleApiError(error),
                variant: "destructive"
            })
        } finally {
            setLoading(false)
            setRefreshing(false)
        }
    }

    useEffect(() => {
        loadAnalytics()
    }, [])

    const getTrendIcon = (current: number, previous: number) => {
        if (current > previous) return <ArrowUpRight className="h-4 w-4 text-green-600" />
        if (current < previous) return <ArrowDownRight className="h-4 w-4 text-red-600" />
        return <Minus className="h-4 w-4 text-gray-600" />
    }

    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const getActivityIcon = (type: string) => {
        switch (type) {
            case 'assessment_completed':
                return <CheckCircle className="h-4 w-4 text-green-600" />
            case 'learning_path_generated':
                return <Target className="h-4 w-4 text-blue-600" />
            case 'intervention_triggered':
                return <AlertCircle className="h-4 w-4 text-orange-600" />
            default:
                return <Activity className="h-4 w-4 text-gray-600" />
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    if (!analytics) {
        return (
            <div className="text-center py-12">
                <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Analytics Data</h3>
                <p className="text-gray-600">Unable to load analytics data at this time.</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-3">
                    <BarChart3 className="h-8 w-8 text-blue-600" />
                    <div>
                        <h1 className="text-3xl font-bold">Learning Analytics</h1>
                        <p className="text-gray-600">Comprehensive insights into your classroom</p>
                    </div>
                </div>
                <Button
                    variant="outline"
                    onClick={() => loadAnalytics(true)}
                    disabled={refreshing}
                >
                    <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                    {refreshing ? 'Refreshing...' : 'Refresh'}
                </Button>
            </div>

            {/* Key Metrics Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Total Students</p>
                                <p className="text-3xl font-bold">{analytics.total_students}</p>
                                <p className="text-sm text-gray-500">Active learners</p>
                            </div>
                            <Users className="h-8 w-8 text-blue-600" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Active Paths</p>
                                <p className="text-3xl font-bold">{analytics.active_learning_paths}</p>
                                <p className="text-sm text-gray-500">Learning journeys</p>
                            </div>
                            <Target className="h-8 w-8 text-green-600" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Assessments This Week</p>
                                <p className="text-3xl font-bold">{analytics.completed_assessments_this_week}</p>
                                <p className="text-sm text-gray-500">Completed</p>
                            </div>
                            <Award className="h-8 w-8 text-purple-600" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Class Progress</p>
                                <p className="text-3xl font-bold">{analytics.average_class_progress}%</p>
                                <p className="text-sm text-gray-500">Average</p>
                            </div>
                            <TrendingUp className="h-8 w-8 text-orange-600" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Student Performance Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <Users className="h-5 w-5" />
                            <span>Student Performance</span>
                        </CardTitle>
                        <CardDescription>Support and enrichment opportunities</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="text-center p-4 bg-red-50 rounded-lg">
                                <div className="text-2xl font-bold text-red-600">{analytics.students_needing_support}</div>
                                <div className="text-sm text-red-600">Need Support</div>
                            </div>
                            <div className="text-center p-4 bg-green-50 rounded-lg">
                                <div className="text-2xl font-bold text-green-600">{analytics.students_ready_for_enrichment}</div>
                                <div className="text-sm text-green-600">Ready for Enrichment</div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium">Average Assessment Score</span>
                                <span className="text-sm font-semibold">{analytics.average_assessment_score}%</span>
                            </div>
                            <Progress value={analytics.average_assessment_score} className="h-3" />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <Target className="h-5 w-5" />
                            <span>Learning Paths</span>
                        </CardTitle>
                        <CardDescription>AI-generated personalized learning</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-2xl font-bold">{analytics.learning_paths_generated}</div>
                                <div className="text-sm text-gray-600">Total Generated</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold">{analytics.path_completion_rate}%</div>
                                <div className="text-sm text-gray-600">Completion Rate</div>
                            </div>
                        </div>
                        <div>
                            <p className="text-sm font-medium mb-2">Common Learning Goals</p>
                            <div className="flex flex-wrap gap-1">
                                {analytics.most_common_learning_goals?.map((goal, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                        {goal}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Assessment Analytics */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <BookOpen className="h-5 w-5" />
                        <span>Assessment Analytics</span>
                    </CardTitle>
                    <CardDescription>Assessment usage and performance insights</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Assessment by Subject */}
                        <div>
                            <h4 className="font-medium mb-3">Assessments by Subject</h4>
                            <div className="space-y-2">
                                {Object.entries(analytics.assessment_subjects || {}).map(([subject, count]) => (
                                    <div key={subject} className="flex justify-between items-center">
                                        <span className="text-sm">{subject}</span>
                                        <Badge variant="outline">{count}</Badge>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Difficulty Distribution */}
                        <div>
                            <h4 className="font-medium mb-3">Difficulty Distribution</h4>
                            <div className="space-y-2">
                                {Object.entries(analytics.difficulty_distribution || {}).map(([difficulty, count]) => (
                                    <div key={difficulty} className="flex justify-between items-center">
                                        <span className="text-sm capitalize">{difficulty}</span>
                                        <Badge variant="outline">{count}</Badge>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Performance Stats */}
                        <div>
                            <h4 className="font-medium mb-3">Performance Stats</h4>
                            <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-sm">
                                        <span>Avg Completion Time</span>
                                        <span>{analytics.average_completion_time} min</span>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm">
                                        <span>Total Assessments</span>
                                        <span>{analytics.total_assessments}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* AI Agent Activity */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Brain className="h-5 w-5" />
                        <span>AI Agent Activity</span>
                    </CardTitle>
                    <CardDescription>Automated interventions and assistance</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <div className="text-2xl font-bold text-blue-600">{analytics.ai_interventions_this_week}</div>
                            <div className="text-sm text-blue-600">Interventions This Week</div>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-lg">
                            <div className="text-2xl font-bold text-purple-600">{analytics.automated_paths_created}</div>
                            <div className="text-sm text-purple-600">Auto-Generated Paths</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                            <div className="text-2xl font-bold text-green-600">{analytics.chatbot_interactions}</div>
                            <div className="text-sm text-green-600">Chatbot Interactions</div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Subject Performance */}
            {analytics.subject_performance && analytics.subject_performance.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <PieChart className="h-5 w-5" />
                            <span>Subject Performance</span>
                        </CardTitle>
                        <CardDescription>Average performance across subjects</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {analytics.subject_performance.map((subject) => (
                                <div key={subject.subject}>
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium">{subject.subject}</span>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm text-gray-600">{subject.student_count} students</span>
                                            <span className="font-semibold">{subject.average_score}%</span>
                                        </div>
                                    </div>
                                    <Progress value={subject.average_score} className="h-2" />
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Recent Activities */}
            {analytics.recent_activities && analytics.recent_activities.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <Activity className="h-5 w-5" />
                            <span>Recent Activities</span>
                        </CardTitle>
                        <CardDescription>Latest student and system activities</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {analytics.recent_activities.map((activity, index) => (
                                <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                                    {getActivityIcon(activity.type)}
                                    <div className="flex-1">
                                        <p className="text-sm font-medium">{activity.description}</p>
                                        {activity.student_name && (
                                            <p className="text-xs text-gray-600">Student: {activity.student_name}</p>
                                        )}
                                    </div>
                                    <div className="text-xs text-gray-500">
                                        {formatTimestamp(activity.timestamp)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}
