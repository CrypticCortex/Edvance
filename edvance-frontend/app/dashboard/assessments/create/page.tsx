"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Plus, Trash2, BookOpen, Users, Clock } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, handleApiError } from "@/lib/api"

interface Question {
    question_text: string
    options: string[]
    correct_answer: number
    topic: string
    difficulty: 'easy' | 'medium' | 'hard'
}

export default function CreateAssessmentPage() {
    const [loading, setLoading] = useState(false)
    const [assessment, setAssessment] = useState({
        title: "",
        subject: "",
        grade: 5,
        topics: [] as string[],
        estimated_duration_minutes: 30,
    })
    const [questions, setQuestions] = useState<Question[]>([])
    const [currentQuestion, setCurrentQuestion] = useState<Question>({
        question_text: "",
        options: ["", "", "", ""],
        correct_answer: 0,
        topic: "",
        difficulty: "medium",
    })
    const [newTopic, setNewTopic] = useState("")

    const router = useRouter()
    const { toast } = useToast()

    const subjects = [
        "Mathematics", "Science", "English", "History", "Geography",
        "Physics", "Chemistry", "Biology", "Literature", "Art"
    ]

    const addTopic = () => {
        if (newTopic && !assessment.topics.includes(newTopic)) {
            setAssessment(prev => ({
                ...prev,
                topics: [...prev.topics, newTopic]
            }))
            setNewTopic("")
        }
    }

    const removeTopic = (topic: string) => {
        setAssessment(prev => ({
            ...prev,
            topics: prev.topics.filter(t => t !== topic)
        }))
    }

    const addQuestion = () => {
        if (currentQuestion.question_text && currentQuestion.options.every(opt => opt.trim())) {
            setQuestions(prev => [...prev, { ...currentQuestion }])
            setCurrentQuestion({
                question_text: "",
                options: ["", "", "", ""],
                correct_answer: 0,
                topic: "",
                difficulty: "medium",
            })
            toast({
                title: "Question Added",
                description: "Question has been added to the assessment",
            })
        } else {
            toast({
                title: "Incomplete Question",
                description: "Please fill in all question fields",
                variant: "destructive",
            })
        }
    }

    const removeQuestion = (index: number) => {
        setQuestions(prev => prev.filter((_, i) => i !== index))
    }

    const updateQuestionOption = (index: number, value: string) => {
        setCurrentQuestion(prev => ({
            ...prev,
            options: prev.options.map((opt, i) => i === index ? value : opt)
        }))
    }

    const handleSubmit = async () => {
        if (!assessment.title || !assessment.subject || questions.length === 0) {
            toast({
                title: "Incomplete Assessment",
                description: "Please fill in all required fields and add at least one question",
                variant: "destructive",
            })
            return
        }

        setLoading(true)
        try {
            const assessmentData = {
                ...assessment,
                questions,
            }

            const result = await apiService.createAssessment(assessmentData)

            toast({
                title: "Assessment Created",
                description: `Assessment "${assessment.title}" has been created successfully`,
            })

            router.push("/dashboard/assessments")

        } catch (error: any) {
            console.error('Assessment creation error:', error)
            toast({
                title: "Creation Failed",
                description: handleApiError(error),
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center space-x-3">
                <BookOpen className="h-8 w-8 text-blue-600" />
                <div>
                    <h1 className="text-3xl font-bold">Create Assessment</h1>
                    <p className="text-gray-600">Build a comprehensive assessment for your students</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Assessment Details */}
                <div className="lg:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Assessment Information</CardTitle>
                            <CardDescription>Basic details about the assessment</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <Label htmlFor="title">Assessment Title</Label>
                                <Input
                                    id="title"
                                    value={assessment.title}
                                    onChange={(e) => setAssessment(prev => ({ ...prev, title: e.target.value }))}
                                    placeholder="e.g., Grade 5 Math Assessment"
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <Label htmlFor="subject">Subject</Label>
                                    <Select value={assessment.subject} onValueChange={(value) =>
                                        setAssessment(prev => ({ ...prev, subject: value }))
                                    }>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select subject" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {subjects.map(subject => (
                                                <SelectItem key={subject} value={subject}>{subject}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div>
                                    <Label htmlFor="grade">Grade Level</Label>
                                    <Select value={assessment.grade.toString()} onValueChange={(value) =>
                                        setAssessment(prev => ({ ...prev, grade: parseInt(value) }))
                                    }>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select grade" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(grade => (
                                                <SelectItem key={grade} value={grade.toString()}>Grade {grade}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div>
                                <Label htmlFor="duration">Estimated Duration (minutes)</Label>
                                <Input
                                    id="duration"
                                    type="number"
                                    value={assessment.estimated_duration_minutes}
                                    onChange={(e) => setAssessment(prev => ({
                                        ...prev,
                                        estimated_duration_minutes: parseInt(e.target.value) || 30
                                    }))}
                                    min="5"
                                    max="180"
                                />
                            </div>

                            <div>
                                <Label>Topics</Label>
                                <div className="flex space-x-2 mb-2">
                                    <Input
                                        value={newTopic}
                                        onChange={(e) => setNewTopic(e.target.value)}
                                        placeholder="Add a topic"
                                        onKeyPress={(e) => e.key === 'Enter' && addTopic()}
                                    />
                                    <Button onClick={addTopic} variant="outline">Add</Button>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {assessment.topics.map(topic => (
                                        <Badge key={topic} variant="secondary" className="cursor-pointer"
                                            onClick={() => removeTopic(topic)}>
                                            {topic} <Trash2 className="h-3 w-3 ml-1" />
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Add Question */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Add Question</CardTitle>
                            <CardDescription>Create multiple choice questions for the assessment</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <Label htmlFor="question">Question Text</Label>
                                <Textarea
                                    id="question"
                                    value={currentQuestion.question_text}
                                    onChange={(e) => setCurrentQuestion(prev => ({
                                        ...prev,
                                        question_text: e.target.value
                                    }))}
                                    placeholder="Enter your question here..."
                                    rows={3}
                                />
                            </div>

                            <div>
                                <Label>Answer Options</Label>
                                <div className="space-y-2">
                                    {currentQuestion.options.map((option, index) => (
                                        <div key={index} className="flex items-center space-x-2">
                                            <Input
                                                value={option}
                                                onChange={(e) => updateQuestionOption(index, e.target.value)}
                                                placeholder={`Option ${index + 1}`}
                                                className={currentQuestion.correct_answer === index ?
                                                    "border-green-500 bg-green-50" : ""}
                                            />
                                            <Button
                                                variant={currentQuestion.correct_answer === index ? "default" : "outline"}
                                                size="sm"
                                                onClick={() => setCurrentQuestion(prev => ({
                                                    ...prev,
                                                    correct_answer: index
                                                }))}
                                            >
                                                {currentQuestion.correct_answer === index ? "Correct" : "Mark Correct"}
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <Label htmlFor="questionTopic">Topic</Label>
                                    <Select value={currentQuestion.topic} onValueChange={(value) =>
                                        setCurrentQuestion(prev => ({ ...prev, topic: value }))
                                    }>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select topic" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {assessment.topics.map(topic => (
                                                <SelectItem key={topic} value={topic}>{topic}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div>
                                    <Label htmlFor="difficulty">Difficulty</Label>
                                    <Select value={currentQuestion.difficulty} onValueChange={(value: any) =>
                                        setCurrentQuestion(prev => ({ ...prev, difficulty: value }))
                                    }>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select difficulty" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="easy">Easy</SelectItem>
                                            <SelectItem value="medium">Medium</SelectItem>
                                            <SelectItem value="hard">Hard</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <Button onClick={addQuestion} className="w-full">
                                <Plus className="h-4 w-4 mr-2" />
                                Add Question
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                {/* Assessment Summary */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <Users className="h-5 w-5" />
                                <span>Assessment Summary</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex justify-between">
                                <span className="text-sm text-gray-600">Questions:</span>
                                <span className="font-medium">{questions.length}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-sm text-gray-600">Duration:</span>
                                <span className="font-medium flex items-center">
                                    <Clock className="h-4 w-4 mr-1" />
                                    {assessment.estimated_duration_minutes} min
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-sm text-gray-600">Topics:</span>
                                <span className="font-medium">{assessment.topics.length}</span>
                            </div>
                            <div className="pt-4">
                                <Button
                                    onClick={handleSubmit}
                                    className="w-full"
                                    disabled={loading || questions.length === 0}
                                >
                                    {loading ? "Creating..." : "Create Assessment"}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Questions List */}
                    {questions.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Questions ({questions.length})</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3 max-h-96 overflow-y-auto">
                                    {questions.map((question, index) => (
                                        <div key={index} className="p-3 border rounded-lg">
                                            <div className="flex justify-between items-start mb-2">
                                                <span className="text-sm font-medium">Q{index + 1}</span>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => removeQuestion(index)}
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                            <p className="text-sm text-gray-700 mb-2">{question.question_text}</p>
                                            <div className="flex justify-between text-xs text-gray-500">
                                                <span>{question.topic}</span>
                                                <span className="capitalize">{question.difficulty}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    )
}
