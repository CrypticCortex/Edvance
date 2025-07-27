"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { LanguageSelector } from "@/components/ui/language-selector"
import {
    Brain,
    Send,
    User,
    Bot,
    BookOpen,
    Lightbulb,
    MessageSquare,
    HelpCircle,
    Sparkles,
    Clock,
    RefreshCw,
    Copy,
    ThumbsUp,
    ThumbsDown
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useLanguage } from "@/contexts/LanguageContext"
import { apiService, handleApiError } from "@/lib/api"

interface Message {
    id: string
    type: 'user' | 'ai'
    content: string
    timestamp: Date
    isLoading?: boolean
}

interface SuggestedTopic {
    title: string
    description: string
    icon: any
    prompt: string
}

const suggestedTopics: SuggestedTopic[] = [
    {
        title: "Teaching Strategies",
        description: "Get advice on effective teaching methods and classroom management",
        icon: BookOpen,
        prompt: "Can you suggest some effective teaching strategies for engaging students in the classroom?"
    },
    {
        title: "Assessment Techniques",
        description: "Learn about different assessment methods and evaluation techniques",
        icon: HelpCircle,
        prompt: "What are some innovative assessment techniques I can use to evaluate student understanding?"
    },
    {
        title: "Curriculum Planning",
        description: "Get help with lesson planning and curriculum development",
        icon: Lightbulb,
        prompt: "How can I create an effective curriculum plan for my subject area?"
    },
    {
        title: "Student Support",
        description: "Learn how to support struggling students and identify learning gaps",
        icon: User,
        prompt: "What are some strategies to help struggling students catch up with the class?"
    }
]

