import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import Layout from "../components/Layout"
import ConfirmDialog from "../components/ConfirmDialog"
import { getProjects, createProject, getAllUsers, addProjectMember, removeProjectMember, getProjectMembers, deleteProject, getAllIssues } from "../services/api"
import "./projects-page.css"
import "../styles/modal.css"
import MemberSearchSelect from "../components/MemberSearchSelect"

function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [allUsers, setAllUsers] = useState([])
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)
  const [expandedProject, setExpandedProject] = useState(null)
  const [projectMembers, setProjectMembers] = useState([])
  const [openMenu, setOpenMenu] = useState(null)
  const [projectStatus, setProjectStatus] = useState({})

  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [newMembers, setNewMembers] = useState([])

  const [deleteTarget, setDeleteTarget] = useState(null)
  const [removeMemberTarget, setRemoveMemberTarget] = useState(null)

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null

  useEffect(() => {
    fetchProjects()
    if (user?.role === "admin") fetchAllUsers()
  }, [])

  async function fetchProjects() {
    try {
      const result = await getProjects()
      if (Array.isArray(result)) {
        setProjects(result)
        computeProjectStatuses(result)
      }
    } catch (err) {}
    setLoading(false)
  }

  async function computeProjectStatuses(projectList) {
    const statusMap = {}
    for (const p of projectList) {
      try {
        const issues = await getAllIssues({ project_id: p.id })
        if (Array.isArray(issues) && issues.length > 0) {
          statusMap[p.id] = issues.every(i => i.status === "DONE") ? "completed" : "active"
        } else {
          statusMap[p.id] = "active"
        }
      } catch (err) {
        statusMap[p.id] = "active"
      }
    }
    setProjectStatus(statusMap)
  }

  async function fetchAllUsers() {
    try {
      const result = await getAllUsers()
      if (Array.isArray(result)) setAllUsers(result)
    } catch (err) {}
  }

  function openCreateForm() {
    setName(""); setDescription(""); setNewMembers([])
    setMessage("")
    setShowForm(true)
  }

  function addNewMember(selectedUser) {
    if (!selectedUser?.id) return
    if (newMembers.some(m => m.id === selectedUser.id)) return
    setNewMembers(prev => [...prev, selectedUser])
  }

  function removeNewMember(userId) {
    setNewMembers(prev => prev.filter(m => m.id !== userId))
  }

  async function handleCreate() {
    if (!name.trim()) { setMessage("Project name is required."); return }
    try {
      await createProject({
        name, description,
        members: newMembers.map(m => m.id)
      })
      setMessage("Project created successfully!")
      setShowForm(false)
      fetchProjects()
    } catch (err) {
      setMessage(err.message || "Failed to create project")
    }
  }

  async function confirmDeleteProject() {
    try {
      await deleteProject(deleteTarget.id)
      setOpenMenu(null)
      setDeleteTarget(null)
      fetchProjects()
    } catch (err) {
      setMessage(err.message || "Failed to delete project")
      setDeleteTarget(null)
    }
  }

  async function toggleMembers(projectId) {
    if (expandedProject === projectId) { setExpandedProject(null); return }
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

  async function confirmRemoveMember() {
    try {
      await removeProjectMember(removeMemberTarget.projectId, removeMemberTarget.userId)
      const result = await getProjectMembers(removeMemberTarget.projectId)
      if (Array.isArray(result)) setProjectMembers(result)
    } catch (err) {
      setMessage(err.message || "Failed to remove member")
    }
    setRemoveMemberTarget(null)
  }

  const avatarColors = ["#7a1f2b", "#b23a48", "#6d4c8f", "#2e7d4f", "#c07a1e"]
  function getInitials(n) {
    return n?.trim() ? n.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2) : "?"
  }

  return (
    <Layout>
      <div className="projects-container">
        <div className="issues-header">
          <h1 className="projects-title">Projects</h1>
          {user?.role === "admin" && (
            <button className="projects-button new-btn" onClick={openCreateForm}>+ New Project</button>
          )}
        </div>

        {message && (
          <p className={`projects-message ${message.includes("success") ? "" : "projects-error"}`}>{message}</p>
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
                  <span className={`status-badge ${projectStatus[project.id] === "completed" ? "status-completed" : ""}`}>
                    {projectStatus[project.id] === "completed" ? "Completed" : "Active"}
                  </span>
                  {user?.role === "admin" && (
                    <div className="row-menu-wrapper">
                      <button className="row-menu-btn" onClick={() => setOpenMenu(openMenu === project.id ? null : project.id)}>⋮</button>
                      {openMenu === project.id && (
                        <div className="row-menu-dropdown">
                          <button onClick={() => { navigate(`/projects/${project.id}?edit=true`); setOpenMenu(null) }}>Edit</button>
                          <button className="row-menu-delete" onClick={() => { setDeleteTarget(project); setOpenMenu(null) }}>Delete</button>
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
                          <button className="remove-btn" onClick={() => setRemoveMemberTarget({ projectId: project.id, userId: m.id, name: m.name })}>Remove</button>
                        </div>
                      ))
                    )}
                    <MemberSearchSelect
                      options={allUsers.filter(u => !projectMembers.some(m => m.id === u.id))}
                      onSelect={(selectedUser) => handleAddMember(project.id, selectedUser.id)}
                      placeholder="Search user to add..."
                    />
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create Project</h3>
              <button className="modal-close" onClick={() => setShowForm(false)}>×</button>
            </div>
            <div className="modal-body">
              <label>Project Name *</label>
              <input className="projects-input" value={name} onChange={e => setName(e.target.value)} />

              <label>Description</label>
              <textarea className="projects-input" rows={3} value={description} onChange={e => setDescription(e.target.value)} />

              <label>Members</label>
              <MemberSearchSelect
                options={allUsers.filter(u => !newMembers.some(m => m.id === u.id))}
                onSelect={addNewMember}
                placeholder="Search user to add..."
              />
              {newMembers.length > 0 && (
                <div className="member-panel">
                  {newMembers.map(m => (
                    <div key={m.id} className="member-row">
                      <span>{m.name} ({m.role})</span>
                      <button className="remove-btn" onClick={() => removeNewMember(m.id)}>Remove</button>
                    </div>
                  ))}
                </div>
              )}

              {message && <p className="projects-error">{message}</p>}
              <div className="modal-actions">
                <button className="back-btn" onClick={() => setShowForm(false)}>Cancel</button>
                <button className="projects-button" onClick={handleCreate}>Create Project</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {deleteTarget && (
        <ConfirmDialog
          message={`Delete "${deleteTarget.name}" and all its issues/sprints? This cannot be undone.`}
          confirmLabel="Delete"
          danger
          onConfirm={confirmDeleteProject}
          onCancel={() => setDeleteTarget(null)}
        />
      )}

      {removeMemberTarget && (
        <ConfirmDialog
          message={`Remove ${removeMemberTarget.name} from this project?`}
          confirmLabel="Remove"
          danger
          onConfirm={confirmRemoveMember}
          onCancel={() => setRemoveMemberTarget(null)}
        />
      )}
    </Layout>
  )
}

export default ProjectsPage