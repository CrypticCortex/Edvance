"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { BookOpen, Users, TrendingUp, Zap, User, UserCheck } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { firebaseAuth } from "@/lib/firebase"
import { apiService, handleApiError } from "@/lib/api"

export default function LoginPage() {
  const [role, setRole] = useState<"teacher" | "student">("teacher")
  const [email, setEmail] = useState("")
  const [userId, setUserId] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const router = useRouter()
  const { toast } = useToast()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      if (role === "teacher") {
        // Teacher authentication with email and password
        const authResult = await firebaseAuth.signIn(email, password)

        if (!authResult.success || !authResult.idToken) {
          throw new Error(authResult.error || 'Authentication failed')
        }

        // Set the auth tokens for API calls
        apiService.setAuthTokens({ idToken: authResult.idToken })

        // Get user profile from backend
        const userProfile = await apiService.getProfile()

        // Store user data locally
        localStorage.setItem("teacher_token", authResult.idToken)
        localStorage.setItem("teacher_data", JSON.stringify(userProfile))

        toast({
          title: "Login Successful",
          description: `Welcome back, ${userProfile.first_name}!`,
        })

        // Redirect to dashboard
        router.push("/dashboard")

      } else {
        // Student authentication with user ID and password
        const studentAuth = await apiService.studentLogin(userId, password)

        if (!studentAuth.success) {
          throw new Error(studentAuth.error || 'Student authentication failed')
        }

        console.log('Student auth successful, storing data:', {
          token: studentAuth.token,
          user: studentAuth.user,
          session_id: studentAuth.session_id
        });

        // Store student data using the proper method
        if (studentAuth.token && studentAuth.user && studentAuth.session_id) {
          apiService.setStudentAuth({
            token: studentAuth.token,
            user: studentAuth.user,
            session_id: studentAuth.session_id
          });
        } else {
          // Fallback to manual storage if session_id is missing
          localStorage.setItem("student_token", studentAuth.token || "")
          localStorage.setItem("student_data", JSON.stringify(studentAuth.user))
        }

        // Verify data was stored
        console.log('Verification - Token stored:', localStorage.getItem("student_token"));
        console.log('Verification - Data stored:', localStorage.getItem("student_data"));
        console.log('Verification - Session ID stored:', localStorage.getItem("student_session_id"));

        toast({
          title: "Login Successful",
          description: `Welcome, ${studentAuth.user?.first_name || 'Student'}!`,
        })

        // Redirect to student dashboard
        router.push("/student-dashboard")
      }

    } catch (error: any) {
      console.error('Login error:', error)
      setError(handleApiError(error))

      toast({
        title: "Login Failed",
        description: handleApiError(error),
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center">
        {/* Left side - Branding and Features */}
        <div className="space-y-8">
          <div className="text-center lg:text-left">
            <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">Edvance</h1>
            <p className="text-xl text-gray-600 mb-8">
              AI-Powered Learning Platform for Educators and Students
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <BookOpen className="h-8 w-8 text-green-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Smart Lessons</h3>
                <p className="text-sm text-gray-600">AI-generated content</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <Users className="h-8 w-8 text-blue-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Student Tracking</h3>
                <p className="text-sm text-gray-600">Real-time progress</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <TrendingUp className="h-8 w-8 text-purple-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Analytics</h3>
                <p className="text-sm text-gray-600">Performance insights</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-4 bg-white rounded-lg shadow-sm">
              <Zap className="h-8 w-8 text-orange-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Fast Generation</h3>
                <p className="text-sm text-gray-600">27s lesson creation</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right side - Login Form */}
        <Card className="w-full max-w-md mx-auto">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Welcome Back</CardTitle>
            <CardDescription>
              Sign in to your {role} account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Role Selection */}
              <div className="space-y-2">
                <Label htmlFor="role">I am a</Label>
                <Select value={role} onValueChange={(value: "teacher" | "student") => setRole(value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="teacher">
                      <div className="flex items-center space-x-2">
                        <UserCheck className="h-4 w-4" />
                        <span>Teacher</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="student">
                      <div className="flex items-center space-x-2">
                        <User className="h-4 w-4" />
                        <span>Student</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Conditional Input Fields */}
              {role === "teacher" ? (
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="teacher@school.edu"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="userId">Student ID</Label>
                  <Input
                    id="userId"
                    type="text"
                    placeholder="Enter your student ID"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    required
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Signing in..." : `Sign In as ${role === "teacher" ? "Teacher" : "Student"}`}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{" "}
                <Link href="/auth/signup" className="text-green-600 hover:underline">
                  Sign up
                </Link>
              </p>
              {role === "student" && (
                <p className="text-xs text-gray-500 mt-2">
                  Students: Contact your teacher to get your login credentials
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