export default function AIAgentPage() {
    const [messages, setMessages] = useState<Message[]>([])
    const [inputMessage, setInputMessage] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const { toast } = useToast()
    const { currentLanguage } = useLanguage()

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    useEffect(() => {
        // Add welcome message
        const welcomeMessage: Message = {
            id: 'welcome',
            type: 'ai',
            content: "Hello! I'm your AI teaching assistant. I'm here to help you with any questions about teaching, curriculum planning, student assessment, classroom management, or any educational topic. How can I assist you today?",
            timestamp: new Date()
        }
        setMessages([welcomeMessage])
    }, [])

    const sendMessage = async (messageContent: string) => {
        if (!messageContent.trim()) return

        const userMessage: Message = {
            id: `user_${Date.now()}`,
            type: 'user',
            content: messageContent,
            timestamp: new Date()
        }

        const loadingMessage: Message = {
            id: `ai_${Date.now()}`,
            type: 'ai',
            content: "I'm thinking about your question...",
            timestamp: new Date(),
            isLoading: true
        }

        setMessages(prev => [...prev, userMessage, loadingMessage])
        setInputMessage("")
        setIsLoading(true)

        try {
            // Call the real AI agent API with current language
            const response = await apiService.invokeAgent(messageContent, currentLanguage)

            const aiMessage: Message = {
                id: `ai_${Date.now()}_response`,
                type: 'ai',
                content: response.response || "I'm sorry, I couldn't generate a response. Please try again.",
                timestamp: new Date()
            }

            setMessages(prev => prev.slice(0, -1).concat([aiMessage]))
        } catch (error: any) {
            console.error('Error sending message:', error)

            // Show more detailed error information
            let errorMessage = "I'm having trouble processing your request right now."

            if (error.message?.includes('422')) {
                errorMessage = "There was an issue with your request format. Please try rephrasing your question."
            } else if (error.message?.includes('401')) {
                errorMessage = "You need to be logged in to use the AI agent. Please log in and try again."
            } else if (error.message?.includes('500')) {
                errorMessage = "The AI service is temporarily unavailable. Please try again in a moment."
            }

            // Fallback to mock response if API fails
            const fallbackResponse = generateMockResponse(messageContent)

            const aiMessage: Message = {
                id: `ai_${Date.now()}_fallback`,
                type: 'ai',
                content: fallbackResponse,
                timestamp: new Date()
            }

            setMessages(prev => prev.slice(0, -1).concat([aiMessage]))

            toast({
                title: "Using Offline Mode",
                description: "Connected to backup AI system while main service is unavailable.",
                variant: "destructive"
            })
        } finally {
            setIsLoading(false)
        }
    }

    const generateMockResponse = (userMessage: string): string => {
        const message = userMessage.toLowerCase()

        if (message.includes('teaching') || message.includes('strategy')) {
            return `Great question about teaching strategies! Here are some effective approaches:

**Active Learning Techniques:**
• Use think-pair-share activities to encourage student participation
• Implement hands-on experiments and interactive demonstrations
• Create group projects that promote collaboration

**Engagement Strategies:**
• Start lessons with thought-provoking questions
• Use real-world examples to make content relevant
• Incorporate multimedia and visual aids

**Assessment Integration:**
• Use formative assessments to check understanding throughout the lesson
• Provide immediate feedback to students
• Create opportunities for peer assessment

Would you like me to elaborate on any of these strategies or discuss specific subject areas?`
        }

        if (message.includes('assessment') || message.includes('evaluation')) {
            return `Assessment is crucial for understanding student progress. Here are some innovative techniques:

**Formative Assessment:**
• Exit tickets to gauge daily understanding
• One-minute papers for quick reflection
• Digital polling tools for real-time feedback

**Authentic Assessment:**
• Portfolio-based assessments
• Performance tasks that mirror real-world applications
• Student-led presentations and demonstrations

**Technology-Enhanced Assessment:**
• Online quizzes with immediate feedback
• Digital storytelling projects
• Collaborative online documents

**Alternative Assessment Methods:**
• Peer assessment activities
• Self-reflection journals
• Project-based evaluations

These methods can provide a more comprehensive view of student learning. Which type of assessment are you most interested in implementing?`
        }

        if (message.includes('curriculum') || message.includes('lesson plan')) {
            return `Effective curriculum planning is essential for student success. Here's a structured approach:

**Curriculum Design Steps:**
1. **Learning Objectives:** Define clear, measurable goals
2. **Content Mapping:** Organize topics in logical sequence
3. **Assessment Alignment:** Ensure assessments match objectives
4. **Resource Planning:** Identify materials and tools needed

**Lesson Planning Framework:**
• **Opening:** Hook students with engaging starter activity
• **Introduction:** Present learning objectives clearly
• **Development:** Build knowledge through varied activities
• **Practice:** Provide guided and independent practice
• **Closure:** Summarize key points and preview next lesson

**Best Practices:**
• Build in flexibility for different learning paces
• Include multiple learning modalities (visual, auditory, kinesthetic)
• Plan for differentiation to meet diverse needs
• Regular review and revision cycles

What specific subject or grade level are you planning curriculum for?`
        }

        if (message.includes('student') || message.includes('struggling') || message.includes('support')) {
            return `Supporting struggling students requires a multi-faceted approach:

**Identification Strategies:**
• Regular formative assessments to identify gaps
• Observation of student engagement and participation
• Review of assignment quality and completion rates

**Support Interventions:**
• **Differentiated Instruction:** Adjust content, process, or product based on student needs
• **Scaffolding:** Break complex tasks into smaller, manageable steps
• **Peer Tutoring:** Pair struggling students with stronger peers
• **Extra Practice:** Provide additional exercises and review sessions

**Motivation and Engagement:**
• Set achievable short-term goals
• Celebrate small victories and progress
• Connect learning to student interests
• Provide choice in learning activities when possible

**Communication:**
• Regular check-ins with students
• Collaboration with parents/guardians
• Coordination with special education teams when needed

**Technology Support:**
• Educational apps for skill practice
• Adaptive learning platforms
• Visual aids and multimedia resources

What specific challenges are your students facing? I can provide more targeted advice.`
        }

        // Default response
        return `Thank you for your question! I'm here to help with all aspects of teaching and education. 

Based on your inquiry, I can provide guidance on:
• Teaching methodologies and best practices
• Classroom management techniques
• Student assessment and evaluation
• Curriculum development and lesson planning
• Educational technology integration
• Student support and differentiation strategies

Could you provide a bit more detail about what specific aspect you'd like to explore? This will help me give you more targeted and useful advice for your teaching situation.`
    }

    const handleSuggestedTopic = (topic: SuggestedTopic) => {
        sendMessage(topic.prompt)
    }

    const copyMessage = (content: string) => {
        navigator.clipboard.writeText(content)
        toast({
            title: "Copied",
            description: "Message copied to clipboard",
        })
    }

    const formatTimestamp = (timestamp: Date) => {
        return timestamp.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-white">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                        <Brain className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold">AI Teaching Assistant</h1>
                        <p className="text-gray-600">Get instant help with teaching questions and educational guidance</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <LanguageSelector variant="compact" />
                    <div className="flex items-center space-x-2 bg-green-50 px-3 py-1 rounded-full">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium text-green-800">Online</span>
                    </div>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Suggested Topics Sidebar */}
                <div className="w-80 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto">
                    <h3 className="font-semibold mb-4 flex items-center">
                        <Sparkles className="h-4 w-4 mr-2 text-purple-600" />
                        Quick Help Topics
                    </h3>
                    <div className="space-y-3">
                        {suggestedTopics.map((topic, index) => (
                            <Card key={index} className="cursor-pointer hover:shadow-md transition-shadow">
                                <CardContent className="p-4">
                                    <div className="flex items-start space-x-3">
                                        <div className="p-2 bg-blue-100 rounded-lg">
                                            <topic.icon className="h-4 w-4 text-blue-600" />
                                        </div>
                                        <div className="flex-1">
                                            <h4 className="font-medium text-sm mb-1">{topic.title}</h4>
                                            <p className="text-xs text-gray-600 mb-2">{topic.description}</p>
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleSuggestedTopic(topic)}
                                                className="w-full text-xs"
                                            >
                                                Ask About This
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>

                {/* Chat Area */}
                <div className="flex-1 flex flex-col">
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.map((message) => (
                            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] flex items-start space-x-3 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                                    {/* Avatar */}
                                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${message.type === 'user' ? 'bg-blue-600' : 'bg-green-600'
                                        }`}>
                                        {message.type === 'user' ? (
                                            <User className="h-4 w-4 text-white" />
                                        ) : (
                                            <Bot className="h-4 w-4 text-white" />
                                        )}
                                    </div>

                                    {/* Message Bubble */}
                                    <div className={`rounded-lg p-4 ${message.type === 'user'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-white border border-gray-200'
                                        }`}>
                                        {message.isLoading ? (
                                            <div className="flex items-center space-x-2">
                                                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-gray-500"></div>
                                                <span className="text-gray-600">Thinking...</span>
                                            </div>
                                        ) : (
                                            <div>
                                                <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                                                <div className="flex items-center justify-between mt-2">
                                                    <span className={`text-xs ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                                                        {formatTimestamp(message.timestamp)}
                                                    </span>
                                                    {message.type === 'ai' && !message.isLoading && (
                                                        <div className="flex items-center space-x-1">
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => copyMessage(message.content)}
                                                                className="h-6 w-6 p-0"
                                                            >
                                                                <Copy className="h-3 w-3" />
                                                            </Button>
                                                            <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                                                                <ThumbsUp className="h-3 w-3" />
                                                            </Button>
                                                            <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                                                                <ThumbsDown className="h-3 w-3" />
                                                            </Button>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="border-t border-gray-200 p-4 bg-white">
                        <div className="flex items-end space-x-2">
                            <div className="flex-1">
                                <Textarea
                                    placeholder="Ask me anything about teaching, curriculum, assessments, or educational strategies..."
                                    value={inputMessage}
                                    onChange={(e) => setInputMessage(e.target.value)}
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault()
                                            sendMessage(inputMessage)
                                        }
                                    }}
                                    className="resize-none"
                                    rows={2}
                                    disabled={isLoading}
                                />
                            </div>
                            <Button
                                onClick={() => sendMessage(inputMessage)}
                                disabled={!inputMessage.trim() || isLoading}
                                size="lg"
                            >
                                <Send className="h-4 w-4" />
                            </Button>
                        </div>
                        <div className="flex items-center justify-between mt-2">
                            <div className="text-xs text-gray-500">
                                Press Enter to send, Shift+Enter for new line
                            </div>
                            <div className="text-xs text-gray-500">
                                Powered by AI • Always verify important information
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
