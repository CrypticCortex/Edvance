"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Plus,
  Search,
  Brain,
  Target,
  Clock,
  BookOpen,
  Users,
  TrendingUp,
  ChevronRight,
  Play,
  CheckCircle
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"

interface LearningPath {
  path_id: string
  title: string
  description: string
  subject: string
  target_grade: number
  total_steps: number
  completion_percentage: number
  current_step: number
  estimated_duration_hours: number
  learning_goals: string[]
  addresses_gaps: number
  student_id: string
  student_name: string
  created_at: string
  status: 'active' | 'completed' | 'paused'
}

export default function LearningPathsPage() {
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [filterSubject, setFilterSubject] = useState("")
  const [filterStatus, setFilterStatus] = useState("")
  const { toast } = useToast()

  useEffect(() => {
    const loadData = async () => {
      try {
        // Mock data for learning paths
        const mockPaths: LearningPath[] = [
          {
            path_id: "path_xyz789",
            title: "Personalized Mathematics Learning Path",
            description: "Customized journey to master multiplication and strengthen math foundations",
            subject: "Mathematics",
            target_grade: 5,
            total_steps: 8,
            completion_percentage: 37.5,
            current_step: 3,
            estimated_duration_hours: 4.5,
            learning_goals: [
              "Master basic multiplication facts",
              "Understand multiplication strategies",
              "Build confidence in problem solving"
            ],
            addresses_gaps: 2,
            student_id: "student_123",
            student_name: "Alex Johnson",
            created_at: "2025-07-21T12:00:00Z",
            status: "active"
          },
          {
            path_id: "path_abc456",
            title: "Reading Comprehension Enhancement",
            description: "Targeted intervention for improving reading skills and vocabulary",
            subject: "English",
            target_grade: 4,
            total_steps: 6,
            completion_percentage: 83.3,
            current_step: 5,
            estimated_duration_hours: 3.0,
            learning_goals: [
              "Improve reading fluency",
              "Expand vocabulary",
              "Enhance comprehension strategies"
            ],
            addresses_gaps: 1,
            student_id: "student_456",
            student_name: "Sarah Chen",
            created_at: "2025-07-20T09:30:00Z",
            status: "active"
          },
          {
            path_id: "path_def789",
            title: "Science Exploration Journey",
            description: "Comprehensive science learning covering matter, energy, and life processes",
            subject: "Science",
            target_grade: 5,
            total_steps: 12,
            completion_percentage: 100,
            current_step: 12,
            estimated_duration_hours: 6.0,
            learning_goals: [
              "Understand states of matter",
              "Learn about energy transfer",
              "Explore life cycles"
            ],
            addresses_gaps: 3,
            student_id: "student_789",
            student_name: "Marcus Williams",
            created_at: "2025-07-18T14:15:00Z",
            status: "completed"
          }
        ]

        setTimeout(() => {
          setLearningPaths(mockPaths)
          setLoading(false)
        }, 1000)

      } catch (error: any) {
        console.error('Failed to load learning paths:', error)
        toast({
          title: "Loading Failed",
          description: handleApiError(error),
          variant: "destructive",
        })
        setLoading(false)
      }
    }

    loadData()
  }, [toast])

  const filteredPaths = learningPaths.filter(path => {
    const matchesSearch = path.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      path.student_name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSubject = !filterSubject || path.subject === filterSubject
    const matchesStatus = !filterStatus || path.status === filterStatus

    return matchesSearch && matchesSubject && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-800"
      case "completed": return "bg-blue-100 text-blue-800"
      case "paused": return "bg-yellow-100 text-yellow-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

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
          <Brain className="h-8 w-8 text-purple-600" />
          <div>
            <h1 className="text-3xl font-bold">Learning Paths</h1>
            <p className="text-gray-600">AI-generated personalized learning journeys</p>
          </div>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Generate Path
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Paths</p>
                <p className="text-3xl font-bold">
                  {learningPaths.filter(p => p.status === 'active').length}
                </p>
              </div>
              <Target className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed Paths</p>
                <p className="text-3xl font-bold">
                  {learningPaths.filter(p => p.status === 'completed').length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Progress</p>
                <p className="text-3xl font-bold">
                  {(learningPaths.reduce((sum, p) => sum + p.completion_percentage, 0) /
                    learningPaths.length).toFixed(0)}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Steps</p>
                <p className="text-3xl font-bold">
                  {learningPaths.reduce((sum, p) => sum + p.total_steps, 0)}
                </p>
              </div>
              <BookOpen className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search learning paths or students..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={filterSubject} onValueChange={setFilterSubject}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Subjects" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Subjects</SelectItem>
            <SelectItem value="Mathematics">Mathematics</SelectItem>
            <SelectItem value="Science">Science</SelectItem>
            <SelectItem value="English">English</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="paused">Paused</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Learning Paths */}
      <div className="space-y-4">
        {filteredPaths.map((path) => (
          <Card key={path.path_id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{path.title}</CardTitle>
                  <CardDescription className="flex items-center space-x-2">
                    <Badge variant="outline">{path.subject}</Badge>
                    <Badge variant="outline">Grade {path.target_grade}</Badge>
                    <Badge className={getStatusColor(path.status)}>
                      {path.status.charAt(0).toUpperCase() + path.status.slice(1)}
                    </Badge>
                  </CardDescription>
                </div>
                <Button variant="ghost" size="sm">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">{path.description}</p>

              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Student: {path.student_name}</span>
                <span className="text-gray-500">{formatDate(path.created_at)}</span>
              </div>

              {/* Progress */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{path.completion_percentage.toFixed(0)}% complete</span>
                </div>
                <Progress value={path.completion_percentage} className="h-2" />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Step {path.current_step} of {path.total_steps}</span>
                  <span>{path.estimated_duration_hours}h total</span>
                </div>
              </div>

              {/* Learning Goals */}
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">Learning Goals:</p>
                <div className="space-y-1">
                  {path.learning_goals.slice(0, 2).map((goal, index) => (
                    <div key={index} className="flex items-center space-x-2 text-sm">
                      <Target className="h-3 w-3 text-blue-500" />
                      <span>{goal}</span>
                    </div>
                  ))}
                  {path.learning_goals.length > 2 && (
                    <div className="text-xs text-gray-500">
                      +{path.learning_goals.length - 2} more goals
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center pt-2">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Brain className="h-4 w-4" />
                  <span>Addresses {path.addresses_gaps} gaps</span>
                </div>
                <div className="flex space-x-2">
                  {path.status === 'active' && (
                    <Button size="sm">
                      <Play className="h-3 w-3 mr-1" />
                      Continue
                    </Button>
                  )}
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredPaths.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No learning paths found</h3>
            <p className="text-gray-600 mb-6">
              {searchTerm || filterSubject || filterStatus
                ? "Try adjusting your filters to see more results"
                : "Create personalized learning paths for your students"}
            </p>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Generate Learning Path
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
