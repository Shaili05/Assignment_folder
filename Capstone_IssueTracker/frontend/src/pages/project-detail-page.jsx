import { useState, useEffect } from "react"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"
import Layout from "../components/Layout"
import MemberSearchSelect from "../components/MemberSearchSelect"
import { getProjectById, getProjectMembers, updateProjectDescription, getAllUsers, addProjectMember, removeProjectMember } from "../services/api"
import "./project-detail-page.css"
import "../styles/modal.css"

function ProjectDetailPage() {
  const navigate = useNavigate()
  const { projectId } = useParams()
  const [searchParams] = useSearchParams()

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null
  const isAdmin = user?.role === "admin"

  const [project, setProject] = useState(null)
  const [members, setMembers] = useState([])
  const [allUsers, setAllUsers] = useState([])
  const [editing, setEditing] = useState(searchParams.get("edit") === "true")
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

  async function handleAddMember(selectedUser) {
    if (!selectedUser?.id) return
    try {
      await addProjectMember(projectId, selectedUser.id)
      const m = await getProjectMembers(projectId)
      if (Array.isArray(m)) setMembers(m)
    } catch (err) {
      setMessage(err.message || "Failed to add member")
    }
  }

  async function handleRemoveMember(userId) {
    if (!window.confirm("Remove this member from the project?")) return
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
          {editing ? (
            <div className="modal-body" style={{ padding: 0 }}>
              <h3>Edit Project</h3>

              <label>Project Name (locked)</label>
              <input className="projects-input" value={project.name} disabled />

              <label>Project Key (locked)</label>
              <input className="projects-input" value={project.project_key} disabled />

              <label>Description</label>
              <textarea
                className="projects-input"
                rows={4}
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Project description"
              />

              {message && <p className="detail-message">{message}</p>}
              <div className="modal-actions">
                <button className="back-btn" onClick={() => { setEditing(false); setDescription(project.description || "") }}>Cancel</button>
                <button className="projects-button" onClick={handleSave}>Save</button>
              </div>
            </div>
          ) : (
            <>
              <div className="detail-title-row">
                <h1 className="detail-title">{project.name}</h1>
                <span className="detail-key">[{project.project_key}]</span>
              </div>
              <p className="detail-desc">{project.description || "No description provided."}</p>
              {isAdmin && (
                <button className="issue-btn" onClick={() => setEditing(true)}>Edit Project</button>
              )}
              {message && <p className="detail-message">{message}</p>}
            </>
          )}
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
            <MemberSearchSelect
              options={allUsers.filter(u => !members.some(m => m.id === u.id))}
              onSelect={handleAddMember}
              placeholder="Search user to add..."
            />
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