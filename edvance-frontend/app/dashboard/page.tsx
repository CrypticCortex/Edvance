"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Users, BookOpen, TrendingUp, CheckCircle, AlertCircle, Brain, Target } from "lucide-react"
import { OverviewChart } from "@/components/dashboard/overview-chart"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { apiService, handleApiError } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"

interface DashboardData {
  classroom_overview: {
    total_students: number
    active_learning_paths: number
    completed_assessments_this_week: number
    average_class_progress: number
  }
  automated_interventions: {
    paths_generated_this_week: number
    students_needing_support: number
    students_ready_for_enrichment: number
    lesson_completion_rate: number
  }
  ai_agent_activity: {
    monitoring_active: boolean
    assessments_analyzed: number
    learning_paths_generated: number
    lessons_created: number
    chatbot_interactions: number
  }
}

export default function DashboardPage() {
  const [teacherData, setTeacherData] = useState<any>(null)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const { toast } = useToast()
  const router = useRouter()

  // Helper function to safely get dashboard values
  const getSafeValue = (path: string, fallback: number = 0) => {
    const parts = path.split('.')
    let current: any = dashboardData
    for (const part of parts) {
      current = current?.[part]
      if (current === undefined || current === null) return fallback
    }
    return current
  }

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // Load teacher data from localStorage
        const storedData = localStorage.getItem("teacher_data")
        if (!storedData) {
          router.push("/auth/login")
          return
        }

        const userData = JSON.parse(storedData)
        setTeacherData(userData)

        // Get auth tokens and set them for API calls
        const authTokens = apiService.getAuthTokens()
        if (!authTokens) {
          router.push("/auth/login")
          return
        }

        // Fetch real dashboard data from API
        const analytics = await apiService.getTeacherAnalytics()
        setDashboardData(analytics as DashboardData)

      } catch (error: any) {
        console.error('Dashboard data loading error:', error)
        setError(handleApiError(error))

        // Fallback to mock data if API fails
        const mockData: DashboardData = {
          classroom_overview: {
            total_students: 28,
            active_learning_paths: 45,
            completed_assessments_this_week: 156,
            average_class_progress: 73.2,
          },
          automated_interventions: {
            paths_generated_this_week: 12,
            students_needing_support: 5,
            students_ready_for_enrichment: 3,
            lesson_completion_rate: 87.5,
          },
          ai_agent_activity: {
            monitoring_active: true,
            assessments_analyzed: 47,
            learning_paths_generated: 12,
            lessons_created: 96,
            chatbot_interactions: 1247,
          },
        }
        setDashboardData(mockData)

        toast({
          title: "Using Demo Data",
          description: "API connection failed, showing demo analytics",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [router, toast])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-green-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-2" />
            <span className="text-yellow-800">{error}</span>
          </div>
        </div>
      )}
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">
          Welcome back, {teacherData?.first_name} {teacherData?.last_name}!
        </h1>
        <p className="text-green-100 mb-4">
          Your AI Learning Path Agent is actively monitoring and supporting your students.
        </p>
        <div className="flex items-center space-x-2">
          <CheckCircle className="h-5 w-5" />
          <span>AI Agent Status: Active</span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link href="/dashboard/assessments/create">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-dashed border-2 border-blue-300 bg-blue-50">
            <CardContent className="p-6 text-center">
              <BookOpen className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-semibold text-blue-800">Create Assessment</h3>
              <p className="text-sm text-blue-600">Build new student evaluation</p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard/learning-paths">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-dashed border-2 border-purple-300 bg-purple-50">
            <CardContent className="p-6 text-center">
              <Target className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h3 className="font-semibold text-purple-800">Generate Path</h3>
              <p className="text-sm text-purple-600">AI personalized learning</p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard/students">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-dashed border-2 border-green-300 bg-green-50">
            <CardContent className="p-6 text-center">
              <Users className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold text-green-800">View Students</h3>
              <p className="text-sm text-green-600">Monitor progress</p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard/analytics">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-dashed border-2 border-yellow-300 bg-yellow-50">
            <CardContent className="p-6 text-center">
              <TrendingUp className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
              <h3 className="font-semibold text-yellow-800">View Analytics</h3>
              <p className="text-sm text-yellow-600">Class insights</p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="card-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{getSafeValue('classroom_overview.total_students')}</div>
            <p className="text-xs text-muted-foreground">Active learners in your classroom</p>
          </CardContent>
        </Card>

        <Card className="card-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Learning Paths</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.classroom_overview?.active_learning_paths || 0}</div>
            <p className="text-xs text-muted-foreground">Personalized learning journeys</p>
          </CardContent>
        </Card>

        <Card className="card-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Lessons Created</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.ai_agent_activity?.lessons_created || 0}</div>
            <p className="text-xs text-muted-foreground">AI-generated this month</p>
          </CardContent>
        </Card>

        <Card className="card-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Class Progress</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.classroom_overview?.average_class_progress || 0}%</div>
            <Progress value={dashboardData?.classroom_overview?.average_class_progress || 0} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* AI Agent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-purple-600" />
              <span>AI Agent Activity</span>
            </CardTitle>
            <CardDescription>Automated learning support this week</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm">Assessments Analyzed</span>
              <Badge variant="secondary">{dashboardData?.ai_agent_activity?.assessments_analyzed || 0}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Learning Paths Generated</span>
              <Badge variant="secondary">{dashboardData?.ai_agent_activity?.learning_paths_generated || 0}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Chatbot Interactions</span>
              <Badge variant="secondary">{dashboardData?.ai_agent_activity?.chatbot_interactions || 0}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Lesson Completion Rate</span>
              <Badge variant="outline">{dashboardData?.automated_interventions?.lesson_completion_rate || 0}%</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-orange-600" />
              <span>Student Interventions</span>
            </CardTitle>
            <CardDescription>Students requiring attention</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm">Need Support</span>
              <Badge variant="destructive">{dashboardData?.automated_interventions?.students_needing_support || 0}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Ready for Enrichment</span>
              <Badge variant="default">{dashboardData?.automated_interventions?.students_ready_for_enrichment || 0}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">New Paths This Week</span>
              <Badge variant="secondary">{dashboardData?.automated_interventions?.paths_generated_this_week || 0}</Badge>
            </div>
            <Button className="w-full mt-4 bg-transparent" variant="outline">
              View Detailed Analytics
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <OverviewChart />
        </div>
        <div>
          <RecentActivity />
        </div>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and shortcuts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="h-20 flex flex-col space-y-2">
              <BookOpen className="h-6 w-6" />
              <span>Create Assessment</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2 bg-transparent">
              <Users className="h-6 w-6" />
              <span>View Students</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2 bg-transparent">
              <TrendingUp className="h-6 w-6" />
              <span>Analytics Report</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
