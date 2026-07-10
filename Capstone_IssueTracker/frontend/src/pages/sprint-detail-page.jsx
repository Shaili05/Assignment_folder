import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import Layout from "../components/Layout"
import { getAllSprints, getProjectById, getProjectMembers, getAllIssues } from "../services/api"
import "./project-detail-page.css"

function SprintDetailPage() {
  const navigate = useNavigate()
  const { sprintId } = useParams()

  const [sprint, setSprint] = useState(null)
  const [projectName, setProjectName] = useState("")
  const [members, setMembers] = useState([])
  const [issues, setIssues] = useState([])
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => { fetchAll() }, [sprintId])

  async function fetchAll() {
    try {
      const all = await getAllSprints({})
      const found = Array.isArray(all) ? all.find(s => s.id === sprintId) : null
      if (!found) {
        setMessage("Sprint not found")
        setLoading(false)
        return
      }
      setSprint(found)
      const p = await getProjectById(found.project_id)
      setProjectName(p.name)
      const m = await getProjectMembers(found.project_id)
      if (Array.isArray(m)) setMembers(m)
      const allIssues = await getAllIssues({})
      if (Array.isArray(allIssues)) setIssues(allIssues.filter(i => found.issues.includes(i.id)))
    } catch (err) {
      setMessage("Failed to load sprint")
    }
    setLoading(false)
  }

  function getMemberName(memberId) {
    const found = members.find(m => m.id === memberId)
    return found ? found.name : null
  }

  if (loading) return <Layout><p className="muted-text">Loading...</p></Layout>
  if (!sprint) return <Layout><p className="muted-text">{message || "Sprint not found."}</p></Layout>

  return (
    <Layout>
      <div className="detail-container">
        <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>

        <div className="detail-header-card">
          <div className="detail-title-row">
            <h1 className="detail-title">{sprint.name}</h1>
            <span className="detail-key" style={{ textTransform: "capitalize" }}>{sprint.status}</span>
          </div>
          <p className="detail-desc">{sprint.goal || "No goal set."}</p>

          <p><strong>Project:</strong> {projectName}</p>
          <p><strong>Dates:</strong> {sprint.start_date} → {sprint.end_date}</p>
        </div>

        <div className="detail-members-card">
          <h3 className="form-heading">Project Members ({members.length})</h3>
          {members.length === 0 ? (
            <p className="muted-text">No members on this project.</p>
          ) : (
            members.map(m => (
              <div key={m.id} className="detail-member-row">
                <span>{m.name}</span>
                <span className="detail-member-role">{m.role}</span>
              </div>
            ))
          )}
        </div>

        <div className="detail-members-card">
          <h3 className="form-heading">Issues in this Sprint ({issues.length})</h3>
          {issues.length === 0 ? (
            <p className="muted-text">No issues assigned to this sprint.</p>
          ) : (
            issues.map(issue => (
              <div key={issue.id} className="detail-member-row">
                <span
                  className="issue-title-link"
                  style={{ cursor: "pointer" }}
                  onClick={() => navigate(`/issues/${issue.id}`)}
                >
                  {issue.title}
                </span>
                <span>Assigned to: {getMemberName(issue.assignee_id) || "Unassigned"} · {issue.status}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </Layout>
  )
}

export default SprintDetailPage