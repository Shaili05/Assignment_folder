import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import Layout from "../components/Layout"
import { getProjectById, getProjectMembers, updateProjectDescription, getAllUsers, addProjectMember, removeProjectMember } from "../services/api"
import "./project-detail-page.css"

function ProjectDetailPage() {
  const navigate = useNavigate()
  const { projectId } = useParams()

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null
  const isAdmin = user?.role === "admin"

  const [project, setProject] = useState(null)
  const [members, setMembers] = useState([])
  const [allUsers, setAllUsers] = useState([])
  const [editing, setEditing] = useState(false)
  const [description, setDescription] = useState("")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (projectId) fetchAll()
    if (isAdmin) fetchAllUsers()
  }, [projectId])

  async function fetchAll() {
    try {
      const p = await getProjectById(projectId)
      setProject(p)
      setDescription(p.description || "")
    } catch (err) {
      setMessage("Failed to load project")
    }
    try {
      const m = await getProjectMembers(projectId)
      if (Array.isArray(m)) setMembers(m)
    } catch (err) {}
    setLoading(false)
  }

  async function fetchAllUsers() {
    try {
      const result = await getAllUsers()
      if (Array.isArray(result)) setAllUsers(result)
    } catch (err) {}
  }

  async function handleSave() {
    try {
      const updated = await updateProjectDescription(projectId, description)
      setProject(updated)
      setEditing(false)
      setMessage("Project updated successfully!")
    } catch (err) {
      setMessage(err.message || "Failed to update project")
    }
  }

  async function handleAddMember(userId) {
    if (!userId) return
    try {
      await addProjectMember(projectId, userId)
      const m = await getProjectMembers(projectId)
      if (Array.isArray(m)) setMembers(m)
    } catch (err) {
      setMessage(err.message || "Failed to add member")
    }
  }

  async function handleRemoveMember(userId) {
    try {
      await removeProjectMember(projectId, userId)
      const m = await getProjectMembers(projectId)
      if (Array.isArray(m)) setMembers(m)
    } catch (err) {
      setMessage(err.message || "Failed to remove member")
    }
  }

  if (loading) return <Layout><p className="muted-text">Loading...</p></Layout>
  if (!project) return <Layout><p className="muted-text">Project not found.</p></Layout>

  return (
    <Layout>
      <div className="detail-container">
        <button className="back-btn" onClick={() => navigate("/projects")}>← Back to Projects</button>

        <div className="detail-header-card">
          <div className="detail-title-row">
            <h1 className="detail-title">{project.name}</h1>
            <span className="detail-key">[{project.project_key}]</span>
          </div>

          {editing ? (
            <div className="detail-edit-form">
              <textarea
                className="detail-textarea"
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Project description"
              />
              <div className="detail-edit-actions">
                <button className="issues-button" onClick={handleSave}>Save</button>
                <button className="back-btn" onClick={() => { setEditing(false); setDescription(project.description || "") }}>Cancel</button>
              </div>
            </div>
          ) : (
            <p className="detail-desc">{project.description || "No description provided."}</p>
          )}

          {isAdmin && !editing && (
            <button className="issue-btn" onClick={() => setEditing(true)}>Edit Description</button>
          )}
          {message && <p className="detail-message">{message}</p>}

          <p className="detail-note">Project name and key cannot be changed after creation.</p>
        </div>

        <div className="detail-members-card">
          <h3 className="form-heading">Team Members</h3>
          {members.length === 0 ? (
            <p className="muted-text">No members yet.</p>
          ) : (
            members.map(m => (
              <div key={m.id} className="detail-member-row">
                <span>{m.name} ({m.role})</span>
                {isAdmin && (
                  <button className="remove-btn" onClick={() => handleRemoveMember(m.id)}>Remove</button>
                )}
              </div>
            ))
          )}
          {isAdmin && (
            <select
              className="detail-add-select"
              value=""
              onChange={(e) => handleAddMember(e.target.value)}
            >
              <option value="">Add member...</option>
              {allUsers
                .filter(u => !members.some(m => m.id === u.id))
                .map(u => (
                  <option key={u.id} value={u.id}>{u.name} ({u.role})</option>
                ))}
            </select>
          )}
        </div>

        <div className="detail-actions-row">
          <button className="issue-btn" onClick={() => navigate(`/issues?project_id=${project.id}`)}>View Issues</button>
          <button className="sprint-btn" onClick={() => navigate(`/sprints?project_id=${project.id}`)}>View Sprints</button>
        </div>
      </div>
    </Layout>
  )
}

export default ProjectDetailPage