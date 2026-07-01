import { useState, useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { getIssues, createIssue } from "../services/api"
import "./issues-page.css"

function IssuesPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const projectId = searchParams.get("project_id")

  const [issues, setIssues] = useState([])
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [issueType, setIssueType] = useState("task")
  const [priority, setPriority] = useState("medium")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (projectId) fetchIssues()
  }, [projectId])

  async function fetchIssues() {
    try {
      const result = await getIssues(projectId)
      if (Array.isArray(result)) setIssues(result)
    } catch (err) {
      setMessage("Failed to load issues")
    }
    setLoading(false)
  }

  async function handleCreate() {
    if (!title.trim()) {
      setMessage("Title is required.")
      return
    }
    try {
      await createIssue({ title, description, issue_type: issueType, priority, project_id: projectId })
      setMessage("Issue created successfully!")
      setTitle("")
      setDescription("")
      fetchIssues()
    } catch (err) {
      setMessage(err.message || "Failed to create issue")
    }
  }

  const statusColors = {
    BACKLOG: "#94a3b8",
    TODO: "#60a5fa",
    IN_PROGRESS: "#f59e0b",
    DONE: "#22c55e"
  }

  return (
    <div className="issues-container">
      <div className="issues-header">
        <h2>Issues</h2>
        <button className="back-btn" onClick={() => navigate("/projects")}>← Back to Projects</button>
      </div>

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

      <div className="issues-list">
        <h3>All Issues</h3>
        {loading ? <p>Loading...</p> : issues.length === 0 ? <p>No issues yet.</p> : (
          issues.map(issue => (
            <div key={issue.id} className="issue-card">
              <div className="issue-card-top">
                <span className="issue-title">{issue.title}</span>
                <span className="issue-status" style={{ backgroundColor: statusColors[issue.status] || "#94a3b8" }}>
                  {issue.status}
                </span>
              </div>
              <div className="issue-card-bottom">
                <span className="issue-type">{issue.issue_type}</span>
                <span className="issue-priority">Priority: {issue.priority}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default IssuesPage