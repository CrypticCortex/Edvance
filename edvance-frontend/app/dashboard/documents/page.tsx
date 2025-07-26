"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Plus, Upload, FileText, Download, Eye, Trash2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"

interface Document {
    id: string
    filename: string
    subject: string
    grade_level: number
    file_type: string
    file_size: number
    upload_date: string
    processed_status?: string
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([])
    const [loading, setLoading] = useState(true)
    const { toast } = useToast()

    useEffect(() => {
        const loadDocuments = async () => {
            try {
                // Load documents from the API
                const response = await apiService.listDocuments() as any

                if (response.success && response.data) {
                    setDocuments(response.data)
                } else {
                    console.warn('Failed to load documents from API')
                    setDocuments([])
                }
            } catch (error: any) {
                console.error('Error loading documents:', error)
                toast({
                    title: "Error Loading Documents",
                    description: handleApiError(error),
                    variant: "destructive"
                })
                setDocuments([])
            } finally {
                setLoading(false)
            }
        }

        loadDocuments()
    }, [toast])

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes'
        const k = 1024
        const sizes = ['Bytes', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const getFileIcon = (fileType: string) => {
        return <FileText className="w-6 h-6 text-blue-500" />
    }

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Documents</h1>
                        <p className="text-muted-foreground">Manage your uploaded documents</p>
                    </div>
                    <Button disabled>
                        <Plus className="w-4 h-4 mr-2" />
                        Upload Document
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
                    <h1 className="text-2xl font-bold">Documents</h1>
                    <p className="text-muted-foreground">
                        Manage and upload documents for your teaching materials
                    </p>
                </div>
                <Link href="/dashboard/documents/upload">
                    <Button>
                        <Plus className="w-4 h-4 mr-2" />
                        Upload Document
                    </Button>
                </Link>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-2">
                            <FileText className="w-5 h-5 text-blue-500" />
                            <div>
                                <p className="text-sm text-muted-foreground">Total Documents</p>
                                <p className="text-2xl font-bold">{documents.length}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-2">
                            <Upload className="w-5 h-5 text-green-500" />
                            <div>
                                <p className="text-sm text-muted-foreground">Total Size</p>
                                <p className="text-2xl font-bold">
                                    {formatFileSize(documents.reduce((sum, doc) => sum + (doc.file_size || 0), 0))}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-2">
                            <FileText className="w-5 h-5 text-yellow-500" />
                            <div>
                                <p className="text-sm text-muted-foreground">Subjects</p>
                                <p className="text-2xl font-bold">
                                    {new Set(documents.map(doc => doc.subject)).size}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-2">
                            <Eye className="w-5 h-5 text-purple-500" />
                            <div>
                                <p className="text-sm text-muted-foreground">Processed</p>
                                <p className="text-2xl font-bold">
                                    {documents.filter(doc => doc.processed_status === 'completed').length}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Documents List */}
            {documents.length === 0 ? (
                <Card className="text-center p-12">
                    <CardContent>
                        <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                        <h3 className="text-lg font-semibold mb-2">No documents yet</h3>
                        <p className="text-muted-foreground mb-4">
                            Upload your first document to get started with AI-powered content analysis
                        </p>
                        <Link href="/dashboard/documents/upload">
                            <Button>
                                <Plus className="w-4 h-4 mr-2" />
                                Upload Your First Document
                            </Button>
                        </Link>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {documents.map((document) => (
                        <Card key={document.id} className="hover:shadow-lg transition-shadow">
                            <CardHeader>
                                <div className="flex items-start gap-3">
                                    {getFileIcon(document.file_type)}
                                    <div className="flex-1 min-w-0">
                                        <CardTitle className="text-lg truncate">{document.filename}</CardTitle>
                                        <CardDescription>
                                            {document.subject} • Grade {document.grade_level}
                                        </CardDescription>
                                    </div>
                                    <Badge variant="secondary" className="text-xs">
                                        {document.file_type.toUpperCase()}
                                    </Badge>
                                </div>
                            </CardHeader>

                            <CardContent className="space-y-4">
                                {/* File Info */}
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Size:</span>
                                        <span className="font-medium">{formatFileSize(document.file_size)}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Subject:</span>
                                        <span className="font-medium">{document.subject}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Grade Level:</span>
                                        <span className="font-medium">{document.grade_level}</span>
                                    </div>
                                    {document.processed_status && (
                                        <div className="flex justify-between text-sm">
                                            <span className="text-muted-foreground">Status:</span>
                                            <Badge
                                                variant={document.processed_status === 'completed' ? 'default' : 'secondary'}
                                                className="text-xs"
                                            >
                                                {document.processed_status}
                                            </Badge>
                                        </div>
                                    )}
                                </div>

                                {/* Actions */}
                                <div className="flex gap-2 pt-2">
                                    <Button variant="outline" size="sm" className="flex-1">
                                        <Eye className="w-4 h-4 mr-2" />
                                        View
                                    </Button>
                                    <Button variant="outline" size="sm">
                                        <Download className="w-4 h-4 mr-2" />
                                        Download
                                    </Button>
                                    <Button variant="outline" size="sm">
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>

                                {/* Upload Date */}
                                <p className="text-xs text-muted-foreground">
                                    Uploaded {new Date(document.upload_date).toLocaleDateString()}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    )
}
