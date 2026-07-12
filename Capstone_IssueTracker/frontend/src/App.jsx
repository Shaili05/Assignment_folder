import { Routes, Route, Navigate } from "react-router-dom"
import LoginPage from "./pages/login-page"
import RegisterPage from "./pages/register-page"
import ProjectsPage from "./pages/projects-page"
import IssuesPage from "./pages/issues-page"
import "./App.css"

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/projects" element={<ProjectsPage />} />
      <Route path="/issues" element={<IssuesPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App