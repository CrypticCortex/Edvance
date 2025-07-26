"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  LayoutDashboard,
  Users,
  BookOpen,
  TrendingUp,
  Settings,
  Brain,
  Target,
  MessageSquare,
  FileText,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Students", href: "/dashboard/students", icon: Users },
  { name: "Assessments", href: "/dashboard/assessments", icon: FileText },
  { name: "Learning Paths", href: "/dashboard/learning-paths", icon: Target },
  { name: "Lessons", href: "/dashboard/lessons", icon: BookOpen },
  { name: "AI Agent", href: "/dashboard/ai-agent", icon: Brain },
  { name: "Analytics", href: "/dashboard/analytics", icon: TrendingUp },
  { name: "Chat Support", href: "/dashboard/chat", icon: MessageSquare },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <div
      className={cn(
        "bg-white border-r border-gray-200 flex flex-col transition-all duration-300",
        collapsed ? "w-16" : "w-64",
      )}
    >
      {/* Logo */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          {!collapsed && <h2 className="text-xl font-bold text-green-600">Edvance</h2>}
          <Button variant="ghost" size="sm" onClick={() => setCollapsed(!collapsed)} className="ml-auto">
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link key={item.name} href={item.href}>
              <Button
                variant={isActive ? "default" : "ghost"}
                className={cn("w-full justify-start", collapsed && "px-2")}
              >
                <item.icon className={cn("h-4 w-4", !collapsed && "mr-2")} />
                {!collapsed && item.name}
              </Button>
            </Link>
          )
        })}
      </nav>

      {/* AI Agent Status */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200">
          <div className="bg-green-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-800">AI Agent Active</span>
            </div>
            <p className="text-xs text-green-600 mt-1">Monitoring 28 students</p>
          </div>
        </div>
      )}
    </div>
  )
}
