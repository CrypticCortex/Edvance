"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Clock, CheckCircle, AlertCircle, Users } from "lucide-react"

export function RecentActivity() {
  const activities = [
    {
      id: 1,
      type: "assessment_completed",
      title: "Math Assessment Completed",
      description: "Sarah Johnson completed Grade 5 Math Assessment",
      time: "2 minutes ago",
      icon: CheckCircle,
      color: "text-green-600",
    },
    {
      id: 2,
      type: "learning_path_generated",
      title: "Learning Path Created",
      description: "AI generated personalized path for Michael Chen",
      time: "15 minutes ago",
      icon: Users,
      color: "text-blue-600",
    },
    {
      id: 3,
      type: "intervention_needed",
      title: "Student Needs Support",
      description: "Emma Davis struggling with multiplication concepts",
      time: "1 hour ago",
      icon: AlertCircle,
      color: "text-orange-600",
    },
    {
      id: 4,
      type: "lesson_generated",
      title: "Lesson Generated",
      description: 'AI created "Understanding Fractions" lesson in 24s',
      time: "2 hours ago",
      icon: CheckCircle,
      color: "text-green-600",
    },
    {
      id: 5,
      type: "assessment_analyzed",
      title: "Assessment Analyzed",
      description: "Performance analysis completed for 5 students",
      time: "3 hours ago",
      icon: Users,
      color: "text-purple-600",
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Clock className="h-5 w-5" />
          <span>Recent Activity</span>
        </CardTitle>
        <CardDescription>Latest updates from your classroom</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-3">
              <activity.icon className={`h-4 w-4 mt-1 ${activity.color}`} />
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium">{activity.title}</p>
                <p className="text-xs text-gray-600">{activity.description}</p>
                <p className="text-xs text-gray-400">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
