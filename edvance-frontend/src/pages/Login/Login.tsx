import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Paper,
  Divider,
  Link,
  InputAdornment,
  IconButton
} from '@mui/material';
import {
  AutoAwesome,
  Email,
  Lock,
  Visibility,
  VisibilityOff,
  Login as LoginIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showToken, setShowToken] = useState(false);

  const handleLogin = async () => {
    if (!token.trim()) {
      setError('Please enter your Firebase ID token');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(token);
      navigate('/dashboard');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login failed. Please check your token.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2
      }}
    >
      <Card
        sx={{
          maxWidth: 500,
          width: '100%',
          borderRadius: 4,
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
          overflow: 'visible'
        }}
      >
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
              <AutoAwesome sx={{ fontSize: 40, color: '#667eea', mr: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#333' }}>
                Edvance AI
              </Typography>
            </Box>
            <Typography variant="h6" color="textSecondary" sx={{ mb: 1 }}>
              Intelligent Teaching Assistant
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Powered by Google AI • Ultra-Fast • Automated
            </Typography>
          </Box>

          {/* Login Form */}
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, textAlign: 'center' }}>
              Welcome Back! 👋
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <TextField
              fullWidth
              label="Firebase ID Token"
              type={showToken ? 'text' : 'password'}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Paste your Firebase ID token here"
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowToken(!showToken)}
                      edge="end"
                    >
                      {showToken ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />

            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleLogin}
              disabled={loading}
              startIcon={<LoginIcon />}
              sx={{
                background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                borderRadius: 3,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold',
                mb: 3
              }}
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </Button>

            <Divider sx={{ my: 3 }}>
              <Typography variant="body2" color="textSecondary">
                Need a token?
              </Typography>
            </Divider>

            <Paper
              sx={{
                p: 3,
                bgcolor: '#f8f9fa',
                border: '1px solid #e0e0e0',
                borderRadius: 2
              }}
            >
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
                🔑 How to get your Firebase ID Token:
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                1. Open <code>get_id_token.html</code> in your browser
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                2. Enter your teacher account credentials
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                3. Copy the generated ID token
              </Typography>
              <Typography variant="body2" color="textSecondary">
                4. Paste it above and sign in
              </Typography>
            </Paper>

            <Box sx={{ textAlign: 'center', mt: 3 }}>
              <Typography variant="body2" color="textSecondary">
                Don't have an account?{' '}
                <Link href="#" color="primary" sx={{ fontWeight: 'bold' }}>
                  Contact Administrator
                </Link>
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;