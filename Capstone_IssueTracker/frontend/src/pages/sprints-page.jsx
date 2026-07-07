import { useState, useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import Layout from "../components/Layout"
import { getSprints, createSprint, addIssueToSprint, getIssues, updateSprint, updateSprintStatus, deleteSprint, getProjectById } from "../services/api"
import "./sprints-page.css"

function SprintsPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const projectId = searchParams.get("project_id")

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null
  const canCreate = user?.role === "admin"
  const canAddIssue = user?.role === "admin" || user?.role === "member"
  const isAdmin = user?.role === "admin"

  const [sprints, setSprints] = useState([])
  const [issues, setIssues] = useState([])
  const [projectName, setProjectName] = useState("")
  const [name, setName] = useState("")
  const [goal, setGoal] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [selectedIssue, setSelectedIssue] = useState("")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)

  const [openMenu, setOpenMenu] = useState(null)
  const [editingSprint, setEditingSprint] = useState(null)
  const [editName, setEditName] = useState("")
  const [editGoal, setEditGoal] = useState("")

  useEffect(() => {
    if (projectId) { fetchSprints(); fetchIssues(); fetchProjectName() }
  }, [projectId])

  async function fetchProjectName() {
    try {
      const result = await getProjectById(projectId)
      if (result?.name) setProjectName(result.name)
    } catch (err) {}
  }

  async function fetchSprints() {
    try {
      const result = await getSprints(projectId)
      if (Array.isArray(result)) setSprints([...result].reverse())
    } catch (err) {}
    setLoading(false)
  }

  async function fetchIssues() {
    try {
      const result = await getIssues(projectId)
      if (Array.isArray(result)) setIssues(result.filter(i => i.status !== "DONE"))
    } catch (err) {}
  }

  async function handleCreate() {
    if (!name.trim()) { setMessage("Sprint name is required."); return }
    if (!startDate || !endDate) { setMessage("Start and end dates are required."); return }
    try {
      await createSprint({ name, project_id: projectId, goal, start_date: startDate, end_date: endDate })
      setMessage("Sprint created successfully!")
      setName(""); setGoal(""); setStartDate(""); setEndDate("")
      fetchSprints()
    } catch (err) {
      setMessage(err.message || "Failed to create sprint")
    }
  }

  async function handleAddIssue(sprintId) {
    if (!selectedIssue) { setMessage("Please select an issue."); return }
    try {
      await addIssueToSprint(sprintId, selectedIssue)
      setMessage("Issue added to sprint!")
      setSelectedIssue("")
      fetchSprints()
    } catch (err) {
      setMessage(err.message || "Failed to add issue")
    }
  }

  async function handleStatusChange(sprintId, newStatus) {
    try {
      await updateSprintStatus(sprintId, newStatus)
      fetchSprints()
    } catch (err) {
      setMessage(err.message || "Failed to update sprint status")
    }
  }

  function startEdit(sprint) {
    setEditingSprint(sprint.id)
    setEditName(sprint.name)
    setEditGoal(sprint.goal || "")
    setOpenMenu(null)
  }

  async function handleSaveEdit(sprintId) {
    try {
      await updateSprint(sprintId, { name: editName, goal: editGoal })
      setEditingSprint(null)
      fetchSprints()
    } catch (err) {
      setMessage(err.message || "Failed to update sprint")
    }
  }

  async function handleDeleteSprint(sprintId) {
    if (!window.confirm("Delete this sprint permanently?")) return
    try {
      await deleteSprint(sprintId)
      setOpenMenu(null)
      fetchSprints()
    } catch (err) {
      setMessage(err.message || "Failed to delete sprint")
    }
  }

  const statusColors = { planned: "#94a3b8", active: "var(--color-primary)", completed: "#22c55e" }

  return (
    <Layout>
      <div className="sprints-container">
        <div className="sprints-header">
          <div>
            <h2>Sprints</h2>
            {projectName && <p className="sprints-project-subtitle">Project: {projectName}</p>}
          </div>
          <button className="back-btn" onClick={() => navigate("/projects")}>← Back to Projects</button>
        </div>

        <div className="sprints-list">
          <h3>All Sprints</h3>
          {loading ? <p>Loading...</p> : sprints.length === 0 ? <p>No sprints yet.</p> : (
            sprints.map(sprint => {
              const isEditing = editingSprint === sprint.id

              if (isEditing) {
                return (
                  <div key={sprint.id} className="sprint-card">
                    <input className="sprints-input" value={editName} onChange={e => setEditName(e.target.value)} />
                    <input className="sprints-input" value={editGoal} onChange={e => setEditGoal(e.target.value)} placeholder="Sprint Goal" />
                    <div className="sprint-add-issue">
                      <button className="add-issue-btn" onClick={() => handleSaveEdit(sprint.id)}>Save</button>
                      <button className="back-btn" onClick={() => setEditingSprint(null)}>Cancel</button>
                    </div>
                  </div>
                )
              }

              return (
                <div key={sprint.id} className="sprint-card">
                  <div className="sprint-card-top">
                    <strong>{sprint.name}</strong>
                    {isAdmin ? (
                      <select
                        className="sprints-select"
                        value={sprint.status}
                        onChange={(e) => handleStatusChange(sprint.id, e.target.value)}
                        style={{ backgroundColor: statusColors[sprint.status] || "#94a3b8", color: "#fff", fontWeight: "600" }}
                      >
                        <option value="planned">Planned</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                      </select>
                    ) : (
                      <span className="sprint-status" style={{ backgroundColor: statusColors[sprint.status] || "#94a3b8" }}>
                        {sprint.status}
                      </span>
                    )}
                    {isAdmin && (
                      <div className="row-menu-wrapper">
                        <button className="row-menu-btn" onClick={() => setOpenMenu(openMenu === sprint.id ? null : sprint.id)}>⋮</button>
                        {openMenu === sprint.id && (
                          <div className="row-menu-dropdown">
                            <button onClick={() => startEdit(sprint)}>Edit</button>
                            <button className="row-menu-delete" onClick={() => handleDeleteSprint(sprint.id)}>Delete</button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  {sprint.goal && <p className="sprint-goal">{sprint.goal}</p>}
                  {sprint.start_date && sprint.end_date && (
                    <p className="sprint-goal">{sprint.start_date} → {sprint.end_date}</p>
                  )}
                  <p className="sprint-issues-count">Issues in sprint: {sprint.issues.length}</p>
                  {canAddIssue && (
                    <div className="sprint-add-issue">
                      <select className="sprints-select" value={selectedIssue} onChange={e => setSelectedIssue(e.target.value)}>
                        <option value="">Select issue to add</option>
                        {issues.map(issue => (
                          <option key={issue.id} value={issue.id}>{issue.title}</option>
                        ))}
                      </select>
                      <button className="add-issue-btn" onClick={() => handleAddIssue(sprint.id)}>Add Issue</button>
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>

        {canCreate && (
          <div className="sprints-form">
            <h3>Create New Sprint</h3>
            <input className="sprints-input" placeholder="Sprint Name *" value={name} onChange={e => setName(e.target.value)} />
            <input className="sprints-input" placeholder="Sprint Goal" value={goal} onChange={e => setGoal(e.target.value)} />
            <input className="sprints-input" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
            <input className="sprints-input" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
            <button className="sprints-button" onClick={handleCreate}>Create Sprint</button>
            {message && (
              <p className={`sprints-message ${message.includes("required") || message.includes("Failed") || message.includes("select") || message.includes("active") ? "sprints-error" : ""}`}>
                {message}
              </p>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default SprintsPage