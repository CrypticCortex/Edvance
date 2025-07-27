"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { LanguageSelector } from "@/components/ui/language-selector"
import { useToast } from "@/hooks/use-toast"
import { useLanguage } from "@/contexts/LanguageContext"
import { apiService, handleApiError } from "@/lib/api"
import { ArrowLeft, Wand2, Eye, Save } from "lucide-react"
import Link from "next/link"

interface AssessmentConfig {
    name: string;
    subject: string;
    target_grade: number;
    difficulty_level: 'easy' | 'medium' | 'hard';
    topic: string;
    question_count: number;
    time_limit_minutes: number;
}

interface GeneratedQuestion {
    question?: string;
    question_text?: string;
    text?: string;
    prompt?: string;
    options?: string[];
    correct_answer?: string;
    explanation?: string;
    type?: string;
    [key: string]: any; // Allow for additional fields from backend
}

interface GeneratedAssessment {
    config_id?: string;
    assessment_id?: string;
    questions: GeneratedQuestion[];
    metadata?: {
        total_questions?: number;
        estimated_duration?: number;
        subject?: string;
        grade?: number;
        difficulty?: string;
    };
    [key: string]: any; // Allow for additional fields from backend
}

export default function CreateAssessmentPage() {
    const router = useRouter()
    const { toast } = useToast()
    const { currentLanguage } = useLanguage()

    const [formData, setFormData] = useState<AssessmentConfig>({
        name: '',
        subject: '',
        target_grade: 5,
        difficulty_level: 'medium',
        topic: '',
        question_count: 10,
        time_limit_minutes: 30
    })

    const [isCreating, setIsCreating] = useState(false)
    const [isGenerating, setIsGenerating] = useState(false)
    const [configId, setConfigId] = useState<string | null>(null)
    const [generatedAssessment, setGeneratedAssessment] = useState<GeneratedAssessment | null>(null)
    const [showPreview, setShowPreview] = useState(false)
    const [autoGenerate, setAutoGenerate] = useState(true) // Auto-generate after config creation

    const subjects = [
        'Mathematics',
        'Science',
        'English Language Arts',
        'Social Studies',
        'History',
        'Geography',
        'Physics',
        'Chemistry',
        'Biology'
    ]

    const grades = Array.from({ length: 8 }, (_, i) => i + 5) // Grades 5-12

    const handleInputChange = (field: keyof AssessmentConfig, value: any) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }))
    }

    // Shared function to generate assessment from config ID
    const generateAssessment = async (targetConfigId: string) => {
        if (!targetConfigId) {
            toast({
                title: "No Configuration",
                description: "Please create a configuration first",
                variant: "destructive"
            })
            return
        }

        setIsGenerating(true)
        try {
            console.log('Generating assessment with config ID:', targetConfigId)
            const response = await apiService.generateAssessmentFromConfig(targetConfigId, currentLanguage) as any
            console.log('Generate assessment response:', response)

            // Handle different response formats
            let assessmentData = null
            if (response.success && response.data) {
                assessmentData = response.data
            } else if (response.questions) {
                assessmentData = response
            } else if (response.data) {
                assessmentData = response.data
            }

            if (assessmentData) {
                console.log('Assessment data received:', assessmentData)
                console.log('Questions array:', assessmentData.questions)
                setGeneratedAssessment(assessmentData)
                setShowPreview(true)
                toast({
                    title: "Assessment Generated",
                    description: `Successfully generated ${assessmentData.questions?.length || formData.question_count} questions`
                })
            } else {
                throw new Error(response.message || response.error || 'Failed to generate assessment - no questions returned')
            }
        } catch (error: any) {
            toast({
                title: "Error Generating Assessment",
                description: handleApiError(error),
                variant: "destructive"
            })
        } finally {
            setIsGenerating(false)
        }
    }

    const handleCreateConfig = async () => {
        if (!formData.name || !formData.subject || !formData.topic) {
            toast({
                title: "Missing Information",
                description: "Please fill in all required fields",
                variant: "destructive"
            })
            return
        }

        setIsCreating(true)
        try {
            const response = await apiService.createAssessmentConfig(formData) as any
            console.log('Config creation response:', response)

            // Handle different response formats
            let configId = null
            if (response.success && response.data?.config_id) {
                configId = response.data.config_id
            } else if (response.config_id) {
                configId = response.config_id
            } else if (response.data?.id) {
                configId = response.data.id
            } else if (response.id) {
                configId = response.id
            }

            if (configId) {
                setConfigId(configId)
                toast({
                    title: "Configuration Created",
                    description: "Assessment configuration saved successfully"
                })

                // Auto-generate assessment if enabled
                if (autoGenerate) {
                    setTimeout(async () => {
                        await generateAssessment(configId)
                    }, 500) // Small delay to allow UI to update
                }
            } else {
                throw new Error(response.message || response.error || 'Failed to create configuration - no config ID returned')
            }
        } catch (error: any) {
            toast({
                title: "Error Creating Configuration",
                description: handleApiError(error),
                variant: "destructive"
            })
        } finally {
            setIsCreating(false)
        }
    }

    const handleGenerateAssessment = async () => {
        await generateAssessment(configId!)
    }

    const handleSaveAssessment = async () => {
        if (!generatedAssessment) return

        try {
            toast({
                title: "Assessment Saved",
                description: "Assessment has been saved successfully"
            })

            // Navigate to assessments list
            router.push('/dashboard/assessments')
        } catch (error: any) {
            toast({
                title: "Error Saving Assessment",
                description: handleApiError(error),
                variant: "destructive"
            })
        }
    }

    if (showPreview && generatedAssessment) {
        return (
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowPreview(false)}
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Form
                    </Button>
                    <div>
                        <h1 className="text-2xl font-bold">Assessment Preview</h1>
                        <p className="text-muted-foreground">
                            Review the AI-generated assessment before saving
                        </p>
                    </div>
                </div>

                {/* Preview Content */}
                <Card>
                    <CardHeader>
                        <CardTitle>{formData.name}</CardTitle>
                        <CardDescription>
                            {formData.subject} • Grade {formData.target_grade} • {formData.difficulty_level} difficulty
                        </CardDescription>
                        <div className="flex gap-4 text-sm text-muted-foreground">
                            <span>{generatedAssessment.questions.length} questions</span>
                            <span>{formData.time_limit_minutes} minutes</span>
                            <span>Topic: {formData.topic}</span>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            {generatedAssessment.questions.map((question, index) => {
                                // Debug: log the question structure
                                console.log(`Question ${index + 1}:`, question)

                                // Try multiple possible field names for the question text
                                const questionText = question.question ||
                                    question.question_text ||
                                    question.text ||
                                    question.prompt ||
                                    `Question ${index + 1} (text not found)`

                                return (
                                    <div key={index} className="border rounded-lg p-4">
                                        <div className="flex items-start gap-3">
                                            <span className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-medium">
                                                {index + 1}
                                            </span>
                                            <div className="flex-1 space-y-3">
                                                <p className="font-medium">{questionText}</p>

                                                {question.options && (
                                                    <div className="space-y-2">
                                                        <p className="text-sm font-medium text-muted-foreground">Options:</p>
                                                        {question.options.map((option, optIndex) => (
                                                            <div key={optIndex} className="flex items-center gap-2">
                                                                <div className="w-4 h-4 border rounded-full flex-shrink-0" />
                                                                <span className={
                                                                    option === question.correct_answer
                                                                        ? "text-green-600 font-medium"
                                                                        : ""
                                                                }>
                                                                    {option}
                                                                </span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}

                                                {question.correct_answer && (
                                                    <div className="text-sm">
                                                        <span className="font-medium text-green-600">Correct Answer: </span>
                                                        <span className="text-green-600">{question.correct_answer}</span>
                                                    </div>
                                                )}

                                                {question.explanation && (
                                                    <div className="text-sm text-muted-foreground bg-muted p-3 rounded">
                                                        <strong>Explanation:</strong> {question.explanation}
                                                    </div>
                                                )}

                                                {/* Debug info - remove in production */}
                                                <details className="text-xs text-muted-foreground">
                                                    <summary>Debug Info</summary>
                                                    <pre>{JSON.stringify(question, null, 2)}</pre>
                                                </details>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>

                        <div className="flex gap-3 mt-6">
                            <Button onClick={handleSaveAssessment} className="flex-1">
                                <Save className="w-4 h-4 mr-2" />
                                Save Assessment
                            </Button>
                            <Button variant="outline" onClick={() => setShowPreview(false)}>
                                Edit Configuration
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link href="/dashboard/assessments">
                    <Button variant="ghost" size="sm">
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Assessments
                    </Button>
                </Link>
                <div>
                    <h1 className="text-2xl font-bold">Create Assessment</h1>
                    <p className="text-muted-foreground">
                        Configure your assessment parameters and let AI generate the questions
                    </p>
                </div>
            </div>

            {/* Configuration Form */}
            <Card>
                <CardHeader>
                    <CardTitle>Assessment Configuration</CardTitle>
                    <CardDescription>
                        Set up the basic parameters for your assessment. AI will generate questions based on these settings.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Basic Information */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Assessment Name *</Label>
                            <Input
                                id="name"
                                value={formData.name}
                                onChange={(e) => handleInputChange('name', e.target.value)}
                                placeholder="e.g., Grade 5 Math Quiz"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="subject">Subject *</Label>
                            <Select
                                value={formData.subject}
                                onValueChange={(value) => handleInputChange('subject', value)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a subject" />
                                </SelectTrigger>
                                <SelectContent>
                                    {subjects.map((subject) => (
                                        <SelectItem key={subject} value={subject}>
                                            {subject}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="grade">Target Grade *</Label>
                            <Select
                                value={formData.target_grade.toString()}
                                onValueChange={(value) => handleInputChange('target_grade', parseInt(value))}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {grades.map((grade) => (
                                        <SelectItem key={grade} value={grade.toString()}>
                                            Grade {grade}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="difficulty">Difficulty Level</Label>
                            <Select
                                value={formData.difficulty_level}
                                onValueChange={(value: 'easy' | 'medium' | 'hard') => handleInputChange('difficulty_level', value)}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="easy">Easy</SelectItem>
                                    <SelectItem value="medium">Medium</SelectItem>
                                    <SelectItem value="hard">Hard</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label>Language</Label>
                            <LanguageSelector variant="button" className="w-full justify-start" />
                            <p className="text-xs text-gray-500">AI will generate questions in the selected language</p>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="question_count">Number of Questions</Label>
                            <Input
                                id="question_count"
                                type="number"
                                value={formData.question_count}
                                onChange={(e) => handleInputChange('question_count', parseInt(e.target.value) || 10)}
                                min="5"
                                max="50"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="topic">Topic/Chapter *</Label>
                            <Input
                                id="topic"
                                value={formData.topic}
                                onChange={(e) => handleInputChange('topic', e.target.value)}
                                placeholder="e.g., Fractions and Decimals"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="time_limit">Time Limit (minutes)</Label>
                            <Input
                                id="time_limit"
                                type="number"
                                value={formData.time_limit_minutes}
                                onChange={(e) => handleInputChange('time_limit_minutes', parseInt(e.target.value) || 30)}
                                min="10"
                                max="180"
                            />
                        </div>
                    </div>

                    {/* Auto-generation Option */}
                    <div className="flex items-center space-x-2 pt-2">
                        <input
                            type="checkbox"
                            id="auto_generate"
                            checked={autoGenerate}
                            onChange={(e) => setAutoGenerate(e.target.checked)}
                            className="rounded border-gray-300"
                        />
                        <Label htmlFor="auto_generate" className="text-sm">
                            Automatically generate questions after creating configuration
                        </Label>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3 pt-4">
                        {!configId ? (
                            <Button
                                onClick={handleCreateConfig}
                                disabled={isCreating}
                                className="flex-1"
                            >
                                {isCreating ? "Creating..." : "Create Configuration"}
                            </Button>
                        ) : (
                            <>
                                <Button
                                    onClick={handleGenerateAssessment}
                                    disabled={isGenerating}
                                    className="flex-1"
                                >
                                    <Wand2 className="w-4 h-4 mr-2" />
                                    {isGenerating ? "Generating Questions..." : "Generate AI Questions"}
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => setConfigId(null)}
                                >
                                    Edit Configuration
                                </Button>
                            </>
                        )}
                    </div>

                    {configId && (
                        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                            <p className="text-sm text-green-700 dark:text-green-300">
                                ✓ Configuration created successfully (ID: {configId}).
                                {autoGenerate ? ' Questions are being generated automatically...' : ' Click "Generate AI Questions" to create your assessment.'}
                            </p>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
