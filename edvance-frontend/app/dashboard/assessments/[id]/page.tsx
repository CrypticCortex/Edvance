"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, BookOpen, Clock, Users, CheckCircle, XCircle, BarChart3, Share, Download } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"

interface Assessment {
  assessment_id: string
  title: string
  subject: string
  grade: number
  topic: string
  difficulty_level: string
  questions: Array<{
    question_text: string
    options: string[]
    correct_answer: number
    topic: string
    difficulty: string
  }>
  metadata: {
    total_questions: number
    estimated_duration_minutes: number
    subject: string
    grade: number
  }
  created_at: string
  teacher_uid: string
}

export default function AssessmentViewPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const assessmentId = params.id as string

  useEffect(() => {
    loadAssessment()
  }, [assessmentId])

  const generateQuestions = async () => {
    if (!assessment) return

    try {
      setGenerating(true)
      const response = await apiService.generateAssessmentFromConfig(assessment.assessment_id)
      console.log('Generated assessment:', response)
      
      // Update the assessment with the generated questions
      const updatedAssessment: Assessment = {
        ...assessment,
        questions: response.questions || [],
        metadata: {
          ...assessment.metadata,
          total_questions: response.questions?.length || 0
        }
      }
      
      setAssessment(updatedAssessment)
      toast({
        title: "Questions Generated",
        description: `Successfully generated ${response.questions?.length || 0} questions!`,
      })
    } catch (error: any) {
      console.error('Error generating questions:', error)
      toast({
        title: "Error Generating Questions",
        description: handleApiError(error),
        variant: "destructive"
      })
    } finally {
      setGenerating(false)
    }
  }

  const loadAssessment = async () => {
    try {
      setLoading(true)
      
      // First try to get the specific config
      try {
        const response = await apiService.getAssessmentConfig(assessmentId)
        console.log('Assessment config response:', response)
        
        // Transform config to assessment format for display
        const transformedAssessment: Assessment = {
          assessment_id: response.config_id,
          title: response.name,
          subject: response.subject,
          grade: response.target_grade,
          topic: response.topic,
          difficulty_level: response.difficulty_level,
          questions: [], // No questions yet - this is just a config
          metadata: {
            total_questions: response.question_count,
            estimated_duration_minutes: response.time_limit_minutes,
            subject: response.subject,
            grade: response.target_grade
          },
          created_at: response.created_at,
          teacher_uid: response.teacher_uid
        }
        
        setAssessment(transformedAssessment)
        return
      } catch (specificError: any) {
        console.warn('Failed to get specific config, trying fallback:', specificError.message)
        
        // Fallback: Get all configs and find the matching one
        const allConfigs = await apiService.getAssessmentConfigs()
        console.log('All configs response:', allConfigs)
        
        let configsData = allConfigs.data || allConfigs
        if (!Array.isArray(configsData)) {
          configsData = []
        }
        
        // Find the config with matching ID
        const matchingConfig = configsData.find((config: any) => 
          config.config_id === assessmentId || config.id === assessmentId
        )
        
        if (matchingConfig) {
          // Transform the config to assessment format for display
          const transformedAssessment: Assessment = {
            assessment_id: matchingConfig.config_id || matchingConfig.id,
            title: matchingConfig.name || matchingConfig.title || 'Untitled Assessment',
            subject: matchingConfig.subject || 'Unknown Subject',
            grade: matchingConfig.target_grade || matchingConfig.grade || 0,
            topic: matchingConfig.topic || 'General',
            difficulty_level: matchingConfig.difficulty_level || 'medium',
            questions: [], // No questions yet - this is just a config
            metadata: {
              total_questions: matchingConfig.question_count || 10,
              estimated_duration_minutes: matchingConfig.time_limit_minutes || 30,
              subject: matchingConfig.subject || 'Unknown Subject',
              grade: matchingConfig.target_grade || matchingConfig.grade || 0
            },
            created_at: matchingConfig.created_at || new Date().toISOString(),
            teacher_uid: matchingConfig.teacher_uid || matchingConfig.teacher_id || ''
          }
          
          console.log('Found matching config:', transformedAssessment)
          setAssessment(transformedAssessment)
          return
        }
        
        throw new Error('Assessment configuration not found')
      }
    } catch (error: any) {
      console.error('Error loading assessment config:', error)
      toast({
        title: "Error Loading Assessment",
        description: handleApiError(error),
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!assessment) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </div>
        <Card>
          <CardContent className="p-12 text-center">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Assessment Not Found</h3>
            <p className="text-gray-600">
              The assessment you're looking for doesn't exist or has been removed.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex items-center space-x-3">
            <BookOpen className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold">{assessment.title}</h1>
              <p className="text-gray-600">Assessment Details</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {assessment.questions.length === 0 && (
            <Button onClick={generateQuestions} disabled={generating}>
              <BookOpen className="h-4 w-4 mr-2" />
              {generating ? 'Generating...' : 'Generate Questions'}
            </Button>
          )}
          <Button variant="outline">
            <Share className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline">
            <BarChart3 className="h-4 w-4 mr-2" />
            Analytics
          </Button>
        </div>
      </div>

      {/* Assessment Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Assessment Details</CardTitle>
              <CardDescription>Assessment information and metadata</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Subject</label>
                  <p className="text-lg">{assessment.subject}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Grade Level</label>
                  <p className="text-lg">Grade {assessment.grade}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Topic</label>
                  <p className="text-lg">{assessment.topic}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Difficulty</label>
                  <Badge variant="outline" className="capitalize">
                    {assessment.difficulty_level}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Questions</label>
                  <p className="text-lg">{assessment.questions.length} questions</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Duration</label>
                  <p className="text-lg">{assessment.metadata.estimated_duration_minutes} minutes</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Assessment Questions */}
          <Card>
            <CardHeader>
              <CardTitle>Assessment Questions</CardTitle>
              <CardDescription>
                {assessment.questions.length} questions in this assessment
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {assessment.questions.map((question, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Question {index + 1}</h4>
                    <div className="flex gap-2">
                      <Badge variant="outline" className="text-xs">{question.topic}</Badge>
                      <Badge variant="outline" className="text-xs capitalize">{question.difficulty}</Badge>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700 mb-3">{question.question_text}</p>
                  <div className="space-y-2">
                    {question.options.map((option, optionIndex) => (
                      <div key={optionIndex} className="flex items-center space-x-2">
                        <span className="text-xs bg-gray-100 rounded px-2 py-1 min-w-[24px] text-center">
                          {String.fromCharCode(65 + optionIndex)}
                        </span>
                        <span className="text-sm flex-1">{option}</span>
                        {optionIndex === question.correct_answer && (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
              
              {assessment.questions.length === 0 && (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No questions available for this assessment</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-4 w-4 text-blue-600" />
                  <span className="text-sm">Questions</span>
                </div>
                <span className="font-medium">{assessment.questions.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Duration</span>
                </div>
                <span className="font-medium">{assessment.metadata.estimated_duration_minutes}m</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-purple-600" />
                  <span className="text-sm">Grade</span>
                </div>
                <span className="font-medium">{assessment.grade}</span>
              </div>
            </CardContent>
          </Card>

          {/* Question Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Question Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {assessment.questions.length > 0 ? (
                Object.entries(
                  assessment.questions.reduce((acc: any, question) => {
                    const difficulty = question.difficulty;
                    acc[difficulty] = (acc[difficulty] || 0) + 1;
                    return acc;
                  }, {} as Record<string, number>)
                ).map(([difficulty, count]) => (
                  <div key={difficulty} className="flex justify-between items-center">
                    <Badge variant="outline" className="capitalize">{difficulty}</Badge>
                    <span className="text-sm font-medium">{count}</span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No questions generated yet</p>
              )}
            </CardContent>
          </Card>

          {/* Metadata */}
          <Card>
            <CardHeader>
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div>
                <label className="text-xs font-medium text-gray-500">Created</label>
                <p className="text-sm">{formatDate(assessment.created_at)}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Assessment ID</label>
                <p className="text-xs font-mono bg-gray-100 rounded px-2 py-1">
                  {assessment.assessment_id}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}