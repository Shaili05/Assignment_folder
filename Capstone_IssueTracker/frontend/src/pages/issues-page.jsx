import { useState, useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import Layout from "../components/Layout"
import { getIssues, createIssue, updateIssueStatus, getProjectMembers, reassignIssue, updateIssue, deleteIssue, getProjectById } from "../services/api"
import "./issues-page.css"

function IssuesPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const projectId = searchParams.get("project_id")

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null
  const canCreate = user?.role === "admin" || user?.role === "member"
  const canUpdateStatus = user?.role === "admin" || user?.role === "member"
  const isAdmin = user?.role === "admin"

  const [issues, setIssues] = useState([])
  const [members, setMembers] = useState([])
  const [projectName, setProjectName] = useState("")
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [issueType, setIssueType] = useState("task")
  const [priority, setPriority] = useState("medium")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)

  const [openMenu, setOpenMenu] = useState(null)
  const [editingIssue, setEditingIssue] = useState(null)
  const [editTitle, setEditTitle] = useState("")
  const [editIssueType, setEditIssueType] = useState("task")
  const [editDescription, setEditDescription] = useState("")
  const [editPriority, setEditPriority] = useState("medium")

  useEffect(() => {
    if (projectId) {
      fetchIssues()
      fetchProjectName()
      if (isAdmin) fetchMembers()
    }
  }, [projectId])

  async function fetchProjectName() {
    try {
      const result = await getProjectById(projectId)
      if (result?.name) setProjectName(result.name)
    } catch (err) {}
  }

  async function fetchIssues() {
    try {
      const result = await getIssues(projectId)
      if (Array.isArray(result)) setIssues([...result].reverse())
    } catch (err) {
      setMessage("Failed to load issues")
    }
    setLoading(false)
  }

  async function fetchMembers() {
    try {
      const result = await getProjectMembers(projectId)
      if (Array.isArray(result)) setMembers(result)
    } catch (err) {}
  }

  async function handleCreate() {
    if (!title.trim()) { setMessage("Title is required."); return }
    try {
      await createIssue({ title, description, issue_type: issueType, priority, project_id: projectId })
      setMessage("Issue created successfully!")
      setTitle(""); setDescription("")
      fetchIssues()
    } catch (err) {
      setMessage(err.message || "Failed to create issue")
    }
  }

  async function handleStatusUpdate(issueId, newStatus) {
    try {
      await updateIssueStatus(issueId, newStatus)
      fetchIssues()
    } catch (err) {
      setMessage(err.message || "Failed to update status")
    }
  }

  async function handleReassign(issueId, newAssigneeId) {
    if (!newAssigneeId) return
    try {
      await reassignIssue(issueId, newAssigneeId)
      fetchIssues()
    } catch (err) {
      setMessage(err.message || "Failed to reassign issue")
    }
  }

  function getMemberName(memberId) {
    const found = members.find(m => m.id === memberId)
    return found ? found.name : null
  }

  function startEdit(issue) {
    setEditingIssue(issue.id)
    setEditDescription(issue.description || "")
    setEditPriority(issue.priority)
    setEditIssueType(issue.issue_type)
    setOpenMenu(null)
  }

  async function handleSaveEdit(issueId) {
  try {
    await updateIssue(issueId, { description: editDescription, priority: editPriority, issue_type: editIssueType })
    setEditingIssue(null)
    fetchIssues()
  } catch (err) {
    setMessage(err.message || "Failed to update issue")
  }
  }

  async function handleDeleteIssue(issueId) {
    if (!window.confirm("Delete this issue permanently?")) return
    try {
      await deleteIssue(issueId)
      setOpenMenu(null)
      fetchIssues()
    } catch (err) {
      setMessage(err.message || "Failed to delete issue")
    }
  }

  const statusColors = {
    BACKLOG: "#94a3b8", TODO: "#60a5fa",
    IN_PROGRESS: "#f59e0b", DONE: "#22c55e"
  }

  return (
    <Layout>
      <div className="issues-container">
        <div className="issues-header">
          <div>
            <h2>Issues</h2>
            {projectName && <p className="issues-project-subtitle">Project: {projectName}</p>}
          </div>
          <button className="back-btn" onClick={() => navigate("/projects")}>← Back to Projects</button>
        </div>

        <div className="issues-list">
          <h3>All Issues</h3>
          {loading ? <p>Loading...</p> : issues.length === 0 ? <p>No issues yet.</p> : (
            issues.map(issue => {
              const nextStatus = { BACKLOG: "TODO", TODO: "IN_PROGRESS", IN_PROGRESS: "DONE", DONE: null }[issue.status]
              const assigneeName = getMemberName(issue.assignee_id)
              const isEditing = editingIssue === issue.id

              if (isEditing) {
                return (
                  <div key={issue.id} className="issue-card">
                    <p className="issue-title">{issue.title}</p>
                    <input className="issues-input" value={editDescription} onChange={e => setEditDescription(e.target.value)} />
                    <select className="issues-select" value={editIssueType} onChange={e => setEditIssueType(e.target.value)}>
                      <option value="bug">Bug</option>
                      <option value="task">Task</option>
                      <option value="story">Story</option>
                    </select>
                    <select className="issues-select" value={editPriority} onChange={e => setEditPriority(e.target.value)}>
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                    <div className="issue-card-bottom">
                      <button className="status-btn" onClick={() => handleSaveEdit(issue.id)}>Save</button>
                      <button className="back-btn" onClick={() => setEditingIssue(null)}>Cancel</button>
                    </div>
                  </div>
                )
              }

              return (
                <div key={issue.id} className="issue-card">
                  <div className="issue-card-top">
                    <span className="issue-title">{issue.title}</span>
                    <span className="issue-status" style={{ backgroundColor: statusColors[issue.status] || "#94a3b8" }}>
                      {issue.status}
                    </span>
                    {isAdmin && (
                      <div className="row-menu-wrapper">
                        <button className="row-menu-btn" onClick={() => setOpenMenu(openMenu === issue.id ? null : issue.id)}>⋮</button>
                        {openMenu === issue.id && (
                          <div className="row-menu-dropdown">
                            <button onClick={() => startEdit(issue)}>Edit</button>
                            <button className="row-menu-delete" onClick={() => handleDeleteIssue(issue.id)}>Delete</button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="issue-card-bottom">
                    <span className="issue-type">{issue.issue_type}</span>
                    <span className="issue-priority">Priority: {issue.priority}</span>
                    <span className="issue-assignee">
                      Assigned to: {assigneeName || issue.assignee_id || "Unassigned"}
                    </span>
                    {canUpdateStatus && nextStatus && (
                      <button className="status-btn" onClick={() => handleStatusUpdate(issue.id, nextStatus)}>
                        Move to {nextStatus.replace("_", " ")}
                      </button>
                    )}
                    {isAdmin && members.length > 0 && (
                      <select
                        className="reassign-select"
                        value=""
                        onChange={(e) => handleReassign(issue.id, e.target.value)}
                      >
                        <option value="">Reassign to...</option>
                        {members.map(m => (
                          <option key={m.id} value={m.id}>{m.name}</option>
                        ))}
                      </select>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>

        {canCreate && (
          <div className="issues-form">
            <h3>Create New Issue</h3>
            <input className="issues-input" placeholder="Issue Title *" value={title} onChange={e => setTitle(e.target.value)} />
            <input className="issues-input" placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} />
            <select className="issues-select" value={issueType} onChange={e => setIssueType(e.target.value)}>
              <option value="bug">Bug</option>
              <option value="task">Task</option>
              <option value="story">Story</option>
            </select>
            <select className="issues-select" value={priority} onChange={e => setPriority(e.target.value)}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <button className="issues-button" onClick={handleCreate}>Create Issue</button>
            {message && (
              <p className={`issues-message ${message.includes("required") || message.includes("Failed") ? "issues-error" : ""}`}>
                {message}
              </p>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default IssuesPage