"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Plus, BookOpen, Users, Clock, TrendingUp, BarChart3, Eye } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
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
  completion_stats?: {
    total_completions: number
    average_score: number
    completion_rate: number
  }
}

export default function AssessmentsPage() {
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    const loadAssessments = async () => {
      try {
        // Get teacher ID from local storage
        const teacherData = getUserFromStorage()
        const teacherId = teacherData?.uid
        
        console.log('Teacher data:', teacherData)
        console.log('Fetching assessments for teacher ID:', teacherId)
        
        // Load assessment configurations from the API with teacher filtering
        const response = await apiService.getAssessmentConfigs(teacherId) as any
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
            completion_stats: {
              total_completions: Math.floor(Math.random() * 50), // Mock data for now
              average_score: Math.round((Math.random() * 30 + 60) * 10) / 10, // 60-90%
              completion_rate: Math.round((Math.random() * 30 + 70) * 10) / 10 // 70-100%
            }
          }))
          
          console.log('Transformed assessments:', transformedAssessments)
          setAssessments(transformedAssessments)
          
          if (transformedAssessments.length === 0) {
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
      }
    }

    loadAssessments()
  }, [toast])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Assessments</h1>
            <p className="text-muted-foreground">Manage and create assessments for your students</p>
          </div>
          <Button disabled>
            <Plus className="w-4 h-4 mr-2" />
            Create Assessment
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-muted rounded w-3/4"></div>
                <div className="h-3 bg-muted rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-muted rounded"></div>
                  <div className="h-3 bg-muted rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Assessments</h1>
          <p className="text-muted-foreground">
            Manage and create AI-powered assessments for your students
          </p>
        </div>
        <Link href="/dashboard/assessments/create">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Create Assessment
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Total Assessments</p>
                <p className="text-2xl font-bold">{assessments.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Total Completions</p>
                <p className="text-2xl font-bold">
                  {assessments.reduce((sum, a) => sum + (a.completion_stats?.total_completions || 0), 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-yellow-500" />
              <div>
                <p className="text-sm text-muted-foreground">Avg Score</p>
                <p className="text-2xl font-bold">
                  {assessments.length > 0 
                    ? Math.round(
                        (assessments.reduce((sum, a) => sum + (a.completion_stats?.average_score || 0), 0) / assessments.length) * 10
                      ) / 10
                    : 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-500" />
              <div>
                <p className="text-sm text-muted-foreground">Completion Rate</p>
                <p className="text-2xl font-bold">
                  {assessments.length > 0 
                    ? Math.round(
                        (assessments.reduce((sum, a) => sum + (a.completion_stats?.completion_rate || 0), 0) / assessments.length) * 10
                      ) / 10
                    : 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Assessments List */}
      {assessments.length === 0 ? (
        <Card className="text-center p-12">
          <CardContent>
            <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No assessments yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first AI-powered assessment to get started
            </p>
            <Link href="/dashboard/assessments/create">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Assessment
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assessments.map((assessment) => (
            <Card key={assessment.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{assessment.title}</CardTitle>
                    <CardDescription>
                      {assessment.subject} • Grade {assessment.grade}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {assessment.questions_count} questions
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Topics */}
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Topics</p>
                  <div className="flex flex-wrap gap-1">
                    {assessment.topics.map((topic, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Duration */}
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  {assessment.estimated_duration_minutes} minutes
                </div>

                {/* Stats */}
                {assessment.completion_stats && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Completions:</span>
                      <span className="font-medium">{assessment.completion_stats.total_completions}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Avg Score:</span>
                      <span className="font-medium">{assessment.completion_stats.average_score}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Completion Rate:</span>
                      <span className="font-medium">{assessment.completion_stats.completion_rate}%</span>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="w-4 h-4 mr-2" />
                    View Details
                  </Button>
                  <Button variant="outline" size="sm">
                    Share
                  </Button>
                </div>

                {/* Created Date */}
                <p className="text-xs text-muted-foreground">
                  Created {new Date(assessment.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
