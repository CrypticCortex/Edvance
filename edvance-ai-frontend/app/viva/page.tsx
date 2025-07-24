"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Video,
  Mic,
  MicOff,
  VideoOff,
  Phone,
  Users,
  MessageSquare,
  Settings,
  Calendar,
  Upload,
  Eye,
  FileText,
  LayoutDashboard,
  Play,
} from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"

const sidebarItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard" },
  { icon: Video, label: "Viva Viva", href: "/viva", active: true },
  { icon: Upload, label: "Upload Materials", href: "/upload" },
  { icon: Eye, label: "Visual Content", href: "/visual" },
  { icon: FileText, label: "Reports", href: "/reports" },
  { icon: Calendar, label: "Calendar", href: "/calendar" },
  { icon: Settings, label: "Settings", href: "/settings" },
]

const participants = [
  { name: "Kalyan", role: "Teacher", avatar: "K", active: true },
  { name: "Sanjana", role: "Student", avatar: "S", active: true },
  { name: "Ashutosh", role: "Student", avatar: "A", active: true },
  { name: "Sangeetha", role: "Student", avatar: "Sa", active: false },
]

const upcomingSessions = [
  { subject: "Mathematics", grade: "Grade 3", time: "10:00 AM", students: 15 },
  { subject: "Science", grade: "Grade 4", time: "11:30 AM", students: 12 },
  { subject: "English", grade: "Grade 5", time: "2:00 PM", students: 18 },
]

