import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider
} from '@mui/material';
import {
  People,
  School,
  Assessment,
  TrendingUp,
  AutoAwesome,
  PlayArrow,
  Add,
  Psychology,
  Speed,
  CloudUpload
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';
import API_ENDPOINTS from '../../config/api';

interface DashboardStats {
  totalStudents: number;
  activeLearningPaths: number;
  completedLessons: number;
  averageProgress: number;
}

interface RecentActivity {
  id: string;
  type: 'lesson_completed' | 'assessment_taken' | 'path_generated';
  student_name: string;
  description: string;
  timestamp: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalStudents: 0,
    activeLearningPaths: 0,
    completedLessons: 0,
    averageProgress: 0
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch student stats
      const studentStats = await apiService.get(API_ENDPOINTS.students.stats);
      
      // Fetch teacher analytics
      const analytics = await apiService.get(API_ENDPOINTS.learning.teacherAnalytics);
      
      setStats({
        totalStudents: studentStats.total_students || 0,
        activeLearningPaths: analytics.total_active_paths || 0,
        completedLessons: analytics.learning_path_effectiveness?.paths_completed || 0,
        averageProgress: analytics.average_completion_rate || 0
      });

      // Mock recent activity for now
      setRecentActivity([
        {
          id: '1',
          type: 'lesson_completed',
          student_name: 'Alice Johnson',
          description: 'Completed "Introduction to Algebra" lesson',
          timestamp: '2 hours ago'
        },
        {
          id: '2',
          type: 'path_generated',
          student_name: 'Bob Smith',
          description: 'AI generated personalized learning path for Mathematics',
          timestamp: '4 hours ago'
        },
        {
          id: '3',
          type: 'assessment_taken',
          student_name: 'Carol Davis',
          description: 'Completed Grade 5 Mathematics assessment (Score: 85%)',
          timestamp: '6 hours ago'
        }
      ]);

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Upload Students',
      description: 'Add students via CSV upload',
      icon: <People />,
      color: '#4CAF50',
      action: () => navigate('/students'),
      badge: 'Quick'
    },
    {
      title: 'Start AI Monitoring',
      description: 'Activate automated learning paths',
      icon: <Psychology />,
      color: '#FF9800',
      action: () => navigate('/learning-paths'),
      badge: 'AI'
    },
    {
      title: 'Upload Documents',
      description: 'Add educational materials',
      icon: <CloudUpload />,
      color: '#2196F3',
      action: () => navigate('/documents'),
      badge: 'RAG'
    },
    {
      title: 'Create Assessment',
      description: 'Generate AI-powered assessments',
      icon: <Assessment />,
      color: '#9C27B0',
      action: () => navigate('/assessments'),
      badge: 'Smart'
    }
  ];

  const statCards = [
    {
      title: 'Total Students',
      value: stats.totalStudents,
      icon: <People />,
      color: '#4CAF50',
      change: '+12%'
    },
    {
      title: 'Active Learning Paths',
      value: stats.activeLearningPaths,
      icon: <Psychology />,
      color: '#FF9800',
      change: '+25%'
    },
    {
      title: 'Lessons Generated',
      value: stats.completedLessons,
      icon: <School />,
      color: '#2196F3',
      change: '+18%'
    },
    {
      title: 'Average Progress',
      value: `${stats.averageProgress}%`,
      icon: <TrendingUp />,
      color: '#9C27B0',
      change: '+8%'
    }
  ];

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Welcome Section */}
      <Paper
        sx={{
          p: 4,
          mb: 4,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: 3
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
              Welcome back, {user?.first_name || 'Teacher'}! 👋
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
              Your AI-powered teaching assistant is ready to help
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                icon={<AutoAwesome />}
                label="AI Monitoring Active"
                sx={{ bgcolor: '#4CAF50', color: 'white' }}
              />
              <Chip
                icon={<Speed />}
                label="Ultra-Fast Generation"
                sx={{ bgcolor: '#FF9800', color: 'white' }}
              />
            </Box>
          </Box>
          <AutoAwesome sx={{ fontSize: 80, opacity: 0.3 }} />
        </Box>
      </Paper>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                border: '1px solid #e0e0e0',
                borderRadius: 3,
                transition: 'transform 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: stat.color }}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                      {stat.change} this week
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: stat.color, width: 56, height: 56 }}>
                    {stat.icon}
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                🚀 Quick Actions
              </Typography>
              <Grid container spacing={2}>
                {quickActions.map((action, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Card
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        border: '2px solid transparent',
                        borderRadius: 2,
                        transition: 'all 0.2s ease-in-out',
                        '&:hover': {
                          borderColor: action.color,
                          transform: 'translateY(-2px)',
                          boxShadow: `0 4px 20px ${action.color}20`
                        }
                      }}
                      onClick={action.action}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: action.color }}>
                          {action.icon}
                        </Avatar>
                        <Box sx={{ flexGrow: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                              {action.title}
                            </Typography>
                            <Chip
                              label={action.badge}
                              size="small"
                              sx={{
                                bgcolor: action.color,
                                color: 'white',
                                fontSize: '0.7rem',
                                height: 20
                              }}
                            />
                          </Box>
                          <Typography variant="body2" color="textSecondary">
                            {action.description}
                          </Typography>
                        </Box>
                        <PlayArrow sx={{ color: action.color }} />
                      </Box>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                📈 Recent Activity
              </Typography>
              <List>
                {recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            bgcolor: activity.type === 'lesson_completed' ? '#4CAF50' :
                                     activity.type === 'path_generated' ? '#FF9800' : '#2196F3',
                            width: 32,
                            height: 32
                          }}
                        >
                          {activity.type === 'lesson_completed' ? <School /> :
                           activity.type === 'path_generated' ? <Psychology /> : <Assessment />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {activity.student_name}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {activity.description}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              {activity.timestamp}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < recentActivity.length - 1 && <Divider variant="inset" component="li" />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;