import { useState, useEffect } from "react"
import Layout from "../components/Layout"
import { getMyIssues, updateIssueStatus } from "../services/api"
import "./dashboard-page.css"

function MyWorkPage() {
  const [myIssues, setMyIssues] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState("")

  useEffect(() => { fetchMyIssues() }, [])

  async function fetchMyIssues() {
    try {
      const result = await getMyIssues()
      if (Array.isArray(result)) setMyIssues(result)
    } catch (err) {
      setMessage("Failed to load your assigned issues. Please refresh the page.")
    }
    setLoading(false)
  }

  async function handleStatusUpdate(issueId, newStatus) {
    try {
      await updateIssueStatus(issueId, newStatus)
      fetchMyIssues()
    } catch (err) {
      setMessage(err.message || "Failed to update status. Please try again.")
    }
  }

  const statusColors = {
    BACKLOG: "#94a3b8", TODO: "#60a5fa",
    IN_PROGRESS: "#f59e0b", DONE: "#22c55e"
  }

  return (
    <Layout>
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">My Assigned Work</h1>
            <p className="dashboard-subtitle">Issues currently assigned to you</p>
          </div>
        </div>

        {message && <p className="dashboard-error">{message}</p>}

        <div className="dashboard-section">
          {loading ? (
            <p className="loading-text">Loading...</p>
          ) : myIssues.length === 0 ? (
            <p className="empty-text">No issues currently assigned to you.</p>
          ) : (
            <div className="my-work-list">
              {myIssues.map(issue => {
                const nextStatus = { BACKLOG: "TODO", TODO: "IN_PROGRESS", IN_PROGRESS: "DONE", DONE: null }[issue.status]
                return (
                  <div key={issue.id} className="my-work-item">
                    <span className="my-work-title">{issue.title}</span>
                    <span className="my-work-status" style={{ backgroundColor: statusColors[issue.status] || "#94a3b8" }}>
                      {issue.status}
                    </span>
                    {nextStatus && (
                      <button className="my-work-btn" onClick={() => handleStatusUpdate(issue.id, nextStatus)}>
                        Move to {nextStatus.replace("_", " ")}
                      </button>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default MyWorkPage