"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp } from "lucide-react"

export function OverviewChart() {
  // Mock data for the chart
  const data = [
    { name: "Mon", assessments: 12, lessons: 8, paths: 3 },
    { name: "Tue", assessments: 19, lessons: 12, paths: 5 },
    { name: "Wed", assessments: 15, lessons: 10, paths: 4 },
    { name: "Thu", assessments: 22, lessons: 15, paths: 6 },
    { name: "Fri", assessments: 18, lessons: 11, paths: 4 },
    { name: "Sat", assessments: 8, lessons: 5, paths: 2 },
    { name: "Sun", assessments: 6, lessons: 3, paths: 1 },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <TrendingUp className="h-5 w-5" />
          <span>Weekly Activity Overview</span>
        </CardTitle>
        <CardDescription>Student engagement and AI-generated content</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((day, index) => (
            <div key={day.name} className="flex items-center space-x-4">
              <div className="w-12 text-sm font-medium">{day.name}</div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-20 text-xs text-gray-600">Assessments</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(day.assessments / 25) * 100}%` }}
                    ></div>
                  </div>
                  <div className="w-8 text-xs text-right">{day.assessments}</div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 text-xs text-gray-600">Lessons</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${(day.lessons / 20) * 100}%` }}
                    ></div>
                  </div>
                  <div className="w-8 text-xs text-right">{day.lessons}</div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 text-xs text-gray-600">Paths</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full"
                      style={{ width: `${(day.paths / 10) * 100}%` }}
                    ></div>
                  </div>
                  <div className="w-8 text-xs text-right">{day.paths}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
