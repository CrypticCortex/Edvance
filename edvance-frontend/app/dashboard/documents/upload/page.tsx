"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
    Upload,
    FileText,
    FileArchive,
    File,
    CheckCircle,
    XCircle,
    AlertCircle,
    Trash2,
    ArrowLeft
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"

interface UploadedFile {
    file: File
    status: 'pending' | 'uploading' | 'success' | 'error'
    progress: number
    error?: string
    id: string
}

export default function DocumentsUploadPage() {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
    const [isDragOver, setIsDragOver] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const [subject, setSubject] = useState("")
    const [gradeLevel, setGradeLevel] = useState<number>(1)
    const { toast } = useToast()
    const router = useRouter()

    // Accepted file types
    const acceptedTypes = ['.pdf', '.txt', '.zip', '.docx', '.doc']
    const maxFileSize = 50 * 1024 * 1024 // 50MB

    // Subject options (you can customize these based on your needs)
    const subjectOptions = [
        "Mathematics", "Science", "English", "History", "Geography",
        "Physics", "Chemistry", "Biology", "Literature", "Arts",
        "Computer Science", "Social Studies", "Foreign Language"
    ]

    // Grade level options
    const gradeLevelOptions = Array.from({ length: 12 }, (_, i) => i + 1)

    const getFileIcon = (fileName: string) => {
        const extension = fileName.toLowerCase().split('.').pop()
        switch (extension) {
            case 'pdf':
                return <FileText className="h-6 w-6 text-red-500" />
            case 'txt':
                return <FileText className="h-6 w-6 text-blue-500" />
            case 'zip':
                return <FileArchive className="h-6 w-6 text-yellow-500" />
            case 'doc':
            case 'docx':
                return <FileText className="h-6 w-6 text-blue-600" />
            default:
                return <File className="h-6 w-6 text-gray-500" />
        }
    }

    const isValidFileType = (fileName: string): boolean => {
        const extension = '.' + fileName.toLowerCase().split('.').pop()
        return acceptedTypes.includes(extension)
    }

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes'
        const k = 1024
        const sizes = ['Bytes', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const addFilesToQueue = (files: FileList | File[]) => {
        const fileArray = Array.from(files)
        const validFiles: UploadedFile[] = []

        fileArray.forEach((file) => {
            if (!isValidFileType(file.name)) {
                toast({
                    title: "Invalid File Type",
                    description: `${file.name} is not a supported file type. Supported: ${acceptedTypes.join(', ')}`,
                    variant: "destructive",
                })
                return
            }

            if (file.size > maxFileSize) {
                toast({
                    title: "File Too Large",
                    description: `${file.name} is larger than 50MB. Please choose a smaller file.`,
                    variant: "destructive",
                })
                return
            }

            validFiles.push({
                file,
                status: 'pending',
                progress: 0,
                id: Math.random().toString(36).substr(2, 9)
            })
        })

        setUploadedFiles(prev => [...prev, ...validFiles])
    }

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files
        if (files && files.length > 0) {
            addFilesToQueue(files)
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
            addFilesToQueue(files)
        }
    }, [])

    const removeFile = (id: string) => {
        setUploadedFiles(prev => prev.filter(file => file.id !== id))
    }

    const uploadFiles = async () => {
        const filesToUpload = uploadedFiles.filter(f => f.status === 'pending')

        if (filesToUpload.length === 0) {
            toast({
                title: "No Files to Upload",
                description: "Please add some files before uploading.",
                variant: "destructive",
            })
            return
        }

        if (!subject) {
            toast({
                title: "Subject Required",
                description: "Please select a subject before uploading.",
                variant: "destructive",
            })
            return
        }

        setIsUploading(true)

        try {
            // Update status to uploading
            setUploadedFiles(prev =>
                prev.map(file =>
                    filesToUpload.some(f => f.id === file.id)
                        ? { ...file, status: 'uploading' as const, progress: 0 }
                        : file
                )
            )

            // Upload files one by one (backend expects single file)
            for (const uploadedFile of filesToUpload) {
                try {
                    // Simulate progress update
                    const progressInterval = setInterval(() => {
                        setUploadedFiles(prev =>
                            prev.map(file =>
                                file.id === uploadedFile.id && file.status === 'uploading' && file.progress < 90
                                    ? { ...file, progress: file.progress + 10 }
                                    : file
                            )
                        )
                    }, 200)

                    // Upload single file with subject and grade level
                    const result = await apiService.uploadDocument(uploadedFile.file, subject, gradeLevel)

                    clearInterval(progressInterval)

                    // Update status to success
                    setUploadedFiles(prev =>
                        prev.map(file =>
                            file.id === uploadedFile.id
                                ? { ...file, status: 'success' as const, progress: 100 }
                                : file
                        )
                    )

                } catch (error: any) {
                    console.error('Upload error for file:', uploadedFile.file.name, error)

                    // Update status to error for this specific file
                    setUploadedFiles(prev =>
                        prev.map(file =>
                            file.id === uploadedFile.id
                                ? { ...file, status: 'error' as const, error: handleApiError(error) }
                                : file
                        )
                    )
                }
            }

            const successCount = uploadedFiles.filter(f => f.status === 'success').length
            if (successCount > 0) {
                toast({
                    title: "Upload Successful",
                    description: `Successfully uploaded ${successCount} file(s)`,
                })

                // Redirect back to dashboard after 2 seconds
                setTimeout(() => {
                    router.push('/dashboard')
                }, 2000)
            }

        } catch (error: any) {
            console.error('General upload error:', error)

            toast({
                title: "Upload Failed",
                description: handleApiError(error),
                variant: "destructive",
            })
        } finally {
            setIsUploading(false)
        }
    }

    const pendingFiles = uploadedFiles.filter(f => f.status === 'pending')
    const successFiles = uploadedFiles.filter(f => f.status === 'success')
    const errorFiles = uploadedFiles.filter(f => f.status === 'error')

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center space-x-4">
                <Button
                    variant="ghost"
                    onClick={() => router.push('/dashboard')}
                    className="p-2"
                >
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Upload Documents</h1>
                    <p className="text-gray-600">Upload learning materials for AI processing</p>
                </div>
            </div>

            {/* Subject and Grade Level Selection */}
            <Card>
                <CardHeader>
                    <CardTitle>Document Information</CardTitle>
                    <CardDescription>
                        Specify the subject and grade level for better AI processing
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="subject">Subject</Label>
                            <Select value={subject} onValueChange={setSubject}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a subject" />
                                </SelectTrigger>
                                <SelectContent>
                                    {subjectOptions.map((subjectOption) => (
                                        <SelectItem key={subjectOption} value={subjectOption}>
                                            {subjectOption}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="grade-level">Grade Level</Label>
                            <Select value={gradeLevel.toString()} onValueChange={(value) => setGradeLevel(parseInt(value))}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select grade level" />
                                </SelectTrigger>
                                <SelectContent>
                                    {gradeLevelOptions.map((grade) => (
                                        <SelectItem key={grade} value={grade.toString()}>
                                            Grade {grade}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Upload Area */}
            <Card>
                <CardHeader>
                    <CardTitle>Upload Files</CardTitle>
                    <CardDescription>
                        Select subject and grade level, then drag and drop your files here or click to browse.
                        Supported formats: PDF, TXT, ZIP, DOC, DOCX (max 50MB each)
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div
                        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${isDragOver
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-300 hover:border-gray-400'
                            }`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Drop files here
                        </h3>
                        <p className="text-gray-600 mb-4">
                            or click to browse files
                        </p>
                        <input
                            type="file"
                            multiple
                            accept={acceptedTypes.join(',')}
                            onChange={handleFileSelect}
                            className="hidden"
                            id="file-upload"
                        />
                        <label
                            htmlFor="file-upload"
                            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
                        >
                            Choose Files
                        </label>
                    </div>
                </CardContent>
            </Card>

            {/* File List */}
            {uploadedFiles.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Files ({uploadedFiles.length})</CardTitle>
                        <div className="flex space-x-2">
                            {pendingFiles.length > 0 && (
                                <Badge variant="secondary">{pendingFiles.length} Pending</Badge>
                            )}
                            {successFiles.length > 0 && (
                                <Badge variant="default">{successFiles.length} Uploaded</Badge>
                            )}
                            {errorFiles.length > 0 && (
                                <Badge variant="destructive">{errorFiles.length} Failed</Badge>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {uploadedFiles.map((uploadedFile) => (
                                <div key={uploadedFile.id} className="flex items-center space-x-3 p-3 border rounded-lg">
                                    {getFileIcon(uploadedFile.file.name)}

                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium text-gray-900 truncate">
                                            {uploadedFile.file.name}
                                        </p>
                                        <p className="text-sm text-gray-500">
                                            {formatFileSize(uploadedFile.file.size)}
                                        </p>

                                        {uploadedFile.status === 'uploading' && (
                                            <Progress value={uploadedFile.progress} className="mt-2" />
                                        )}

                                        {uploadedFile.status === 'error' && uploadedFile.error && (
                                            <p className="text-sm text-red-600 mt-1">{uploadedFile.error}</p>
                                        )}
                                    </div>

                                    <div className="flex items-center space-x-2">
                                        {uploadedFile.status === 'pending' && (
                                            <AlertCircle className="h-5 w-5 text-yellow-500" />
                                        )}
                                        {uploadedFile.status === 'uploading' && (
                                            <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-blue-600"></div>
                                        )}
                                        {uploadedFile.status === 'success' && (
                                            <CheckCircle className="h-5 w-5 text-green-500" />
                                        )}
                                        {uploadedFile.status === 'error' && (
                                            <XCircle className="h-5 w-5 text-red-500" />
                                        )}

                                        {(uploadedFile.status === 'pending' || uploadedFile.status === 'error') && (
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => removeFile(uploadedFile.id)}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {pendingFiles.length > 0 && (
                            <div className="mt-6 pt-6 border-t">
                                {!subject && (
                                    <Alert className="mb-4">
                                        <AlertCircle className="h-4 w-4" />
                                        <AlertDescription>
                                            Please select a subject before uploading files.
                                        </AlertDescription>
                                    </Alert>
                                )}
                                <Button
                                    onClick={uploadFiles}
                                    disabled={isUploading || !subject}
                                    className="w-full"
                                >
                                    {isUploading ? 'Uploading...' : `Upload ${pendingFiles.length} File(s)`}
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}

            {/* Help Information */}
            <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                    <strong>Tip:</strong> Upload textbooks, lesson plans, and educational materials.
                    The AI will process these documents to generate personalized learning content and assessments.
                </AlertDescription>
            </Alert>
        </div>
    )
}
