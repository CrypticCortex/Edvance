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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Image,
  PictureAsPdf,
  Archive,
  Visibility,
  Delete,
  CheckCircle,
  Schedule,
  Error,
  ExpandMore,
  Folder,
  InsertDriveFile
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { DocumentMetadata, DocumentUploadResponse } from '../../types';
import apiService from '../../services/api';
import API_ENDPOINTS from '../../config/api';

interface OrganizedDocuments {
  individual_documents: DocumentMetadata[];
  zip_extractions: Record<string, DocumentMetadata[]>;
  total_individual: number;
  total_zip_groups: number;
  total_extracted_files: number;
}

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<OrganizedDocuments>({
    individual_documents: [],
    zip_extractions: {},
    total_individual: 0,
    total_zip_groups: 0,
    total_extracted_files: 0
  });
  const [loading, setLoading] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [subject, setSubject] = useState('Mathematics');
  const [gradeLevel, setGradeLevel] = useState(5);

  const subjects = ['Mathematics', 'Science', 'English', 'History', 'Geography'];
  const grades = Array.from({ length: 12 }, (_, i) => i + 1);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const documentsData = await apiService.get<OrganizedDocuments>(API_ENDPOINTS.documents.organized);
      setDocuments(documentsData);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setUploading(true);
    try {
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append('file', file);
      formData.append('subject', subject);
      formData.append('grade_level', gradeLevel.toString());

      const result = await apiService.uploadFile<DocumentUploadResponse>(
        API_ENDPOINTS.documents.upload,
        formData
      );

      setUploadResult(result);
      await fetchDocuments(); // Refresh the list
    } catch (error) {
      console.error('Failed to upload document:', error);
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff'],
      'application/zip': ['.zip']
    },
    multiple: false
  });

  const getFileIcon = (fileType: string) => {
    if (fileType.includes('pdf')) return <PictureAsPdf sx={{ color: '#f44336' }} />;
    if (fileType.includes('image')) return <Image sx={{ color: '#4CAF50' }} />;
    if (fileType.includes('zip')) return <Archive sx={{ color: '#FF9800' }} />;
    return <Description sx={{ color: '#2196F3' }} />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle sx={{ color: '#4CAF50' }} />;
      case 'processing': return <Schedule sx={{ color: '#FF9800' }} />;
      case 'failed': return <Error sx={{ color: '#f44336' }} />;
      default: return <Schedule sx={{ color: '#9E9E9E' }} />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleCloseUploadDialog = () => {
    setUploadDialogOpen(false);
    setUploadResult(null);
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
            📁 Document Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Upload and manage educational materials for RAG-powered assessments
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<CloudUpload />}
          onClick={() => setUploadDialogOpen(true)}
          sx={{
            background: 'linear-gradient(45deg, #2196F3 30%, #1976D2 90%)',
            borderRadius: 3,
            px: 3
          }}
        >
          Upload Documents
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
                    Individual Files
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#2196F3' }}>
                    {documents.total_individual}
                  </Typography>
                </Box>
                <InsertDriveFile sx={{ fontSize: 40, color: '#2196F3' }} />
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
                    ZIP Archives
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#FF9800' }}>
                    {documents.total_zip_groups}
                  </Typography>
                </Box>
                <Archive sx={{ fontSize: 40, color: '#FF9800' }} />
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
                    Extracted Files
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#4CAF50' }}>
                    {documents.total_extracted_files}
                  </Typography>
                </Box>
                <Folder sx={{ fontSize: 40, color: '#4CAF50' }} />
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
                    Total Files
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#9C27B0' }}>
                    {documents.total_individual + documents.total_extracted_files}
                  </Typography>
                </Box>
                <Description sx={{ fontSize: 40, color: '#9C27B0' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Documents List */}
      <Card sx={{ borderRadius: 3, border: '1px solid #e0e0e0' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
            📚 Uploaded Documents
          </Typography>
          
          {documents.total_individual === 0 && documents.total_zip_groups === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <CloudUpload sx={{ fontSize: 64, color: '#ccc', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" sx={{ mb: 2 }}>
                No documents uploaded yet
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Upload educational materials to enable RAG-powered assessment generation
              </Typography>
              <Button
                variant="contained"
                startIcon={<CloudUpload />}
                onClick={() => setUploadDialogOpen(true)}
                sx={{ background: 'linear-gradient(45deg, #2196F3 30%, #1976D2 90%)' }}
              >
                Upload Documents
              </Button>
            </Box>
          ) : (
            <Box>
              {/* Individual Documents */}
              {documents.individual_documents.length > 0 && (
                <Box sx={{ mb: 4 }}>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                    📄 Individual Documents ({documents.total_individual})
                  </Typography>
                  <List>
                    {documents.individual_documents.map((doc) => (
                      <ListItem
                        key={doc.document_id}
                        sx={{
                          border: '1px solid #e0e0e0',
                          borderRadius: 2,
                          mb: 1,
                          '&:hover': {
                            backgroundColor: '#f5f5f5'
                          }
                        }}
                      >
                        <ListItemIcon>
                          {getFileIcon(doc.file_type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                {doc.filename}
                              </Typography>
                              <Chip label={doc.subject} size="small" color="primary" />
                              <Chip label={`Grade ${doc.grade_level}`} size="small" />
                              <Chip
                                label={doc.indexing_status}
                                size="small"
                                color={doc.indexing_status === 'completed' ? 'success' : 
                                       doc.indexing_status === 'processing' ? 'warning' : 'error'}
                              />
                            </Box>
                          }
                          secondary={
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="body2" color="textSecondary">
                                {formatFileSize(doc.file_size)} • Uploaded {new Date(doc.upload_date).toLocaleDateString()}
                              </Typography>
                            </Box>
                          }
                        />
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusIcon(doc.indexing_status)}
                          <IconButton size="small" color="primary">
                            <Visibility />
                          </IconButton>
                          <IconButton size="small" color="error">
                            <Delete />
                          </IconButton>
                        </Box>
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* ZIP Extractions */}
              {Object.keys(documents.zip_extractions).length > 0 && (
                <Box>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                    📦 ZIP Archive Extractions ({documents.total_zip_groups})
                  </Typography>
                  {Object.entries(documents.zip_extractions).map(([zipName, files]) => (
                    <Accordion key={zipName} sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                          <Archive sx={{ color: '#FF9800' }} />
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                            {zipName}
                          </Typography>
                          <Chip
                            label={`${files.length} files`}
                            size="small"
                            sx={{ bgcolor: '#FF9800', color: 'white' }}
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {files.map((doc) => (
                            <ListItem
                              key={doc.document_id}
                              sx={{
                                border: '1px solid #e0e0e0',
                                borderRadius: 1,
                                mb: 1,
                                ml: 2
                              }}
                            >
                              <ListItemIcon>
                                {getFileIcon(doc.file_type)}
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                      {doc.filename}
                                    </Typography>
                                    <Chip
                                      label={doc.indexing_status}
                                      size="small"
                                      color={doc.indexing_status === 'completed' ? 'success' : 
                                             doc.indexing_status === 'processing' ? 'warning' : 'error'}
                                    />
                                  </Box>
                                }
                                secondary={formatFileSize(doc.file_size)}
                              />
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {getStatusIcon(doc.indexing_status)}
                                <IconButton size="small" color="primary">
                                  <Visibility />
                                </IconButton>
                              </Box>
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}
            </Box>
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
            📤 Upload Educational Documents
          </Typography>
        </DialogTitle>
        <DialogContent>
          {!uploadResult ? (
            <Box sx={{ pt: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Upload educational materials for RAG-powered assessment generation. 
                Supported formats: PDF, DOC, DOCX, TXT, Images, ZIP archives
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    select
                    label="Subject"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    fullWidth
                  >
                    {subjects.map((subj) => (
                      <MenuItem key={subj} value={subj}>
                        {subj}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    select
                    label="Grade Level"
                    value={gradeLevel}
                    onChange={(e) => setGradeLevel(Number(e.target.value))}
                    fullWidth
                  >
                    {grades.map((grade) => (
                      <MenuItem key={grade} value={grade}>
                        Grade {grade}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
              </Grid>
              
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
                  {isDragActive ? 'Drop the file here' : 'Drag & drop file here'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  or click to select file (PDF, DOC, DOCX, TXT, Images, ZIP)
                </Typography>
              </Paper>

              {uploading && (
                <Box sx={{ mt: 3 }}>
                  <LinearProgress />
                  <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
                    Uploading and indexing document...
                  </Typography>
                </Box>
              )}
            </Box>
          ) : (
            <Box sx={{ pt: 1 }}>
              <Alert severity="success" sx={{ mb: 3 }}>
                Document uploaded successfully and is being indexed for RAG search!
              </Alert>
              
              {uploadResult.zip_filename ? (
                // ZIP upload result
                <Box>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                    ZIP Archive: {uploadResult.zip_filename}
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={3}>
                      <Card sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="primary">
                          {uploadResult.total_files_found}
                        </Typography>
                        <Typography variant="body2">Found</Typography>
                      </Card>
                    </Grid>
                    <Grid item xs={3}>
                      <Card sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="success.main">
                          {uploadResult.files_processed}
                        </Typography>
                        <Typography variant="body2">Processed</Typography>
                      </Card>
                    </Grid>
                    <Grid item xs={3}>
                      <Card sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="warning.main">
                          {uploadResult.files_skipped}
                        </Typography>
                        <Typography variant="body2">Skipped</Typography>
                      </Card>
                    </Grid>
                    <Grid item xs={3}>
                      <Card sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="error.main">
                          {uploadResult.files_failed}
                        </Typography>
                        <Typography variant="body2">Failed</Typography>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
              ) : (
                // Single file upload result
                <Box>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                    File: {uploadResult.filename}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Size: {formatFileSize(uploadResult.file_size)} • 
                    Subject: {uploadResult.subject} • 
                    Grade: {uploadResult.grade_level}
                  </Typography>
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

export default Documents;