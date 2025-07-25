# Edvance AI Frontend

A modern, responsive React frontend for the Edvance AI Teaching Assistant platform.

## 🚀 Features

- **Modern UI/UX**: Built with Material-UI and custom gradients
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Updates**: Live data synchronization with backend
- **Interactive Components**: Drag & drop, charts, and dynamic forms
- **AI-Powered Interface**: Showcases AI capabilities prominently

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components
- **React Router** for navigation
- **Axios** for API calls
- **React Dropzone** for file uploads
- **Recharts** for data visualization
- **Vite** for fast development

## 📱 Pages & Features

### 🏠 Dashboard
- Welcome section with AI status indicators
- Quick stats cards (students, learning paths, lessons)
- Quick action buttons for common tasks
- Recent activity feed

### 👥 Students
- Student list with grade and subject filters
- CSV upload with drag & drop interface
- Batch upload results with detailed feedback
- Student profile management

### 🧠 Learning Paths
- AI monitoring activation
- Student learning path visualization
- Automatic path generation from assessments
- Progress tracking and analytics

### 📚 Lessons
- Ultra-fast lesson generation (~27 seconds)
- Interactive lesson viewer
- Chatbot integration
- Progress tracking

### 📁 Documents
- Document upload with RAG indexing
- ZIP file extraction and processing
- Organized document management
- Indexing status tracking

## 🔧 Setup & Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure API endpoint:**
   Update `src/config/api.ts` if your backend runs on a different port:
   ```typescript
   export const API_BASE_URL = 'http://localhost:8000/adk';
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## 🔐 Authentication

The frontend uses Firebase ID tokens for authentication:

1. Get a token from `get_id_token.html` in the backend
2. Paste the token in the login form
3. The token is stored in localStorage for subsequent requests

## 🎨 Design System

### Colors
- **Primary**: `#667eea` (Gradient blue)
- **Secondary**: `#764ba2` (Gradient purple)
- **Success**: `#4CAF50`
- **Warning**: `#FF9800`
- **Error**: `#f44336`

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

### Components
- **Cards**: Rounded corners (12px), subtle shadows
- **Buttons**: Gradient backgrounds, no text transform
- **Icons**: Material Design with custom colors

## 📊 API Integration

The frontend integrates with all backend endpoints:

- **Authentication**: User signup, profile management
- **Students**: CSV upload, management, statistics
- **Learning Paths**: AI monitoring, path generation, progress tracking
- **Lessons**: Ultra-fast generation, interactive viewing
- **Documents**: Upload, RAG indexing, organization
- **Assessments**: Configuration, generation (coming soon)
- **Analytics**: Teacher dashboard, student insights (coming soon)

## 🚀 Key Features

### AI-Powered Interface
- Prominent AI status indicators
- Ultra-fast generation timers
- Automated workflow highlights

### Interactive Elements
- Drag & drop file uploads
- Real-time progress bars
- Dynamic charts and graphs
- Responsive data tables

### User Experience
- Smooth animations and transitions
- Loading states and feedback
- Error handling with user-friendly messages
- Mobile-first responsive design

## 🔄 State Management

- **React Context** for authentication
- **Local state** with React hooks
- **API service** with Axios interceptors
- **Error boundaries** for graceful error handling

## 📱 Responsive Design

- **Mobile-first** approach
- **Breakpoints**: xs, sm, md, lg, xl
- **Flexible layouts** with CSS Grid and Flexbox
- **Touch-friendly** interactions

## 🎯 Performance

- **Code splitting** with React.lazy
- **Optimized images** and assets
- **Efficient re-renders** with React.memo
- **Fast development** with Vite HMR

## 🧪 Development

### File Structure
```
src/
├── components/          # Reusable UI components
│   └── Layout/         # Layout components
├── contexts/           # React contexts
├── pages/              # Page components
├── services/           # API services
├── types/              # TypeScript types
├── config/             # Configuration files
└── App.tsx             # Main app component
```

### Adding New Pages
1. Create component in `src/pages/`
2. Add route in `App.tsx`
3. Add navigation item in `Sidebar.tsx`
4. Define types in `src/types/`

### API Integration
1. Add endpoint to `src/config/api.ts`
2. Create service methods in `src/services/api.ts`
3. Use in components with error handling

## 🚀 Deployment

The frontend can be deployed to any static hosting service:

- **Netlify**: Drag & drop build folder
- **Vercel**: Connect GitHub repository
- **Firebase Hosting**: Use Firebase CLI
- **AWS S3**: Upload build files

## 📞 Support

For technical support or questions:
- Check the backend API documentation at `http://localhost:8000/adk/docs`
- Review the component documentation in the code
- Test API endpoints with the provided examples

---

*Built with ❤️ for the future of AI-powered education*