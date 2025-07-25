import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  LinearProgress,
  Avatar,
  Tooltip,
  Fab
} from '@mui/material';
import {
  Add,
  CloudUpload,
  Edit,
  Delete,
  Visibility,
  Psychology,
  School,
  TrendingUp
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { Student, StudentBatchUploadResponse } from '../../types';
import apiService from '../../services/api';
import API_ENDPOINTS from '../../config/api';

const Students: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<StudentBatchUploadResponse | null>(null);

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      const studentsData = await apiService.get<Student[]>(API_ENDPOINTS.students.list);
      setStudents(studentsData);
    } catch (error) {
      console.error('Failed to fetch students:', error);
    } finally {
      setLoading(false);
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const result = await apiService.uploadFile<StudentBatchUploadResponse>(
        API_ENDPOINTS.students.uploadCsv,
        formData
      );

      setUploadResult(result);
      await fetchStudents(); // Refresh the list
    } catch (error) {
      console.error('Failed to upload students:', error);
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false
  });

  const handleCloseUploadDialog = () => {
    setUploadDialogOpen(false);
    setUploadResult(null);
  };

  const getGradeColor = (grade: number) => {
    if (grade <= 3) return '#4CAF50';
    if (grade <= 6) return '#FF9800';
    if (grade <= 9) return '#2196F3';
    return '#9C27B0';
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
            👥 Student Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage your students and track their learning progress
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<CloudUpload />}
          onClick={() => setUploadDialogOpen(true)}
          sx={{
            background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
            borderRadius: 3,
            px: 3
          }}
        >
          Upload Students
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
                    Total Students
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#4CAF50' }}>
                    {students.length}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#4CAF50' }}>
                  <Add />
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
                    Active Students
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#2196F3' }}>
                    {students.filter(s => s.is_active).length}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#2196F3' }}>
                  <TrendingUp />
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
                    Learning Paths
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#FF9800' }}>
                    {students.reduce((acc, s) => acc + Object.keys(s.current_learning_paths).length, 0)}
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
                    Avg Grade
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#9C27B0' }}>
                    {students.length > 0 ? Math.round(students.reduce((acc, s) => acc + s.grade, 0) / students.length) : 0}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: '#9C27B0' }}>
                  <School />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Students Table */}
      <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
            📚 Student List
          </Typography>
          
          {students.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="textSecondary" sx={{ mb: 2 }}>
                No students found
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Upload a CSV file to add students to your class
              </Typography>
              <Button
                variant="contained"
                startIcon={<CloudUpload />}
                onClick={() => setUploadDialogOpen(true)}
                sx={{ background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)' }}
              >
                Upload Students
              </Button>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Student</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Grade</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Subjects</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Learning Paths</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {students.map((student) => (
                    <TableRow key={student.student_id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{ bgcolor: getGradeColor(student.grade) }}>
                            {student.first_name[0]}{student.last_name[0]}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                              {student.first_name} {student.last_name}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              ID: {student.student_id.slice(-8)}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`Grade ${student.grade}`}
                          size="small"
                          sx={{
                            bgcolor: getGradeColor(student.grade),
                            color: 'white',
                            fontWeight: 'bold'
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {student.subjects.slice(0, 2).map((subject) => (
                            <Chip
                              key={subject}
                              label={subject}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                          {student.subjects.length > 2 && (
                            <Chip
                              label={`+${student.subjects.length - 2}`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Psychology sx={{ fontSize: 16, color: '#FF9800' }} />
                          <Typography variant="body2">
                            {Object.keys(student.current_learning_paths).length} active
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={student.is_active ? 'Active' : 'Inactive'}
                          size="small"
                          color={student.is_active ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton size="small" color="primary">
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton size="small" color="secondary">
                              <Edit />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton size="small" color="error">
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={handleCloseUploadDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            📤 Upload Students
          </Typography>
        </DialogTitle>
        <DialogContent>
          {!uploadResult ? (
            <Box>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Upload a CSV file with student data. Required columns: first_name, last_name, grade, password
              </Typography>
              
              <Paper
                {...getRootProps()}
                sx={{
                  p: 4,
                  border: '2px dashed #ccc',
                  borderRadius: 2,
                  textAlign: 'center',
                  cursor: 'pointer',
                  backgroundColor: isDragActive ? '#f5f5f5' : 'transparent',
                  '&:hover': {
                    backgroundColor: '#f9f9f9'
                  }
                }}
              >
                <input {...getInputProps()} />
                <CloudUpload sx={{ fontSize: 48, color: '#ccc', mb: 2 }} />
                <Typography variant="h6" sx={{ mb: 1 }}>
                  {isDragActive ? 'Drop the CSV file here' : 'Drag & drop CSV file here'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  or click to select file
                </Typography>
              </Paper>

              {uploading && (
                <Box sx={{ mt: 3 }}>
                  <LinearProgress />
                  <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
                    Uploading and processing students...
                  </Typography>
                </Box>
              )}
            </Box>
          ) : (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                {uploadResult.upload_summary}
              </Alert>
              
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={3}>
                  <Card sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="primary">
                      {uploadResult.total_students}
                    </Typography>
                    <Typography variant="body2">Total</Typography>
                  </Card>
                </Grid>
                <Grid item xs={3}>
                  <Card sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="success.main">
                      {uploadResult.students_created}
                    </Typography>
                    <Typography variant="body2">Created</Typography>
                  </Card>
                </Grid>
                <Grid item xs={3}>
                  <Card sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="warning.main">
                      {uploadResult.students_updated}
                    </Typography>
                    <Typography variant="body2">Updated</Typography>
                  </Card>
                </Grid>
                <Grid item xs={3}>
                  <Card sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="error.main">
                      {uploadResult.students_failed}
                    </Typography>
                    <Typography variant="body2">Failed</Typography>
                  </Card>
                </Grid>
              </Grid>

              {uploadResult.failed_students.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Failed Students:
                  </Typography>
                  {uploadResult.failed_students.map((failed, index) => (
                    <Alert key={index} severity="error" sx={{ mb: 1 }}>
                      Row {failed.row}: {failed.error}
                    </Alert>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUploadDialog}>
            {uploadResult ? 'Close' : 'Cancel'}
          </Button>
          {uploadResult && (
            <Button
              variant="contained"
              onClick={() => {
                setUploadResult(null);
                setUploadDialogOpen(false);
              }}
            >
              Upload Another File
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Students;