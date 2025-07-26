"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Search, Filter, Plus, TrendingUp, TrendingDown, Minus, Eye, MessageSquare, Target, Upload, RefreshCw, Trash2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"
import CSVUpload from "@/components/dashboard/csv-upload"
import StudentDetailsModal from "@/components/dashboard/student-details-modal"
import LearningPathsModal from "@/components/dashboard/learning-paths-modal"

interface Student {
  student_id: string
  first_name: string
  last_name: string
  email?: string
  grade: number
  subjects: string[]
  overall_progress?: number
  active_paths?: number
  completed_assessments?: number
  performance_trend?: "up" | "down" | "stable"
  last_activity?: string
  needs_support?: boolean
  ready_for_enrichment?: boolean
  created_at: string
  teacher_id: string
}

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)

  // Modal states
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)
  const [studentDetailsOpen, setStudentDetailsOpen] = useState(false)
  const [learningPathsOpen, setLearningPathsOpen] = useState(false)
  const [learningPaths, setLearningPaths] = useState<any[]>([])
  const [pathsLoading, setPathsLoading] = useState(false)

  const { toast } = useToast()

  const loadStudents = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    try {
      const response = await apiService.getStudents()
      console.log('Students API response:', response)

      if (response && Array.isArray(response)) {
        setStudents(response)

        if (isRefresh && response.length > 0) {
          toast({
            title: "Students Refreshed",
            description: `Found ${response.length} student(s)`,
          })
        } else if (response.length === 0 && !isRefresh) {
          toast({
            title: "No Students Found",
            description: "Upload a CSV file to add students to your class!",
          })
        }
      } else {
        console.warn('Invalid students response:', response)
        setStudents([])
      }
    } catch (error: any) {
      console.error('Error loading students:', error)

      // For demo purposes, if API fails, show some mock data
      if (!isRefresh) {
        const mockStudents: Student[] = [
          {
            student_id: "student_001",
            first_name: "Sarah",
            last_name: "Johnson",
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
            created_at: new Date().toISOString(),
            teacher_id: "teacher_001"
          },
        ]
        setStudents(mockStudents)
      }

      toast({
        title: "Error Loading Students",
        description: handleApiError(error),
        variant: "destructive"
      })
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadStudents()
  }, [])

  const handleUploadComplete = async (result: any) => {
    console.log('Upload completed:', result)
    setUploadDialogOpen(false)

    // Refresh the students list
    await loadStudents(true)
  }

  const filteredStudents = students.filter(
    (student) =>
      `${student.first_name} ${student.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (student.email && student.email.toLowerCase().includes(searchTerm.toLowerCase())),
  )

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case "down":
        return <TrendingDown className="h-4 w-4 text-red-600" />
      default:
        return <Minus className="h-4 w-4 text-gray-600" />
    }
  }

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName[0]}${lastName[0]}`.toUpperCase()
  }

  const getStudentName = (student: Student) => {
    return `${student.first_name} ${student.last_name}`
  }

  const handleViewStudent = async (studentId: string) => {
    try {
      const studentDetails = await apiService.getStudent(studentId) as Student
      console.log('Student details:', studentDetails)

      setSelectedStudent(studentDetails)
      setStudentDetailsOpen(true)

    } catch (error: any) {
      console.error('Error fetching student details:', error)
      toast({
        title: "Error",
        description: handleApiError(error),
        variant: "destructive"
      })
    }
  }

  const handleViewPaths = async (studentId: string) => {
    const student = students.find(s => s.student_id === studentId)
    if (!student) return

    setSelectedStudent(student)
    setLearningPathsOpen(true)
    setPathsLoading(true)

    try {
      const paths = await apiService.getStudentLearningPaths(studentId)
      console.log('Student learning paths:', paths)

      // Handle different response formats
      const pathsArray = Array.isArray(paths) ? paths : ((paths as any)?.data || [])
      setLearningPaths(pathsArray)

    } catch (error: any) {
      console.error('Error fetching learning paths:', error)
      toast({
        title: "Error Loading Paths",
        description: handleApiError(error),
        variant: "destructive"
      })
      setLearningPaths([])
    } finally {
      setPathsLoading(false)
    }
  }

  const handleDeleteStudent = async (studentId: string, studentName: string) => {
    if (!confirm(`Are you sure you want to delete ${studentName}? This action cannot be undone.`)) {
      return
    }

    try {
      await apiService.deleteStudent(studentId)

      toast({
        title: "Student Deleted",
        description: `${studentName} has been successfully deleted`,
      })

      // Refresh the students list
      await loadStudents(true)
    } catch (error: any) {
      console.error('Error deleting student:', error)
      toast({
        title: "Error",
        description: handleApiError(error),
        variant: "destructive"
      })
    }
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
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => loadStudents(true)}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload CSV
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Upload Students from CSV</DialogTitle>
                <DialogDescription>
                  Import multiple students at once using a CSV file
                </DialogDescription>
              </DialogHeader>
              <CSVUpload onUploadComplete={handleUploadComplete} />
            </DialogContent>
          </Dialog>
        </div>
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
              {students.length > 0 ? Math.round(students.reduce((acc, s) => acc + (s.overall_progress || 0), 0) / students.length) : 0}%
            </div>
            <p className="text-sm text-gray-600">Average Progress</p>
          </CardContent>
        </Card>
      </div>

      {/* Students List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredStudents.map((student) => (
          <Card key={student.student_id} className="card-hover">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Avatar>
                    <AvatarImage src={`/placeholder.svg?height=40&width=40`} />
                    <AvatarFallback>{getInitials(student.first_name, student.last_name)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-lg">{getStudentName(student)}</CardTitle>
                    <CardDescription>{student.email || `Grade ${student.grade} Student`}</CardDescription>
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
                  <span>{student.overall_progress || 0}%</span>
                </div>
                <Progress value={student.overall_progress || 0} />
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-semibold">{student.active_paths || 0}</div>
                  <div className="text-xs text-gray-600">Active Paths</div>
                </div>
                <div>
                  <div className="text-lg font-semibold">{student.completed_assessments || 0}</div>
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
                <span className="text-xs text-gray-500">
                  Last active: {student.last_activity || 'Unknown'}
                </span>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleViewStudent(student.student_id)}
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    View
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleViewPaths(student.student_id)}
                  >
                    <Target className="h-3 w-3 mr-1" />
                    Paths
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDeleteStudent(student.student_id, getStudentName(student))}
                  >
                    <Trash2 className="h-3 w-3 mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Modals */}
      <StudentDetailsModal
        student={selectedStudent}
        open={studentDetailsOpen}
        onOpenChange={setStudentDetailsOpen}
      />

      <LearningPathsModal
        student={selectedStudent}
        paths={learningPaths}
        open={learningPathsOpen}
        onOpenChange={setLearningPathsOpen}
        loading={pathsLoading}
      />
    </div>
  )
}
