"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import {
    Upload,
    FileText,
    CheckCircle,
    XCircle,
    AlertCircle,
    Trash2,
    Download,
    Info
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"

interface CSVUploadResponse {
    total_students: number;
    students_created: number;
    students_updated: number;
    students_failed: number;
    failed_students: any[];
    created_student_ids: string[];
    upload_summary: string;
}

interface UploadedFile {
    file: File
    status: 'pending' | 'uploading' | 'success' | 'error'
    progress: number
    error?: string
    id: string
    result?: CSVUploadResponse
}

interface CSVUploadProps {
    onUploadComplete: (result: CSVUploadResponse) => void
}

export default function CSVUpload({ onUploadComplete }: CSVUploadProps) {
    const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null)
    const [isUploading, setIsUploading] = useState(false)
    const [isDragOver, setIsDragOver] = useState(false)
    const { toast } = useToast()

    const addFileToQueue = (files: FileList) => {
        if (files.length === 0) return

        const file = files[0]

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.csv')) {
            toast({
                title: "Invalid File Type",
                description: "Please select a CSV file (.csv)",
                variant: "destructive",
            })
            return
        }

        // Validate file size (max 10MB for CSV)
        if (file.size > 10 * 1024 * 1024) {
            toast({
                title: "File Too Large",
                description: `${file.name} is larger than 10MB. Please choose a smaller file.`,
                variant: "destructive",
            })
            return
        }

        setUploadedFile({
            file,
            status: 'pending',
            progress: 0,
            id: Math.random().toString(36).substr(2, 9)
        })
    }

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files
        if (files && files.length > 0) {
            addFileToQueue(files)
        }
    }

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(true)
    }, [])

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(false)
    }, [])

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragOver(false)

        const files = e.dataTransfer.files
        if (files && files.length > 0) {
            addFileToQueue(files)
        }
    }, [])

    const removeFile = () => {
        setUploadedFile(null)
    }

    const uploadFile = async () => {
        if (!uploadedFile || uploadedFile.status !== 'pending') return

        setIsUploading(true)

        try {
            // Update status to uploading
            setUploadedFile(prev => prev ? { ...prev, status: 'uploading', progress: 0 } : null)

            // Simulate progress updates
            const progressInterval = setInterval(() => {
                setUploadedFile(prev =>
                    prev && prev.status === 'uploading' && prev.progress < 90
                        ? { ...prev, progress: prev.progress + 10 }
                        : prev
                )
            }, 200)

            // Upload the CSV file
            const result = await apiService.uploadStudentsCSV(uploadedFile.file)

            clearInterval(progressInterval)

            // Update status to success
            setUploadedFile(prev => prev ? {
                ...prev,
                status: 'success',
                progress: 100,
                result
            } : null)

            toast({
                title: "Upload Successful",
                description: result.upload_summary,
            })

            // Call the callback
            onUploadComplete(result)

        } catch (error: any) {
            console.error('Upload error:', error)

            setUploadedFile(prev => prev ? {
                ...prev,
                status: 'error',
                error: handleApiError(error)
            } : null)

            toast({
                title: "Upload Failed",
                description: handleApiError(error),
                variant: "destructive",
            })
        } finally {
            setIsUploading(false)
        }
    }

    const downloadSampleCSV = () => {
        const csvContent = "first_name,last_name,grade,password\nJohn,Doe,5,student123\nJane,Smith,5,student456\nMike,Johnson,6,student789"
        const blob = new Blob([csvContent], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'students_sample.csv'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
    }

    const getFileIcon = () => {
        return <FileText className="h-8 w-8 text-green-600" />
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'success':
                return <CheckCircle className="h-5 w-5 text-green-600" />
            case 'error':
                return <XCircle className="h-5 w-5 text-red-600" />
            case 'uploading':
                return <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-blue-600" />
            default:
                return <AlertCircle className="h-5 w-5 text-gray-600" />
        }
    }

    return (
        <div className="space-y-6">
            {/* CSV Format Info */}
            <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                    <div className="space-y-2">
                        <p><strong>CSV Format Requirements:</strong></p>
                        <p>Your CSV file must include these columns: <code>first_name</code>, <code>last_name</code>, <code>grade</code>, <code>password</code></p>
                        <div className="flex items-center space-x-2 mt-2">
                            <Button variant="outline" size="sm" onClick={downloadSampleCSV}>
                                <Download className="h-4 w-4 mr-2" />
                                Download Sample CSV
                            </Button>
                        </div>
                    </div>
                </AlertDescription>
            </Alert>

            {/* Upload Area */}
            <Card>
                <CardHeader>
                    <CardTitle>Upload Students CSV</CardTitle>
                    <CardDescription>
                        Upload a CSV file containing student information to bulk import students
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {/* Drag and Drop Zone */}
                    <div
                        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${isDragOver
                                ? "border-blue-500 bg-blue-50"
                                : "border-gray-300 hover:border-gray-400"
                            }`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                        <h3 className="text-lg font-semibold mb-2">Drop your CSV file here</h3>
                        <p className="text-gray-600 mb-4">or click to browse files</p>
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileSelect}
                            className="hidden"
                            id="file-upload"
                        />
                        <label htmlFor="file-upload">
                            <Button variant="outline" className="cursor-pointer">
                                Choose CSV File
                            </Button>
                        </label>
                    </div>

                    {/* File Preview */}
                    {uploadedFile && (
                        <div className="mt-6">
                            <h4 className="font-semibold mb-3">File Ready for Upload</h4>
                            <div className="border rounded-lg p-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        {getFileIcon()}
                                        <div>
                                            <p className="font-medium">{uploadedFile.file.name}</p>
                                            <p className="text-sm text-gray-600">
                                                {(uploadedFile.file.size / 1024).toFixed(1)} KB
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        {getStatusIcon(uploadedFile.status)}
                                        <Badge variant={
                                            uploadedFile.status === 'success' ? 'default' :
                                                uploadedFile.status === 'error' ? 'destructive' :
                                                    uploadedFile.status === 'uploading' ? 'secondary' : 'outline'
                                        }>
                                            {uploadedFile.status === 'uploading' ? 'Uploading...' : uploadedFile.status}
                                        </Badge>
                                        {uploadedFile.status === 'pending' && (
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={removeFile}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        )}
                                    </div>
                                </div>

                                {/* Progress Bar */}
                                {uploadedFile.status === 'uploading' && (
                                    <div className="mt-3">
                                        <Progress value={uploadedFile.progress} className="w-full" />
                                        <p className="text-sm text-gray-600 mt-1">
                                            Uploading... {uploadedFile.progress}%
                                        </p>
                                    </div>
                                )}

                                {/* Error Message */}
                                {uploadedFile.status === 'error' && uploadedFile.error && (
                                    <Alert className="mt-3">
                                        <XCircle className="h-4 w-4" />
                                        <AlertDescription>{uploadedFile.error}</AlertDescription>
                                    </Alert>
                                )}

                                {/* Success Results */}
                                {uploadedFile.status === 'success' && uploadedFile.result && (
                                    <div className="mt-3 space-y-2">
                                        <Alert>
                                            <CheckCircle className="h-4 w-4" />
                                            <AlertDescription>
                                                <div className="space-y-1">
                                                    <p><strong>Upload Summary:</strong></p>
                                                    <p>Total Students: {uploadedFile.result.total_students}</p>
                                                    <p>Created: {uploadedFile.result.students_created}</p>
                                                    <p>Updated: {uploadedFile.result.students_updated}</p>
                                                    {uploadedFile.result.students_failed > 0 && (
                                                        <p className="text-red-600">Failed: {uploadedFile.result.students_failed}</p>
                                                    )}
                                                </div>
                                            </AlertDescription>
                                        </Alert>
                                    </div>
                                )}
                            </div>

                            {/* Upload Button */}
                            {uploadedFile.status === 'pending' && (
                                <div className="mt-4 flex justify-end">
                                    <Button
                                        onClick={uploadFile}
                                        disabled={isUploading}
                                    >
                                        <Upload className="h-4 w-4 mr-2" />
                                        Upload Students
                                    </Button>
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
