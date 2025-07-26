"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import {
    User,
    GraduationCap,
    BookOpen,
    TrendingUp,
    TrendingDown,
    Minus,
    Calendar,
    Clock,
    Target,
    Award,
    Activity
} from "lucide-react"

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

interface StudentDetailsModalProps {
    student: Student | null
    open: boolean
    onOpenChange: (open: boolean) => void
}

export default function StudentDetailsModal({ student, open, onOpenChange }: StudentDetailsModalProps) {
    if (!student) return null

    const getInitials = (firstName: string, lastName: string) => {
        return `${firstName[0]}${lastName[0]}`.toUpperCase()
    }

    const getStudentName = (student: Student) => {
        return `${student.first_name} ${student.last_name}`
    }

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

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="flex items-center space-x-3">
                        <Avatar className="h-10 w-10">
                            <AvatarImage src={`/placeholder.svg?height=40&width=40`} />
                            <AvatarFallback>{getInitials(student.first_name, student.last_name)}</AvatarFallback>
                        </Avatar>
                        <div>
                            <div className="text-xl font-bold">{getStudentName(student)}</div>
                            <div className="text-sm text-gray-600">{student.email || `Grade ${student.grade} Student`}</div>
                        </div>
                    </DialogTitle>
                    <DialogDescription>
                        Detailed information and progress overview
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6">
                    {/* Basic Information */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <User className="h-5 w-5" />
                                <span>Basic Information</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Student ID</label>
                                    <p className="text-sm text-gray-900 font-mono">{student.student_id}</p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Grade Level</label>
                                    <p className="text-sm text-gray-900 flex items-center">
                                        <GraduationCap className="h-4 w-4 mr-1" />
                                        Grade {student.grade}
                                    </p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Enrolled Date</label>
                                    <p className="text-sm text-gray-900 flex items-center">
                                        <Calendar className="h-4 w-4 mr-1" />
                                        {formatDate(student.created_at)}
                                    </p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-600">Last Activity</label>
                                    <p className="text-sm text-gray-900 flex items-center">
                                        <Clock className="h-4 w-4 mr-1" />
                                        {student.last_activity || 'Unknown'}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Performance Overview */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <Activity className="h-5 w-5" />
                                <span>Performance Overview</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Progress Bar */}
                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-sm font-medium">Overall Progress</span>
                                    <div className="flex items-center space-x-2">
                                        {getTrendIcon(student.performance_trend)}
                                        <span className="text-sm font-semibold">{student.overall_progress || 0}%</span>
                                    </div>
                                </div>
                                <Progress value={student.overall_progress || 0} className="h-3" />
                            </div>

                            {/* Stats Grid */}
                            <div className="grid grid-cols-3 gap-4 pt-4">
                                <div className="text-center p-3 bg-blue-50 rounded-lg">
                                    <div className="flex items-center justify-center mb-1">
                                        <Target className="h-5 w-5 text-blue-600" />
                                    </div>
                                    <div className="text-2xl font-bold text-blue-600">{student.active_paths || 0}</div>
                                    <div className="text-xs text-blue-600 font-medium">Active Paths</div>
                                </div>
                                <div className="text-center p-3 bg-green-50 rounded-lg">
                                    <div className="flex items-center justify-center mb-1">
                                        <Award className="h-5 w-5 text-green-600" />
                                    </div>
                                    <div className="text-2xl font-bold text-green-600">{student.completed_assessments || 0}</div>
                                    <div className="text-xs text-green-600 font-medium">Assessments</div>
                                </div>
                                <div className="text-center p-3 bg-purple-50 rounded-lg">
                                    <div className="flex items-center justify-center mb-1">
                                        <BookOpen className="h-5 w-5 text-purple-600" />
                                    </div>
                                    <div className="text-2xl font-bold text-purple-600">{student.subjects.length}</div>
                                    <div className="text-xs text-purple-600 font-medium">Subjects</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Subjects & Status */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <BookOpen className="h-5 w-5" />
                                <span>Subjects & Status</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Subjects */}
                            <div>
                                <label className="text-sm font-medium text-gray-600 mb-2 block">Enrolled Subjects</label>
                                <div className="flex flex-wrap gap-2">
                                    {student.subjects.map((subject) => (
                                        <Badge key={subject} variant="outline" className="px-3 py-1">
                                            {subject}
                                        </Badge>
                                    ))}
                                </div>
                            </div>

                            <Separator />

                            {/* Status Badges */}
                            <div>
                                <label className="text-sm font-medium text-gray-600 mb-2 block">Current Status</label>
                                <div className="flex flex-wrap gap-2">
                                    {student.needs_support && (
                                        <Badge variant="destructive" className="px-3 py-1">
                                            Needs Support
                                        </Badge>
                                    )}
                                    {student.ready_for_enrichment && (
                                        <Badge variant="default" className="px-3 py-1">
                                            Ready for Enrichment
                                        </Badge>
                                    )}
                                    {!student.needs_support && !student.ready_for_enrichment && (
                                        <Badge variant="secondary" className="px-3 py-1">
                                            On Track
                                        </Badge>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </DialogContent>
        </Dialog>
    )
}
