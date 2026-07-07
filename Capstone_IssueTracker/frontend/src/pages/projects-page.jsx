import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import Layout from "../components/Layout"
import { getProjects, createProject, getAllUsers, addProjectMember, removeProjectMember, getProjectMembers, deleteProject } from "../services/api"
import "./projects-page.css"

function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [projectKey, setProjectKey] = useState("")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)
  const [allUsers, setAllUsers] = useState([])
  const [expandedProject, setExpandedProject] = useState(null)
  const [projectMembers, setProjectMembers] = useState([])
  const [openMenu, setOpenMenu] = useState(null)

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null

  useEffect(() => {
    fetchProjects()
    if (user?.role === "admin") fetchAllUsers()
  }, [])

  async function fetchProjects() {
    try {
      const result = await getProjects()
      if (Array.isArray(result)) setProjects(result)
    } catch (err) {}
    setLoading(false)
  }

  async function fetchAllUsers() {
    try {
      const result = await getAllUsers()
      if (Array.isArray(result)) setAllUsers(result)
    } catch (err) {}
  }

  async function handleCreate() {
    if (!name.trim()) { setMessage("Project name is required."); return }
    if (!projectKey.trim()) { setMessage("Project key is required."); return }
    try {
      await createProject({ name, description, project_key: projectKey, members: [] })
      setMessage("Project created successfully!")
      setName(""); setDescription(""); setProjectKey("")
      fetchProjects()
    } catch (err) {
      setMessage(err.message || "Failed to create project")
    }
  }

  async function handleDeleteProject(projectId) {
    if (!window.confirm("Delete this project and all its issues/sprints? This cannot be undone.")) return
    try {
      await deleteProject(projectId)
      setOpenMenu(null)
      fetchProjects()
    } catch (err) {
      setMessage(err.message || "Failed to delete project")
    }
  }

  async function toggleMembers(projectId) {
    if (expandedProject === projectId) {
      setExpandedProject(null)
      return
    }
    setExpandedProject(projectId)
    try {
      const result = await getProjectMembers(projectId)
      if (Array.isArray(result)) setProjectMembers(result)
    } catch (err) {
      setProjectMembers([])
    }
  }

  async function handleAddMember(projectId, userId) {
    if (!userId) return
    try {
      await addProjectMember(projectId, userId)
      const result = await getProjectMembers(projectId)
      if (Array.isArray(result)) setProjectMembers(result)
    } catch (err) {
      setMessage(err.message || "Failed to add member")
    }
  }

  async function handleRemoveMember(projectId, userId) {
    if (!window.confirm("Remove this member from the project?")) return
    try {
      await removeProjectMember(projectId, userId)
      const result = await getProjectMembers(projectId)
      if (Array.isArray(result)) setProjectMembers(result)
    } catch (err) {
      setMessage(err.message || "Failed to remove member")
    }
  }

  const avatarColors = ["#7a1f2b", "#b23a48", "#6d4c8f", "#2e7d4f", "#c07a1e"]

  function getInitials(n) {
    return n?.trim() ? n.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2) : "?"
  }

  return (
    <Layout>
      <div className="projects-container">
        <h1 className="projects-title">Projects</h1>

        {user?.role === "admin" && (
          <div className="projects-form">
            <h3 className="form-heading">Create New Project</h3>
            <input className="projects-input" placeholder="Project Name *" value={name} onChange={e => setName(e.target.value)} />
            <input className="projects-input" placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} />
            <input className="projects-input" placeholder="Project Key (e.g. PROJ) *" value={projectKey} onChange={e => setProjectKey(e.target.value)} />
            <button className="projects-button" onClick={handleCreate}>Create Project</button>
            {message && (
              <p className={`projects-message ${message.includes("success") ? "" : "projects-error"}`}>
                {message}
              </p>
            )}
          </div>
        )}

        <div className="projects-list">
          <h3 className="form-heading">All Projects</h3>
          {loading ? <p className="muted-text">Loading...</p> : projects.length === 0 ? <p className="muted-text">No projects yet.</p> : (
            projects.map((project, i) => (
              <div key={project.id} className="project-row">
                <div className="project-avatar" style={{ backgroundColor: avatarColors[i % avatarColors.length] }}>
                  {getInitials(project.name)}
                </div>
                <div className="project-info">
                  <p className="project-name project-name-link" onClick={() => navigate(`/projects/${project.id}`)}>
                    {project.name || "Untitled Project"}
                  </p>
                  <p className="project-desc">{project.description}</p>
                </div>
                <div className="project-actions">
                  <button className="issue-btn" onClick={() => navigate(`/issues?project_id=${project.id}`)}>Issues</button>
                  <button className="sprint-btn" onClick={() => navigate(`/sprints?project_id=${project.id}`)}>Sprints</button>
                  <span className="status-badge">Active</span>
                  {user?.role === "admin" && (
                    <div className="row-menu-wrapper">
                      <button className="row-menu-btn" onClick={() => setOpenMenu(openMenu === project.id ? null : project.id)}>⋮</button>
                      {openMenu === project.id && (
                        <div className="row-menu-dropdown">
                          <button onClick={() => { navigate(`/projects/${project.id}`); setOpenMenu(null) }}>View / Edit</button>
                          <button className="row-menu-delete" onClick={() => handleDeleteProject(project.id)}>Delete</button>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {user?.role === "admin" && (
                  <div className="member-panel-toggle">
                    <button className="issue-btn" onClick={() => toggleMembers(project.id)}>
                      {expandedProject === project.id ? "Hide Members" : "Manage Members"}
                    </button>
                  </div>
                )}

                {expandedProject === project.id && (
                  <div className="member-panel">
                    <h4 className="form-heading">Current Members</h4>
                    {projectMembers.length === 0 ? (
                      <p className="muted-text">No members yet.</p>
                    ) : (
                      projectMembers.map(m => (
                        <div key={m.id} className="member-row">
                          <span>{m.name} ({m.role})</span>
                          <button className="remove-btn" onClick={() => handleRemoveMember(project.id, m.id)}>Remove</button>
                        </div>
                      ))
                    )}
                    <select
                      className="projects-input"
                      value=""
                      onChange={(e) => handleAddMember(project.id, e.target.value)}
                    >
                      <option value="">Add member...</option>
                      {allUsers
                        .filter(u => !projectMembers.some(m => m.id === u.id))
                        .map(u => (
                          <option key={u.id} value={u.id}>{u.name} ({u.role})</option>
                        ))}
                    </select>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </Layout>
  )
}

export default ProjectsPage