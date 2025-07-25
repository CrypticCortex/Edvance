import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
  Divider,
  Avatar,
  Chip
} from '@mui/material';
import {
  Dashboard,
  People,
  School,
  Assessment,
  Analytics,
  CloudUpload,
  Psychology,
  Chat,
  Settings,
  AutoAwesome
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 280;

interface SidebarProps {
  open: boolean;
}

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
  { text: 'Students', icon: <People />, path: '/students' },
  { text: 'Learning Paths', icon: <Psychology />, path: '/learning-paths', badge: 'AI' },
  { text: 'Lessons', icon: <School />, path: '/lessons', badge: 'Ultra-Fast' },
  { text: 'Assessments', icon: <Assessment />, path: '/assessments' },
  { text: 'Documents', icon: <CloudUpload />, path: '/documents' },
  { text: 'Analytics', icon: <Analytics />, path: '/analytics' },
  { text: 'AI Assistant', icon: <Chat />, path: '/assistant', badge: 'Smart' },
];

const Sidebar: React.FC<SidebarProps> = ({ open }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        },
      }}
    >
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <AutoAwesome sx={{ fontSize: 32, color: '#FFD700' }} />
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
            Edvance AI
          </Typography>
        </Box>
      </Toolbar>
      
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)' }} />
      
      {/* User Profile Section */}
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Avatar sx={{ mx: 'auto', mb: 1, bgcolor: 'rgba(255,255,255,0.2)' }}>
          {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'T'}
        </Avatar>
        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
          {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : 'Teacher'}
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.8 }}>
          {user?.subjects?.length || 0} subjects
        </Typography>
      </Box>
      
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)' }} />

      <List sx={{ flexGrow: 1, pt: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              selected={location.pathname === item.path}
              sx={{
                mx: 1,
                borderRadius: 2,
                '&.Mui-selected': {
                  backgroundColor: 'rgba(255,255,255,0.2)',
                  '&:hover': {
                    backgroundColor: 'rgba(255,255,255,0.3)',
                  },
                },
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: '0.9rem',
                  fontWeight: location.pathname === item.path ? 'bold' : 'normal'
                }}
              />
              {item.badge && (
                <Chip
                  label={item.badge}
                  size="small"
                  sx={{
                    bgcolor: '#FFD700',
                    color: '#333',
                    fontSize: '0.7rem',
                    height: 20,
                    fontWeight: 'bold'
                  }}
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="caption" sx={{ opacity: 0.7 }}>
          Powered by Google AI
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Sidebar;