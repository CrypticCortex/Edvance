"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LanguageSelector } from "@/components/ui/language-selector"
import { Plus, BookOpen, Users, Clock, BarChart3, Eye, RefreshCw } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useLanguage } from "@/contexts/LanguageContext"
import { apiService, handleApiError, getUserFromStorage } from "@/lib/api"

interface Assessment {
  id: string
  title: string
  subject: string
  grade: number
  topics: string[]
  questions_count: number
  estimated_duration_minutes: number
  created_at: string
  teacher_id?: string
  difficulty_level?: string
}

export default function AssessmentsPage() {
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const { toast } = useToast()
  const { currentLanguage } = useLanguage()

  const loadAssessments = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    try {
      // Get teacher ID from local storage
      const teacherData = getUserFromStorage()
      const teacherId = teacherData?.uid

      console.log('Teacher data:', teacherData)
      console.log('Fetching assessments for teacher ID:', teacherId)

      // Load assessment configurations from the API - backend will filter by authenticated user
      const response = await apiService.getAssessmentConfigs() as any
      console.log('API response:', response)

      if (response && (response.success !== false)) {
        // Handle different response formats
        let configsData = response.data || response

        // Ensure it's an array
        if (!Array.isArray(configsData)) {
          console.warn('Response is not an array:', configsData)
          configsData = []
        }

        // Transform the API data to match our interface
        const transformedAssessments: Assessment[] = configsData.map((config: any) => ({
          id: config.config_id || config.id || `config_${Date.now()}_${Math.random()}`,
          title: config.name || config.title || 'Untitled Assessment',
          subject: config.subject || 'Unknown Subject',
          grade: config.target_grade || config.grade || 0,
          topics: config.topic ? [config.topic] : (config.topics || ['General']),
          questions_count: config.question_count || 10,
          estimated_duration_minutes: config.time_limit_minutes || 30,
          created_at: config.created_at || new Date().toISOString(),
          teacher_id: config.teacher_id || teacherId,
          difficulty_level: config.difficulty_level || 'medium'
        }))

        console.log('Transformed assessments:', transformedAssessments)
        setAssessments(transformedAssessments)

        if (isRefresh && transformedAssessments.length > 0) {
          toast({
            title: "Assessments Refreshed",
            description: `Found ${transformedAssessments.length} assessment(s)`,
          })
        } else if (transformedAssessments.length === 0) {
          toast({
            title: "No Assessments Found",
            description: "You haven't created any assessments yet. Create your first assessment to get started!",
          })
        }
      } else {
        console.warn('No assessments data received')
        setAssessments([])
      }
    } catch (error: any) {
      console.error('Error loading assessments:', error)
      toast({
        title: "Error Loading Assessments",
        description: handleApiError(error),
        variant: "destructive"
      })
      setAssessments([])
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadAssessments()
  }, [toast])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <BookOpen className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold">Assessments</h1>
            <p className="text-gray-600">Manage and track student assessments</p>
          </div>
        </div>
        <div className="flex gap-2">
          <LanguageSelector variant="compact" />
          <Button
            variant="outline"
            onClick={() => loadAssessments(true)}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
          <Link href="/dashboard/assessments/create">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Assessment
            </Button>
          </Link>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Assessments</p>
                <p className="text-3xl font-bold">{assessments.length}</p>
              </div>
              <BookOpen className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Questions</p>
                <p className="text-3xl font-bold">
                  {assessments.reduce((sum, a) => sum + a.questions_count, 0)}
                </p>
              </div>
              <Users className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Duration</p>
                <p className="text-3xl font-bold">
                  {assessments.length > 0
                    ? Math.round(assessments.reduce((sum, a) => sum + a.estimated_duration_minutes, 0) / assessments.length)
                    : 0} min
                </p>
              </div>
              <Clock className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Assessments List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {assessments.map((assessment) => (
          <Card key={assessment.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{assessment.title}</CardTitle>
                  <CardDescription className="flex items-center space-x-2 mt-1">
                    <Badge variant="outline">{assessment.subject}</Badge>
                    <Badge variant="outline">Grade {assessment.grade}</Badge>
                  </CardDescription>
                </div>
                <Button variant="ghost" size="sm">
                  <BarChart3 className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Assessment Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-4 w-4 text-gray-500" />
                  <span>{assessment.questions_count} questions</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-gray-500" />
                  <span>{assessment.estimated_duration_minutes} min</span>
                </div>
              </div>

              {/* Topics */}
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">Topics:</p>
                <div className="flex flex-wrap gap-1">
                  {assessment.topics.map((topic) => (
                    <Badge key={topic} variant="secondary" className="text-xs">
                      {topic}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center pt-4 border-t">
                <span className="text-xs text-gray-500">
                  Created {formatDate(assessment.created_at)}
                </span>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {assessments.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No assessments yet</h3>
            <p className="text-gray-600 mb-6">
              Create your first assessment to start evaluating student understanding
            </p>
            <Link href="/dashboard/assessments/create">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Assessment
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
