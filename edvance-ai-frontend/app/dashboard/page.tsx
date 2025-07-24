"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  LayoutDashboard,
  Video,
  Upload,
  Eye,
  FileText,
  Calendar,
  Settings,
  Users,
  TrendingUp,
  BookOpen,
  Award,
  Bell,
  Search,
} from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"
import { apiFetch } from "@/lib/api"
import { getAuth, signOut } from "firebase/auth"

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  // Logout handler
  const handleLogout = async () => {
    try {
      const auth = getAuth()
      await signOut(auth)
    } catch {}
    localStorage.removeItem("idToken")
    window.location.href = "/auth/login"
  }

  useEffect(() => {
    // Redirect to login if not authenticated
    if (typeof window !== "undefined" && !localStorage.getItem("idToken")) {
      window.location.href = "/auth/login"
      return
    }
    setMounted(true)
    const fetchUser = async () => {
      setLoading(true)
      setError("")
      try {
        const res = await apiFetch("/v1/auth/me")
        if (!res.ok) throw new Error("Failed to fetch user profile")
        const data = await res.json()
        setUser(data)
      } catch (err: any) {
        setError(err.message || "Failed to load user profile")
      } finally {
        setLoading(false)
      }
    }
    fetchUser()
  }, [])

  if (!mounted || loading) return <div className="min-h-screen flex items-center justify-center text-lg">Loading...</div>
  if (error) return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <div className="text-red-600 text-lg font-semibold border border-red-300 bg-red-50 rounded p-4 mb-4">
        {error === "Failed to fetch user profile"
          ? "Your session has expired or you are not authorized. Please log in again."
          : error}
      </div>
      <Button variant="outline" onClick={handleLogout}>Go to Login</Button>
    </div>
  )
  if (!user) return null

  // Determine role (default to student if not present)
  const role = user.role || "student"
  const displayName = (user.first_name || "") + (user.last_name ? ` ${user.last_name}` : "");
  const finalDisplayName = displayName.trim() || user.email;

  // Sidebar items by role
  const teacherSidebar = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard", active: true },
    { icon: Upload, label: "Upload Materials", href: "/upload" },
    { icon: FileText, label: "Reports", href: "/reports" },
    { icon: Users, label: "Students", href: "/students" },
    { icon: TrendingUp, label: "Assessments", href: "/assessments" },
    { icon: BookOpen, label: "Learning Paths", href: "/learning-paths" },
    { icon: Settings, label: "Settings", href: "/settings" },
  ]
  const studentSidebar = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard", active: true },
    { icon: BookOpen, label: "Learning Paths", href: "/learning-paths" },
    { icon: TrendingUp, label: "Available Tests", href: "/tests" },
    { icon: Award, label: "Achievements", href: "/achievements" },
    { icon: Settings, label: "Settings", href: "/settings" },
  ]
  const sidebarItems = role === "teacher" ? teacherSidebar : studentSidebar

  // Welcome message
  const welcomeMsg = role === "teacher"
    ? `Welcome back, ${finalDisplayName || "Teacher"}! 👋`
    : `Welcome back, ${finalDisplayName || "Student"}! 👋`

  // Main dashboard content by role (placeholder for now)
  // You can expand these with real API calls for each section as needed
  const teacherContent = (
    <>
      {/* Example: Document upload, reports, assessments, students, learning paths */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-1">{welcomeMsg}</h2>
        <p className="text-gray-600">Here's what's happening with your EdVance platform today.</p>
      </div>
      {/* Add teacher-specific dashboard sections here */}
    </>
  )
  const studentContent = (
    <>
      {/* Example: Learning paths, available tests, lessons, insights */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-1">{welcomeMsg}</h2>
        <p className="text-gray-600">Check your learning progress and upcoming assessments.</p>
      </div>
      {/* Add student-specific dashboard sections here */}
    </>
  )

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <motion.div
        className="w-64 bg-white border-r border-gray-200 flex flex-col"
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">E</span>
            </div>
            <span className="text-xl font-bold text-gray-900">Edvance</span>
          </div>
        </div>
        {/* Navigation */}
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
        {/* User Profile */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <Avatar>
              <AvatarFallback className="bg-blue-100 text-blue-700">
                {finalDisplayName ? finalDisplayName[0].toUpperCase() : "U"}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{finalDisplayName}</p>
              <p className="text-xs text-gray-500">{role.charAt(0).toUpperCase() + role.slice(1)}</p>
            </div>
          </div>
        </div>
      </motion.div>
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <motion.header
          className="bg-white border-b border-gray-200 px-6 py-4"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm">
                <Search className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Bell className="w-4 h-4" />
              </Button>
              <div className="text-sm text-gray-600">Hi, {finalDisplayName}!</div>
              <Button variant="outline" size="sm" onClick={handleLogout} className="ml-2">Logout</Button>
            </div>
          </div>
        </motion.header>
        {/* Dashboard Content */}
        <div className="flex-1 p-6 space-y-6">
          {role === "teacher" ? teacherContent : studentContent}
        </div>
      </div>
    </div>
  )
}
