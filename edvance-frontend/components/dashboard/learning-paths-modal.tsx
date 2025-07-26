"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { 
  Target, 
  BookOpen, 
  CheckCircle, 
  Clock, 
  PlayCircle,
  PauseCircle,
  BarChart3,
  Calendar,
  TrendingUp,
  Award,
  MapPin
} from "lucide-react"

interface LearningStep {
  step_id: string
  title: string
  description: string
  content_type: string
  difficulty_level: string
  estimated_duration_minutes: number
  status: "not_started" | "in_progress" | "completed"
  progress_percentage: number
  learning_objectives: string[]
}

interface LearningPath {
  path_id: string
  title: string
  subject: string
  target_grade: number
  status: "active" | "completed" | "paused"
  progress_percentage: number
  created_at: string
  updated_at: string
  estimated_completion_date: string
  learning_goals: string[]
  steps: LearningStep[]
  total_steps: number
  completed_steps: number
}

interface Student {
  student_id: string
  first_name: string
  last_name: string
  email?: string
  grade: number
  subjects: string[]
}

interface LearningPathsModalProps {
  student: Student | null
  paths: LearningPath[]
  open: boolean
  onOpenChange: (open: boolean) => void
  loading?: boolean
}

export default function LearningPathsModal({ 
  student, 
  paths, 
  open, 
  onOpenChange, 
  loading = false 
}: LearningPathsModalProps) {
  if (!student) return null

  const getStudentName = (student: Student) => {
    return `${student.first_name} ${student.last_name}`
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "active":
        return <PlayCircle className="h-4 w-4 text-blue-600" />
      case "paused":
        return <PauseCircle className="h-4 w-4 text-orange-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-50 text-green-700 border-green-200"
      case "active":
        return "bg-blue-50 text-blue-700 border-blue-200"
      case "paused":
        return "bg-orange-50 text-orange-700 border-orange-200"
      default:
        return "bg-gray-50 text-gray-700 border-gray-200"
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "in_progress":
        return <PlayCircle className="h-4 w-4 text-blue-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Target className="h-6 w-6" />
            <span>Learning Paths for {getStudentName(student)}</span>
          </DialogTitle>
          <DialogDescription>
            Track progress and manage personalized learning journeys
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-blue-600" />
              <span className="ml-2 text-gray-600">Loading learning paths...</span>
            </div>
          ) : paths.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-8">
                <Target className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Learning Paths Found</h3>
                <p className="text-gray-600 text-center">
                  This student doesn't have any learning paths yet. Create a personalized learning path to get started.
                </p>
                <Button className="mt-4">
                  <Target className="h-4 w-4 mr-2" />
                  Create Learning Path
                </Button>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Summary Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <Target className="h-5 w-5 text-blue-600" />
                      <div>
                        <div className="text-2xl font-bold">{paths.length}</div>
                        <div className="text-sm text-gray-600">Total Paths</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <PlayCircle className="h-5 w-5 text-green-600" />
                      <div>
                        <div className="text-2xl font-bold">{paths.filter(p => p.status === 'active').length}</div>
                        <div className="text-sm text-gray-600">Active</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5 text-blue-600" />
                      <div>
                        <div className="text-2xl font-bold">{paths.filter(p => p.status === 'completed').length}</div>
                        <div className="text-sm text-gray-600">Completed</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-5 w-5 text-purple-600" />
                      <div>
                        <div className="text-2xl font-bold">
                          {Math.round(paths.reduce((acc, p) => acc + p.progress_percentage, 0) / paths.length) || 0}%
                        </div>
                        <div className="text-sm text-gray-600">Avg Progress</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Learning Paths List */}
              <div className="space-y-4">
                {paths.map((path) => (
                  <Card key={path.path_id} className="border-l-4 border-l-blue-500">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <CardTitle className="flex items-center space-x-2">
                            <BookOpen className="h-5 w-5" />
                            <span>{path.title}</span>
                          </CardTitle>
                          <CardDescription className="flex items-center space-x-4 mt-1">
                            <Badge variant="outline">{path.subject}</Badge>
                            <Badge variant="outline">Grade {path.target_grade}</Badge>
                            <span className="text-sm text-gray-600">
                              {path.completed_steps}/{path.total_steps} steps completed
                            </span>
                          </CardDescription>
                        </div>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(path.status)}
                          <Badge className={getStatusColor(path.status)} variant="outline">
                            {path.status.charAt(0).toUpperCase() + path.status.slice(1)}
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Progress */}
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">Progress</span>
                          <span className="text-sm font-semibold">{path.progress_percentage}%</span>
                        </div>
                        <Progress value={path.progress_percentage} className="h-2" />
                      </div>

                      {/* Dates */}
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center space-x-2">
                          <Calendar className="h-4 w-4 text-gray-500" />
                          <span className="text-gray-600">Started: {formatDate(path.created_at)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4 text-gray-500" />
                          <span className="text-gray-600">Est. Completion: {formatDate(path.estimated_completion_date)}</span>
                        </div>
                      </div>

                      {/* Learning Goals */}
                      {path.learning_goals && path.learning_goals.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Learning Goals</h4>
                          <div className="flex flex-wrap gap-1">
                            {path.learning_goals.map((goal, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {goal}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Steps Preview */}
                      {path.steps && path.steps.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Steps</h4>
                          <div className="space-y-2">
                            {path.steps.slice(0, 3).map((step, index) => (
                              <div key={step.step_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded-md">
                                <div className="flex items-center space-x-2">
                                  {getStepStatusIcon(step.status)}
                                  <span className="text-sm font-medium">{step.title}</span>
                                </div>
                                <div className="flex-1" />
                                <div className="text-xs text-gray-500">
                                  {step.estimated_duration_minutes} min
                                </div>
                                <Progress value={step.progress_percentage} className="w-16 h-1" />
                              </div>
                            ))}
                            {path.steps.length > 3 && (
                              <div className="text-xs text-gray-500 text-center py-2">
                                +{path.steps.length - 3} more steps
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex justify-end space-x-2 pt-2">
                        <Button variant="outline" size="sm">
                          <BarChart3 className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                        <Button size="sm">
                          <MapPin className="h-4 w-4 mr-1" />
                          Continue Learning
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