export default function VivaPage() {
  const [isVideoOn, setIsVideoOn] = useState(true)
  const [isAudioOn, setIsAudioOn] = useState(true)
  const [isInSession, setIsInSession] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <motion.div
        className="w-64 bg-white border-r border-gray-200 flex flex-col"
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">E</span>
            </div>
            <span className="text-xl font-bold text-gray-900">Edvance</span>
          </Link>
        </div>

        <div className="flex-1 p-4">
          <div className="mb-6">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">NAVIGATION</p>
            <nav className="space-y-1">
              {sidebarItems.map((item, index) => (
                <motion.div
                  key={item.label}
                  initial={{ x: -50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <Link href={item.href}>
                    <div
                      className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                        item.active
                          ? "bg-blue-50 text-blue-700 border-r-2 border-blue-700"
                          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                      }`}
                    >
                      <item.icon className="w-5 h-5" />
                      <span className="text-sm font-medium">{item.label}</span>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </nav>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <motion.header
          className="bg-white border-b border-gray-200 px-6 py-4"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Viva Viva</h1>
              <p className="text-gray-600 mt-1">Interactive live sessions and video calls</p>
            </div>
            <div className="flex items-center space-x-3">
              <Badge variant={isInSession ? "default" : "secondary"} className="px-3 py-1">
                {isInSession ? "Live Session" : "Ready to Start"}
              </Badge>
            </div>
          </div>
        </motion.header>

        <div className="flex-1 p-6">
          {!isInSession ? (
            // Pre-session view
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Quick Start */}
              <motion.div
                className="lg:col-span-2 space-y-6"
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <Card className="border-0 shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Video className="w-5 h-5 mr-2 text-blue-600" />
                      Start New Session
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gray-900 rounded-lg aspect-video flex items-center justify-center mb-6">
                      <div className="text-center text-white">
                        <Video className="w-16 h-16 mx-auto mb-4 opacity-50" />
                        <p className="text-lg font-medium mb-2">Camera Preview</p>
                        <p className="text-sm opacity-75">Your video will appear here</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-center space-x-4 mb-6">
                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <Button
                          variant={isVideoOn ? "default" : "outline"}
                          size="lg"
                          onClick={() => setIsVideoOn(!isVideoOn)}
                          className="w-12 h-12 rounded-full p-0"
                        >
                          {isVideoOn ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
                        </Button>
                      </motion.div>

                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <Button
                          variant={isAudioOn ? "default" : "outline"}
                          size="lg"
                          onClick={() => setIsAudioOn(!isAudioOn)}
                          className="w-12 h-12 rounded-full p-0"
                        >
                          {isAudioOn ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
                        </Button>
                      </motion.div>
                    </div>

                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                      <Button
                        className="w-full bg-green-600 hover:bg-green-700 text-lg py-3"
                        onClick={() => setIsInSession(true)}
                      >
                        <Play className="w-5 h-5 mr-2" />
                        Start Live Session
                      </Button>
                    </motion.div>
                  </CardContent>
                </Card>

                {/* Recent Sessions */}
                <Card className="border-0 shadow-sm">
                  <CardHeader>
                    <CardTitle>Recent Sessions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <Video className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-medium">Mathematics - Grade 3</p>
                            <p className="text-sm text-gray-500">Yesterday, 10:00 AM • 45 min</p>
                          </div>
                        </div>
                        <Badge variant="outline">Completed</Badge>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                            <Video className="w-5 h-5 text-green-600" />
                          </div>
                          <div>
                            <p className="font-medium">Science - Grade 4</p>
                            <p className="text-sm text-gray-500">2 days ago, 11:30 AM • 30 min</p>
                          </div>
                        </div>
                        <Badge variant="outline">Completed</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Upcoming Sessions */}
              <motion.div
                initial={{ x: 50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.6 }}
              >
                <Card className="border-0 shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Calendar className="w-5 h-5 mr-2 text-purple-600" />
                      Upcoming Sessions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {upcomingSessions.map((session, index) => (
                        <motion.div
                          key={index}
                          className="p-4 border border-gray-200 rounded-lg hover:shadow-sm transition-shadow"
                          initial={{ y: 20, opacity: 0 }}
                          animate={{ y: 0, opacity: 1 }}
                          transition={{ duration: 0.4, delay: 0.6 + index * 0.1 }}
                          whileHover={{ scale: 1.02 }}
                        >
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-medium text-gray-900">{session.subject}</h4>
                              <p className="text-sm text-gray-500">{session.grade}</p>
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {session.time}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-1 text-sm text-gray-500">
                              <Users className="w-4 h-4" />
                              <span>{session.students} students</span>
                            </div>
                            <Button size="sm" variant="outline">
                              Join
                            </Button>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          ) : (
            // In-session view
            <motion.div
              className="grid lg:grid-cols-4 gap-6 h-full"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6 }}
            >
              {/* Main Video Area */}
              <div className="lg:col-span-3 space-y-4">
                <Card className="border-0 shadow-sm h-full">
                  <CardContent className="p-4 h-full">
                    <div className="bg-gray-900 rounded-lg h-full flex items-center justify-center relative">
                      <div className="text-center text-white">
                        <Video className="w-20 h-20 mx-auto mb-4 opacity-50" />
                        <p className="text-xl font-medium mb-2">Live Session Active</p>
                        <p className="text-sm opacity-75">Mathematics - Grade 3</p>
                      </div>

                      {/* Session Controls */}
                      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                        <div className="flex items-center space-x-3 bg-black/50 rounded-full px-4 py-2">
                          <Button
                            variant={isAudioOn ? "default" : "destructive"}
                            size="sm"
                            onClick={() => setIsAudioOn(!isAudioOn)}
                            className="w-10 h-10 rounded-full p-0"
                          >
                            {isAudioOn ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
                          </Button>

                          <Button
                            variant={isVideoOn ? "default" : "destructive"}
                            size="sm"
                            onClick={() => setIsVideoOn(!isVideoOn)}
                            className="w-10 h-10 rounded-full p-0"
                          >
                            {isVideoOn ? <Video className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
                          </Button>

                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => setIsInSession(false)}
                            className="w-10 h-10 rounded-full p-0"
                          >
                            <Phone className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Participants & Chat */}
              <div className="space-y-4">
                {/* Participants */}
                <Card className="border-0 shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center">
                      <Users className="w-5 h-5 mr-2 text-blue-600" />
                      Participants ({participants.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {participants.map((participant, index) => (
                        <motion.div
                          key={participant.name}
                          className="flex items-center space-x-3"
                          initial={{ x: 20, opacity: 0 }}
                          animate={{ x: 0, opacity: 1 }}
                          transition={{ duration: 0.4, delay: index * 0.1 }}
                        >
                          <Avatar className="w-8 h-8">
                            <AvatarFallback className="bg-blue-100 text-blue-700 text-xs">
                              {participant.avatar}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">{participant.name}</p>
                            <p className="text-xs text-gray-500">{participant.role}</p>
                          </div>
                          <div
                            className={`w-2 h-2 rounded-full ${participant.active ? "bg-green-500" : "bg-gray-300"}`}
                          />
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Chat */}
                <Card className="border-0 shadow-sm flex-1">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center">
                      <MessageSquare className="w-5 h-5 mr-2 text-green-600" />
                      Chat
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 mb-4">
                      <div className="text-sm">
                        <span className="font-medium text-blue-600">Kalyan:</span>
                        <span className="ml-2 text-gray-700">Welcome everyone to today's math session!</span>
                      </div>
                      <div className="text-sm">
                        <span className="font-medium text-purple-600">Sanjana:</span>
                        <span className="ml-2 text-gray-700">Thank you sir, ready to learn!</span>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        placeholder="Type a message..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <Button size="sm" className="px-3">
                        Send
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
