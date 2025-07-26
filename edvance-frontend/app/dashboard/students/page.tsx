"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Search, Filter, Plus, TrendingUp, TrendingDown, Minus, Eye, MessageSquare, Target } from "lucide-react"

interface Student {
  id: string
  name: string
  email: string
  grade: number
  subjects: string[]
  overall_progress: number
  active_paths: number
  completed_assessments: number
  performance_trend: "up" | "down" | "stable"
  last_activity: string
  needs_support: boolean
  ready_for_enrichment: boolean
}

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Mock student data
    const mockStudents: Student[] = [
      {
        id: "student_001",
        name: "Sarah Johnson",
        email: "sarah.j@school.edu",
        grade: 5,
        subjects: ["Mathematics", "Science"],
        overall_progress: 85.5,
        active_paths: 2,
        completed_assessments: 12,
        performance_trend: "up",
        last_activity: "2 hours ago",
        needs_support: false,
        ready_for_enrichment: true,
      },
      {
        id: "student_002",
        name: "Michael Chen",
        email: "michael.c@school.edu",
        grade: 5,
        subjects: ["Mathematics", "English"],
        overall_progress: 72.3,
        active_paths: 3,
        completed_assessments: 8,
        performance_trend: "stable",
        last_activity: "1 day ago",
        needs_support: false,
        ready_for_enrichment: false,
      },
      {
        id: "student_003",
        name: "Emma Davis",
        email: "emma.d@school.edu",
        grade: 5,
        subjects: ["Mathematics"],
        overall_progress: 45.2,
        active_paths: 1,
        completed_assessments: 5,
        performance_trend: "down",
        last_activity: "3 hours ago",
        needs_support: true,
        ready_for_enrichment: false,
      },
      {
        id: "student_004",
        name: "James Wilson",
        email: "james.w@school.edu",
        grade: 5,
        subjects: ["Science", "Mathematics"],
        overall_progress: 91.7,
        active_paths: 1,
        completed_assessments: 15,
        performance_trend: "up",
        last_activity: "30 minutes ago",
        needs_support: false,
        ready_for_enrichment: true,
      },
      {
        id: "student_005",
        name: "Olivia Brown",
        email: "olivia.b@school.edu",
        grade: 5,
        subjects: ["English", "Mathematics"],
        overall_progress: 68.9,
        active_paths: 2,
        completed_assessments: 9,
        performance_trend: "up",
        last_activity: "5 hours ago",
        needs_support: false,
        ready_for_enrichment: false,
      },
    ]

    setTimeout(() => {
      setStudents(mockStudents)
      setLoading(false)
    }, 1000)
  }, [])

  const filteredStudents = students.filter(
    (student) =>
      student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.email.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case "down":
        return <TrendingDown className="h-4 w-4 text-red-600" />
      default:
        return <Minus className="h-4 w-4 text-gray-600" />
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

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
          <h1 className="text-3xl font-bold">Students</h1>
          <p className="text-gray-600">Manage and monitor your students' progress</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Student
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search students..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{students.length}</div>
            <p className="text-sm text-gray-600">Total Students</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-red-600">{students.filter((s) => s.needs_support).length}</div>
            <p className="text-sm text-gray-600">Need Support</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">
              {students.filter((s) => s.ready_for_enrichment).length}
            </div>
            <p className="text-sm text-gray-600">Ready for Enrichment</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">
              {Math.round(students.reduce((acc, s) => acc + s.overall_progress, 0) / students.length)}%
            </div>
            <p className="text-sm text-gray-600">Average Progress</p>
          </CardContent>
        </Card>
      </div>

      {/* Students List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredStudents.map((student) => (
          <Card key={student.id} className="card-hover">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Avatar>
                    <AvatarImage src={`/placeholder.svg?height=40&width=40`} />
                    <AvatarFallback>{getInitials(student.name)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-lg">{student.name}</CardTitle>
                    <CardDescription>{student.email}</CardDescription>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getTrendIcon(student.performance_trend)}
                  {student.needs_support && <Badge variant="destructive">Needs Support</Badge>}
                  {student.ready_for_enrichment && <Badge variant="default">Enrichment Ready</Badge>}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Overall Progress</span>
                  <span>{student.overall_progress}%</span>
                </div>
                <Progress value={student.overall_progress} />
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-semibold">{student.active_paths}</div>
                  <div className="text-xs text-gray-600">Active Paths</div>
                </div>
                <div>
                  <div className="text-lg font-semibold">{student.completed_assessments}</div>
                  <div className="text-xs text-gray-600">Assessments</div>
                </div>
                <div>
                  <div className="text-lg font-semibold">{student.subjects.length}</div>
                  <div className="text-xs text-gray-600">Subjects</div>
                </div>
              </div>

              <div className="flex flex-wrap gap-1">
                {student.subjects.map((subject) => (
                  <Badge key={subject} variant="outline" className="text-xs">
                    {subject}
                  </Badge>
                ))}
              </div>

              <div className="flex justify-between items-center pt-2">
                <span className="text-xs text-gray-500">Last active: {student.last_activity}</span>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    <Eye className="h-3 w-3 mr-1" />
                    View
                  </Button>
                  <Button size="sm" variant="outline">
                    <Target className="h-3 w-3 mr-1" />
                    Paths
                  </Button>
                  <Button size="sm" variant="outline">
                    <MessageSquare className="h-3 w-3 mr-1" />
                    Chat
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
