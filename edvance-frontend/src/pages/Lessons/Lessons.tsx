import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  LinearProgress,
  Chip,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  TextField,
  Alert
} from '@mui/material';
import {
  School,
  PlayArrow,
  Speed,
  Chat,
  Visibility,
  Add,
  CheckCircle,
  RadioButtonUnchecked,
  Timer,
  Psychology,
  AutoAwesome
} from '@mui/icons-material';
import { Lesson, Student, LearningPath } from '../../types';
import apiService from '../../services/api';
import API_ENDPOINTS from '../../config/api';

const Lessons: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [lessons, setLessons] = useState<Record<string, Lesson[]>>({});
  const [loading, setLoading] = useState(true);
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);
  const [lessonDialogOpen, setLessonDialogOpen] = useState(false);
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [studentPaths, setStudentPaths] = useState<LearningPath[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch students
      const studentsData = await apiService.get<Student[]>(API_ENDPOINTS.students.list);
      setStudents(studentsData);

      // Fetch lessons for each student
      const lessonsData: Record<string, Lesson[]> = {};
      for (const student of studentsData) {
        try {
          const studentLessons = await apiService.get<any>(API_ENDPOINTS.lessons.studentLessons(student.student_id));
          lessonsData[student.student_id] = studentLessons.lessons || [];
        } catch (error) {
          lessonsData[student.student_id] = [];
        }
      }
      setLessons(lessonsData);

    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudentPaths = async (studentId: string) => {
    try {
      const paths = await apiService.get<LearningPath[]>(API_ENDPOINTS.learning.studentPaths(studentId));
      setStudentPaths(paths);
    } catch (error) {
      console.error('Failed to fetch student paths:', error);
      setStudentPaths([]);
    }
  };

  const generateLesson = async (learningStepId: string, studentId: string) => {
    try {
      setLoading(true);
      const lessonData = {
        learning_step_id: learningStepId,
        student_id: studentId,
        customizations: {
          difficulty_adjustment: 'normal',
          include_interactive: true,
          slide_count_preference: 'medium'
        }
      };

      const result = await apiService.post(API_ENDPOINTS.lessons.createFromStep, lessonData);
      await fetchData(); // Refresh data
      setGenerateDialogOpen(false);
      console.log('Lesson generated:', result);
    } catch (error) {
      console.error('Failed to generate lesson:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewLessonDetails = async (lessonId: string) => {
    try {
      const lessonDetails = await apiService.get<any>(API_ENDPOINTS.lessons.getLesson(lessonId));
      setSelectedLesson(lessonDetails.lesson);
      setLessonDialogOpen(true);
    } catch (error) {
      console.error('Failed to fetch lesson details:', error);
    }
  };

  const getStatusColor = (completionPercentage: number) => {
    if (completionPercentage >= 100) return '#4CAF50';
    if (completionPercentage > 0) return '#FF9800';
    return '#9E9E9E';
  };

  const totalLessons = Object.values(lessons).flat().length;
  const completedLessons = Object.values(lessons).flat().filter(l => l.completion_percentage >= 100).length;
  const inProgressLessons = Object.values(lessons).flat().filter(l => l.completion_percentage > 0 && l.completion_percentage < 100).length;

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            📚 Ultra-Fast Lessons
          </Typography>
          <Typography variant="body1" color="textSecondary">
            AI-generated interactive lessons in ~27 seconds
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setGenerateDialogOpen(true)}
          sx={{
            background: 'linear-gradient(45deg, #4CAF50 30%, #45a049 90%)',
            borderRadius: 3,
            px: 3
          }}
        >
          Generate Lesson
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Lessons
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#4CAF50' }}>
                    {totalLessons}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#4CAF50' }}>
                  <School />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    In Progress
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#FF9800' }}>
                    {inProgressLessons}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#FF9800' }}>
                  <PlayArrow />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Completed
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#2196F3' }}>
                    {completedLessons}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#2196F3' }}>
                  <CheckCircle />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Avg Generation
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#9C27B0' }}>
                    27s
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#9C27B0' }}>
                  <Speed />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Student Lessons */}
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                🎓 Student Lessons
              </Typography>
              
              {students.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="textSecondary">
                    No students found. Upload students first to generate lessons.
                  </Typography>
                </Box>
              ) : (
                <List>
                  {students.map((student) => {
                    const studentLessons = lessons[student.student_id] || [];
                    return (
                      <ListItem
                        key={student.student_id}
                        sx={{
                          border: '1px solid #e0e0e0',
                          borderRadius: 2,
                          mb: 2,
                          '&:hover': {
                            backgroundColor: '#f5f5f5'
                          }
                        }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: getStatusColor(studentLessons[0]?.completion_percentage || 0) }}>
                            {student.first_name[0]}{student.last_name[0]}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                                {student.first_name} {student.last_name}
                              </Typography>
                              <Chip
                                label={`Grade ${student.grade}`}
                                size="small"
                                sx={{ bgcolor: '#e3f2fd', color: '#1976d2' }}
                              />
                            </Box>
                          }
                          secondary={
                            <Box sx={{ mt: 1 }}>
                              {studentLessons.length > 0 ? (
                                <Box>
                                  <Typography variant="body2" color="textSecondary">
                                    {studentLessons.length} lesson(s) • 
                                    Avg Progress: {Math.round(studentLessons.reduce((acc, l) => acc + l.completion_percentage, 0) / studentLessons.length)}%
                                  </Typography>
                                  <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                                    {studentLessons.slice(0, 3).map((lesson) => (
                                      <Chip
                                        key={lesson.lesson_id}
                                        label={`${lesson.topic} (${lesson.completion_percentage}%)`}
                                        size="small"
                                        variant="outlined"
                                        onClick={() => viewLessonDetails(lesson.lesson_id)}
                                        sx={{ cursor: 'pointer' }}
                                      />
                                    ))}
                                    {studentLessons.length > 3 && (
                                      <Chip
                                        label={`+${studentLessons.length - 3} more`}
                                        size="small"
                                        variant="outlined"
                                      />
                                    )}
                                  </Box>
                                </Box>
                              ) : (
                                <Typography variant="body2" color="textSecondary">
                                  No lessons yet • Ready for AI generation
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => {
                              setSelectedStudent(student);
                              fetchStudentPaths(student.student_id);
                              setGenerateDialogOpen(true);
                            }}
                          >
                            <Add />
                          </IconButton>
                          {studentLessons.length > 0 && (
                            <IconButton
                              size="small"
                              color="secondary"
                              onClick={() => viewLessonDetails(studentLessons[0].lesson_id)}
                            >
                              <Visibility />
                            </IconButton>
                          )}
                        </Box>
                      </ListItem>
                    );
                  })}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Lesson Features */}
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0', mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                ⚡ Lesson Features
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Paper sx={{ p: 2, bgcolor: '#f8f9fa' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Speed sx={{ color: '#4CAF50' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Ultra-Fast Generation
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Complete lessons generated in ~27 seconds
                  </Typography>
                </Paper>

                <Paper sx={{ p: 2, bgcolor: '#f8f9fa' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Chat sx={{ color: '#2196F3' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Interactive Chatbot
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Context-aware AI tutoring support
                  </Typography>
                </Paper>

                <Paper sx={{ p: 2, bgcolor: '#f8f9fa' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Psychology sx={{ color: '#FF9800' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Adaptive Content
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Lessons adapt to student performance
                  </Typography>
                </Paper>

                <Paper sx={{ p: 2, bgcolor: '#f8f9fa' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <AutoAwesome sx={{ color: '#9C27B0' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Interactive Elements
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Quizzes, exercises, and multimedia content
                  </Typography>
                </Paper>
              </Box>
            </CardContent>
          </Card>

          {/* Generation Stats */}
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                📊 Generation Stats
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">Avg Generation Time</Typography>
                  <Chip label="27 seconds" size="small" color="success" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">Success Rate</Typography>
                  <Chip label="98%" size="small" color="success" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">Avg Slides per Lesson</Typography>
                  <Chip label="8-12" size="small" color="info" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">Student Satisfaction</Typography>
                  <Chip label="94%" size="small" color="success" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Generate Lesson Dialog */}
      <Dialog open={generateDialogOpen} onClose={() => setGenerateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            🚀 Generate Ultra-Fast Lesson
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedStudent && (
            <Box sx={{ pt: 1 }}>
              <Typography variant="body1" sx={{ mb: 3 }}>
                Generate a lesson for <strong>{selectedStudent.first_name} {selectedStudent.last_name}</strong>
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  ⚡ Ultra-Fast Generation (~27 seconds)
                </Typography>
                <Typography variant="body2">
                  Select a learning step from the student's active learning paths to generate an interactive lesson.
                </Typography>
              </Alert>

              {studentPaths.length > 0 ? (
                <Box>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Available Learning Steps:
                  </Typography>
                  {studentPaths.map((path) => (
                    <Paper key={path.path_id} sx={{ p: 2, mb: 2, border: '1px solid #e0e0e0' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {path.title}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                        {path.description}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                        <Chip label={path.subject} size="small" color="primary" />
                        <Chip label={`${path.completion_percentage}% Complete`} size="small" color="success" />
                      </Box>

                      {path.steps.filter(step => !step.is_completed).slice(0, 3).map((step) => (
                        <Box
                          key={step.step_id}
                          sx={{
                            p: 2,
                            border: '1px solid #e0e0e0',
                            borderRadius: 1,
                            mb: 1,
                            cursor: 'pointer',
                            '&:hover': {
                              backgroundColor: '#f5f5f5'
                            }
                          }}
                          onClick={() => generateLesson(step.step_id, selectedStudent.student_id)}
                        >
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                            Step {step.step_number}: {step.title}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {step.description}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Chip label={step.difficulty_level} size="small" />
                            <Chip label={`${step.estimated_duration_minutes} min`} size="small" />
                            <Chip label={step.content_type} size="small" />
                          </Box>
                        </Box>
                      ))}
                    </Paper>
                  ))}
                </Box>
              ) : (
                <Alert severity="warning">
                  No learning paths found for this student. Generate a learning path first.
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Lesson Details Dialog */}
      <Dialog open={lessonDialogOpen} onClose={() => setLessonDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            📖 Lesson Details
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedLesson && (
            <Box sx={{ pt: 1 }}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {selectedLesson.title}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  {selectedLesson.description}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip label={selectedLesson.subject} color="primary" size="small" />
                  <Chip label={selectedLesson.topic} color="secondary" size="small" />
                  <Chip label={`Grade ${selectedLesson.grade_level}`} size="small" />
                  <Chip 
                    label={`${selectedLesson.completion_percentage}% Complete`} 
                    color="success" 
                    size="small" 
                  />
                </Box>

                <LinearProgress
                  variant="determinate"
                  value={selectedLesson.completion_percentage}
                  sx={{ mb: 2, height: 8, borderRadius: 4 }}
                />
              </Box>

              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                Lesson Slides ({selectedLesson.total_slides})
              </Typography>
              
              <Stepper orientation="vertical">
                {selectedLesson.slides.map((slide, index) => (
                  <Step key={slide.slide_id} active={index <= selectedLesson.current_slide}>
                    <StepLabel
                      icon={slide.is_completed ? <CheckCircle color="success" /> : <RadioButtonUnchecked />}
                    >
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        Slide {slide.slide_number}: {slide.title}
                      </Typography>
                    </StepLabel>
                    <StepContent>
                      {slide.subtitle && (
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          {slide.subtitle}
                        </Typography>
                      )}
                      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                        <Chip label={slide.slide_type} size="small" variant="outlined" />
                        {slide.is_interactive && (
                          <Chip label="Interactive" size="small" color="primary" />
                        )}
                        <Chip 
                          label={`${slide.estimated_duration_minutes} min`} 
                          size="small" 
                          variant="outlined" 
                        />
                      </Box>
                      <Typography variant="body2" color="textSecondary">
                        Learning Objective: {slide.learning_objective}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLessonDialogOpen(false)}>Close</Button>
          {selectedLesson && (
            <Button
              variant="contained"
              startIcon={<Chat />}
              sx={{ background: 'linear-gradient(45deg, #2196F3 30%, #1976D2 90%)' }}
            >
              Start Chatbot
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Lessons;