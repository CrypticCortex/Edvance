"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Zap, Play, Eye, Edit, MessageSquare } from "lucide-react"

interface Lesson {
  id: string
  title: string
  topic: string
  subject: string
  target_grade: number
  estimated_duration_minutes: number
  slides_count: number
  generation_time_seconds: number
  created_at: string
  status: "draft" | "published" | "in_progress"
  student_name?: string
  learning_path_id?: string
  interactive_elements: number
  chatbot_enabled: boolean
}

export default function LessonsPage() {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Mock lessons data
    const mockLessons: Lesson[] = [
      {
        id: "lesson_001",
        title: "Understanding Multiplication as Repeated Addition",
        topic: "Basic Multiplication",
        subject: "Mathematics",
        target_grade: 5,
        estimated_duration_minutes: 20,
        slides_count: 4,
        generation_time_seconds: 27.17,
        created_at: "2025-01-21T12:00:00Z",
        status: "published",
        student_name: "Emma Davis",
        learning_path_id: "path_001",
        interactive_elements: 3,
        chatbot_enabled: true,
      },
      {
        id: "lesson_002",
        title: "Advanced Photosynthesis Concepts",
        topic: "Plant Biology",
        subject: "Science",
        target_grade: 5,
        estimated_duration_minutes: 25,
        slides_count: 6,
        generation_time_seconds: 24.83,
        created_at: "2025-01-20T14:30:00Z",
        status: "published",
        student_name: "Sarah Johnson",
        learning_path_id: "path_002",
        interactive_elements: 4,
        chatbot_enabled: true,
      },
      {
        id: "lesson_003",
        title: "Reading Comprehension Strategies",
        topic: "Reading Skills",
        subject: "English",
        target_grade: 5,
        estimated_duration_minutes: 30,
        slides_count: 5,
        generation_time_seconds: 29.45,
        created_at: "2025-01-19T10:15:00Z",
        status: "published",
        student_name: "Michael Chen",
        learning_path_id: "path_003",
        interactive_elements: 2,
        chatbot_enabled: true,
      },
      {
        id: "lesson_004",
        title: "Fraction Fundamentals",
        topic: "Fractions",
        subject: "Mathematics",
        target_grade: 5,
        estimated_duration_minutes: 35,
        slides_count: 7,
        generation_time_seconds: 31.22,
        created_at: "2025-01-22T09:00:00Z",
        status: "draft",
        interactive_elements: 5,
        chatbot_enabled: false,
      },
      {
        id: "lesson_005",
        title: "Weather Patterns and Climate",
        topic: "Weather Science",
        subject: "Science",
        target_grade: 5,
        estimated_duration_minutes: 28,
        slides_count: 6,
        generation_time_seconds: 26.91,
        created_at: "2025-01-18T16:45:00Z",
        status: "published",
        student_name: "James Wilson",
        interactive_elements: 3,
        chatbot_enabled: true,
      },
    ]

    setTimeout(() => {
      setLessons(mockLessons)
      setLoading(false)
    }, 1000)
  }, [])

  const filteredLessons = lessons.filter(
    (lesson) =>
      lesson.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lesson.topic.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lesson.subject.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case "published":
        return "bg-green-100 text-green-800"
      case "draft":
        return "bg-gray-100 text-gray-800"
      case "in_progress":
        return "bg-yellow-100 text-yellow-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const averageGenerationTime =
    lessons.reduce((acc, lesson) => acc + lesson.generation_time_seconds, 0) / lessons.length

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-green-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">AI-Generated Lessons</h1>
          <p className="text-gray-600">Ultra-fast lesson creation and management</p>
        </div>
        <Button>
          <Zap className="h-4 w-4 mr-2" />
          Generate Lesson
        </Button>
      </div>

      {/* Search */}
      <div className="flex space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search lessons..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{lessons.length}</div>
            <p className="text-sm text-gray-600">Total Lessons</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">
              {lessons.filter((l) => l.status === "published").length}
            </div>
            <p className="text-sm text-gray-600">Published</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-blue-600">{Math.round(averageGenerationTime)}s</div>
            <p className="text-sm text-gray-600">Avg Generation Time</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-purple-600">
              {lessons.reduce((acc, l) => acc + l.interactive_elements, 0)}
            </div>
            <p className="text-sm text-gray-600">Interactive Elements</p>
          </CardContent>
        </Card>
      </div>

      {/* Ultra-Fast Generation Highlight */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-blue-600" />
            <span>Ultra-Fast AI Generation</span>
          </CardTitle>
          <CardDescription>Average lesson creation time: {Math.round(averageGenerationTime)} seconds</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-blue-600">91.4%</div>
              <div className="text-sm text-gray-600">AI Generation Time</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-green-600">8.6%</div>
              <div className="text-sm text-gray-600">Save Operations</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-purple-600">80%</div>
              <div className="text-sm text-gray-600">Faster than Traditional</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lessons Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredLessons.map((lesson) => (
          <Card key={lesson.id} className="card-hover">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{lesson.title}</CardTitle>
                  <CardDescription>
                    {lesson.subject} • {lesson.topic}
                    {lesson.student_name && ` • ${lesson.student_name}`}
                  </CardDescription>
                </div>
                <Badge className={getStatusColor(lesson.status)}>
                  {lesson.status.charAt(0).toUpperCase() + lesson.status.slice(1)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-lg font-semibold">{lesson.slides_count}</div>
                  <div className="text-xs text-gray-600">Slides</div>
                </div>
                <div>
                  <div className="text-lg font-semibold">{lesson.estimated_duration_minutes}m</div>
                  <div className="text-xs text-gray-600">Duration</div>
                </div>
                <div>
                  <div className="text-lg font-semibold">{lesson.interactive_elements}</div>
                  <div className="text-xs text-gray-600">Interactive</div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-blue-600">{lesson.generation_time_seconds}s</div>
                  <div className="text-xs text-gray-600">Generated</div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {lesson.chatbot_enabled && (
                    <Badge variant="outline" className="text-xs">
                      <MessageSquare className="h-3 w-3 mr-1" />
                      Chatbot
                    </Badge>
                  )}
                  {lesson.learning_path_id && (
                    <Badge variant="outline" className="text-xs">
                      Path Lesson
                    </Badge>
                  )}
                </div>
                <span className="text-xs text-gray-500">Grade {lesson.target_grade}</span>
              </div>

              <div className="flex justify-between items-center pt-2">
                <span className="text-xs text-gray-500">
                  Created: {new Date(lesson.created_at).toLocaleDateString()}
                </span>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    <Eye className="h-3 w-3 mr-1" />
                    Preview
                  </Button>
                  {lesson.status === "published" && (
                    <Button size="sm" variant="outline">
                      <Play className="h-3 w-3 mr-1" />
                      Launch
                    </Button>
                  )}
                  <Button size="sm" variant="outline">
                    <Edit className="h-3 w-3 mr-1" />
                    Edit
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
