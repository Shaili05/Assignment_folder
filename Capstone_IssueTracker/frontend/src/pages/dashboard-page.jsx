import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import Layout from "../components/Layout"
import { getProjects } from "../services/api"
import "./dashboard-page.css"

function DashboardPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      const result = await getProjects()
      if (Array.isArray(result)) setProjects(result)
    } catch (err) {}
    setLoading(false)
  }

  const stats = [
    { label: "Total Projects", value: projects.length, icon: "▤", color: "var(--color-primary)", bg: "var(--color-primary-light)" },
    { label: "Total Issues", value: 0, icon: "◈", color: "var(--color-info)", bg: "var(--color-info-bg)" },
    { label: "Open Issues", value: 0, icon: "◉", color: "var(--color-warning)", bg: "var(--color-warning-bg)" },
    { label: "Active Sprints", value: 0, icon: "▲", color: "var(--color-success)", bg: "var(--color-success-bg)" },
  ]

  function getInitials(name) {
    return name?.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2) || "??"
  }

  const avatarColors = ["#4f46e5", "#7c3aed", "#0891b2", "#16a34a", "#d97706", "#dc2626"]

  return (
    <Layout>
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">Dashboard</h1>
            <p className="dashboard-subtitle">
              Welcome back, {user?.name || "User"} ({user?.role || "member"})
            </p>
          </div>
          {user?.role === "admin" && (
            <button className="new-project-btn" onClick={() => navigate("/projects")}>
              + New Project
            </button>
          )}
        </div>

        <div className="stats-grid">
          {stats.map((stat, i) => (
            <div key={i} className="stat-card">
              <div className="stat-info">
                <p className="stat-label">{stat.label}</p>
                <p className="stat-value" style={{ color: stat.color }}>{stat.value}</p>
              </div>
              <div className="stat-icon" style={{ backgroundColor: stat.bg, color: stat.color }}>{stat.icon}</div>
            </div>
          ))}
        </div>

        <div className="dashboard-section">
          <div className="section-header">
            <h2 className="section-title">All Projects</h2>
            <button className="view-all-btn" onClick={() => navigate("/projects")}>View All</button>
          </div>

          {loading ? (
            <p className="loading-text">Loading...</p>
          ) : projects.length === 0 ? (
            <p className="empty-text">No projects yet. Create one to get started!</p>
          ) : (
            <div className="project-list">
              {projects.map((project, i) => (
                <div key={project.id} className="project-row">
                  <div className="project-avatar" style={{ backgroundColor: avatarColors[i % avatarColors.length] }}>
                    {getInitials(project.name)}
                  </div>
                  <div className="project-info">
                    <p className="project-name project-name-link" onClick={() => navigate(`/projects/${project.id}`)}>
                      {project.name}
                    </p>
                    <p className="project-desc">{project.description}</p>
                  </div>
                  <div className="project-actions">
                    <button className="action-btn issues-btn" onClick={() => navigate(`/issues?project_id=${project.id}`)}>
                      Issues
                    </button>
                    <button className="action-btn sprints-btn" onClick={() => navigate(`/sprints?project_id=${project.id}`)}>
                      Sprints
                    </button>
                    <span className="project-status">Active</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default DashboardPage