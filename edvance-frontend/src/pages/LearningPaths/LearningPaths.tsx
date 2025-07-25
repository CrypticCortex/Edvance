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
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  Psychology,
  AutoAwesome,
  PlayArrow,
  Visibility,
  TrendingUp,
  School,
  Assessment,
  CheckCircle,
  RadioButtonUnchecked,
  Speed
} from '@mui/icons-material';
import { LearningPath, Student } from '../../types';
import apiService from '../../services/api';
import API_ENDPOINTS from '../../config/api';

const LearningPaths: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [monitoringActive, setMonitoringActive] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [pathDialogOpen, setPathDialogOpen] = useState(false);
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false);
  const [selectedPath, setSelectedPath] = useState<LearningPath | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch students
      const studentsData = await apiService.get<Student[]>(API_ENDPOINTS.students.list);
      setStudents(studentsData);

      // Fetch learning paths for all students
      const pathPromises = studentsData.map(student =>
        apiService.get<LearningPath[]>(API_ENDPOINTS.learning.studentPaths(student.student_id))
          .catch(() => [])
      );
      
      const pathResults = await Promise.all(pathPromises);
      const allPaths = pathResults.flat();
      setLearningPaths(allPaths);

    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startMonitoring = async () => {
    try {
      setLoading(true);
      const result = await apiService.post(API_ENDPOINTS.learning.startMonitoring);
      setMonitoringActive(true);
      console.log('Monitoring started:', result);
    } catch (error) {
      console.error('Failed to start monitoring:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateLearningPath = async (studentId: string, subject: string, grade: number) => {
    try {
      const pathData = {
        student_id: studentId,
        target_subject: subject,
        target_grade: grade,
        learning_goals: [`Master ${subject} concepts`, 'Build problem-solving skills']
      };

      const result = await apiService.post(API_ENDPOINTS.learning.generatePath, pathData);
      await fetchData(); // Refresh data
      setGenerateDialogOpen(false);
      console.log('Learning path generated:', result);
    } catch (error) {
      console.error('Failed to generate learning path:', error);
    }
  };

  const viewPathDetails = async (pathId: string) => {
    try {
      const pathDetails = await apiService.get<LearningPath>(API_ENDPOINTS.learning.pathDetails(pathId));
      setSelectedPath(pathDetails);
      setPathDialogOpen(true);
    } catch (error) {
      console.error('Failed to fetch path details:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4CAF50';
      case 'in_progress': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '#4CAF50';
      case 'medium': return '#FF9800';
      case 'hard': return '#f44336';
      default: return '#9E9E9E';
    }
  };

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
            🧠 AI Learning Paths
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Automated personalized learning paths powered by AI
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AutoAwesome />}
          onClick={startMonitoring}
          disabled={monitoringActive}
          sx={{
            background: 'linear-gradient(45deg, #FF9800 30%, #F57C00 90%)',
            borderRadius: 3,
            px: 3
          }}
        >
          {monitoringActive ? 'Monitoring Active' : 'Start AI Monitoring'}
        </Button>
      </Box>

      {/* AI Monitoring Status */}
      {monitoringActive && (
        <Alert
          severity="success"
          sx={{ mb: 4, borderRadius: 3 }}
          icon={<AutoAwesome />}
        >
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
            🤖 AI Learning Path Agent is Active!
          </Typography>
          <Typography variant="body2">
            The system is automatically monitoring student assessments and generating personalized learning paths.
            New assessments will trigger automatic analysis and path creation.
          </Typography>
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Paths
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#FF9800' }}>
                    {learningPaths.length}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#FF9800' }}>
                  <Psychology />
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
                    Active Paths
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#2196F3' }}>
                    {learningPaths.filter(p => p.status === 'in_progress').length}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#2196F3' }}>
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
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#4CAF50' }}>
                    {learningPaths.filter(p => p.status === 'completed').length}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#4CAF50' }}>
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
                    Avg Progress
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#9C27B0' }}>
                    {learningPaths.length > 0 
                      ? Math.round(learningPaths.reduce((acc, p) => acc + p.completion_percentage, 0) / learningPaths.length)
                      : 0}%
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#9C27B0' }}>
                  <TrendingUp />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Students with Learning Paths */}
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                📚 Student Learning Paths
              </Typography>
              
              {students.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="textSecondary">
                    No students found. Upload students first to generate learning paths.
                  </Typography>
                </Box>
              ) : (
                <List>
                  {students.map((student) => {
                    const studentPaths = learningPaths.filter(p => p.student_id === student.student_id);
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
                          <Avatar sx={{ bgcolor: getStatusColor(studentPaths[0]?.status || 'not_started') }}>
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
                              {studentPaths.length > 0 ? (
                                <Box>
                                  <Typography variant="body2" color="textSecondary">
                                    {studentPaths.length} learning path(s) • 
                                    Avg Progress: {Math.round(studentPaths.reduce((acc, p) => acc + p.completion_percentage, 0) / studentPaths.length)}%
                                  </Typography>
                                  <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                                    {studentPaths.map((path) => (
                                      <Chip
                                        key={path.path_id}
                                        label={`${path.subject} (${path.completion_percentage}%)`}
                                        size="small"
                                        variant="outlined"
                                        onClick={() => viewPathDetails(path.path_id)}
                                        sx={{ cursor: 'pointer' }}
                                      />
                                    ))}
                                  </Box>
                                </Box>
                              ) : (
                                <Typography variant="body2" color="textSecondary">
                                  No learning paths yet • Ready for AI generation
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
                              setGenerateDialogOpen(true);
                            }}
                          >
                            <AutoAwesome />
                          </IconButton>
                          {studentPaths.length > 0 && (
                            <IconButton
                              size="small"
                              color="secondary"
                              onClick={() => viewPathDetails(studentPaths[0].path_id)}
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

        {/* AI Features */}
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0', mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                🤖 AI Features
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Paper sx={{ p: 2, bgcolor: '#f8f9fa' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Speed sx={{ color: '#FF9800' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Ultra-Fast Generation
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Learning paths generated in ~27 seconds
                  </Typography>
                </Paper>

                <Paper sx={{ p: 2, bgcolor: '#f8f9fa' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <AutoAwesome sx={{ color: '#9C27B0' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Automated Monitoring
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    95% of tasks handled automatically by AI agents
                  </Typography>
                </Paper>

                <Paper sx={{ p: 2, bgcolor: '#f8f9fa' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Psychology sx={{ color: '#4CAF50' }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Adaptive Learning
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Paths adjust to student progress automatically
                  </Typography>
                </Paper>
              </Box>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                ⚡ Quick Actions
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Create Assessment
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<School />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Generate Lesson
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  View Analytics
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Generate Learning Path Dialog */}
      <Dialog open={generateDialogOpen} onClose={() => setGenerateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            🧠 Generate Learning Path
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedStudent && (
            <Box sx={{ pt: 1 }}>
              <Typography variant="body1" sx={{ mb: 3 }}>
                Generate a personalized learning path for <strong>{selectedStudent.first_name} {selectedStudent.last_name}</strong>
              </Typography>
              
              <TextField
                select
                label="Subject"
                fullWidth
                sx={{ mb: 2 }}
                defaultValue={selectedStudent.subjects[0] || ''}
              >
                {selectedStudent.subjects.map((subject) => (
                  <MenuItem key={subject} value={subject}>
                    {subject}
                  </MenuItem>
                ))}
              </TextField>
              
              <TextField
                label="Target Grade"
                type="number"
                fullWidth
                defaultValue={selectedStudent.grade}
                sx={{ mb: 2 }}
              />
              
              <Alert severity="info" sx={{ mt: 2 }}>
                The AI will analyze the student's assessment history and generate a personalized learning path
                tailored to their specific needs and knowledge gaps.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<AutoAwesome />}
            onClick={() => {
              if (selectedStudent) {
                generateLearningPath(
                  selectedStudent.student_id,
                  selectedStudent.subjects[0] || 'Mathematics',
                  selectedStudent.grade
                );
              }
            }}
            sx={{ background: 'linear-gradient(45deg, #FF9800 30%, #F57C00 90%)' }}
          >
            Generate Path
          </Button>
        </DialogActions>
      </Dialog>

      {/* Path Details Dialog */}
      <Dialog open={pathDialogOpen} onClose={() => setPathDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            📚 Learning Path Details
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedPath && (
            <Box sx={{ pt: 1 }}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {selectedPath.title}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  {selectedPath.description}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip label={selectedPath.subject} color="primary" size="small" />
                  <Chip label={`Grade ${selectedPath.target_grade}`} color="secondary" size="small" />
                  <Chip 
                    label={`${selectedPath.completion_percentage}% Complete`} 
                    color="success" 
                    size="small" 
                  />
                </Box>

                <LinearProgress
                  variant="determinate"
                  value={selectedPath.completion_percentage}
                  sx={{ mb: 2, height: 8, borderRadius: 4 }}
                />
              </Box>

              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                Learning Steps ({selectedPath.steps.length})
              </Typography>
              
              <Stepper orientation="vertical">
                {selectedPath.steps.map((step, index) => (
                  <Step key={step.step_id} active={index <= selectedPath.current_step}>
                    <StepLabel
                      icon={step.is_completed ? <CheckCircle color="success" /> : <RadioButtonUnchecked />}
                    >
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        {step.title}
                      </Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                        {step.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                        <Chip
                          label={step.difficulty_level}
                          size="small"
                          sx={{
                            bgcolor: getDifficultyColor(step.difficulty_level),
                            color: 'white'
                          }}
                        />
                        <Chip label={step.content_type} size="small" variant="outlined" />
                        <Chip label={`${step.estimated_duration_minutes} min`} size="small" variant="outlined" />
                      </Box>
                      {step.performance_score && (
                        <Typography variant="body2" color="success.main">
                          Score: {step.performance_score}%
                        </Typography>
                      )}
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPathDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LearningPaths;