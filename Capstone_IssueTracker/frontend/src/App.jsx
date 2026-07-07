import { Routes, Route, Navigate } from "react-router-dom"
import ProtectedRoute from "./components/ProtectedRoute"
import LoginPage from "./pages/login-page"
import RegisterPage from "./pages/register-page"
import DashboardPage from "./pages/dashboard-page"
import ProjectsPage from "./pages/projects-page"
import IssuesPage from "./pages/issues-page"
import SprintsPage from "./pages/sprints-page"
import ProjectDetailPage from "./pages/project-detail-page"
import MyWorkPage from "./pages/my-work-page"
import UsersPage from "./pages/users-page"
import "./App.css"

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/projects" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
      <Route path="/issues" element={<ProtectedRoute><IssuesPage /></ProtectedRoute>} />
      <Route path="/sprints" element={<ProtectedRoute><SprintsPage /></ProtectedRoute>} />
      <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
      <Route path="/my-work" element={<ProtectedRoute><MyWorkPage /></ProtectedRoute>} />
      <Route path="/users" element={<ProtectedRoute><UsersPage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App