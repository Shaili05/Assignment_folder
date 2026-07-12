import { useState, useEffect } from "react"
import Layout from "../components/Layout"
import ConfirmDialog from "../components/ConfirmDialog"
import { getAllSprints, getProjects, createSprint, addIssueToSprint, getAllIssues, updateSprint, updateSprintStatus, deleteSprint } from "../services/api"
import "./sprints-page.css"
import "../styles/modal.css"
import { useNavigate, useSearchParams } from "react-router-dom"

function SprintsPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null
  const canCreate = user?.role === "admin"
  const canAddIssue = user?.role === "admin" || user?.role === "member"
  const isAdmin = user?.role === "admin"
  const todayStr = new Date().toISOString().split("T")[0]

  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(
    searchParams.get("project_id") || localStorage.getItem("activeProjectFilter") || ""
  )
  const [sprints, setSprints] = useState([])
  const [availableIssues, setAvailableIssues] = useState([])

  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState("")
  const [goal, setGoal] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [status, setStatus] = useState("planned")
  const [selectedIssue, setSelectedIssue] = useState({})
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const PAGE_SIZE = 10

  const [openMenu, setOpenMenu] = useState(null)
  const [editingSprint, setEditingSprint] = useState(null)
  const [editGoal, setEditGoal] = useState("")
  const [editStartDate, setEditStartDate] = useState("")
  const [editEndDate, setEditEndDate] = useState("")
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [completedNotice, setCompletedNotice] = useState(null)

  useEffect(() => { fetchProjects(); fetchAllOpenIssues() }, [])

  useEffect(() => {
    if (selectedProject) localStorage.setItem("activeProjectFilter", selectedProject)
    else localStorage.removeItem("activeProjectFilter")
    setPage(1)
    fetchSprints()
  }, [selectedProject])

  async function fetchProjects() {
    try {
      const result = await getProjects()
      if (Array.isArray(result)) setProjects(result)
    } catch (err) {}
  }

  async function fetchAllOpenIssues() {
    try {
      const result = await getAllIssues({})
      if (Array.isArray(result)) setAvailableIssues(result)
    } catch (err) {}
  }

  async function fetchSprints() {
    setLoading(true)
    try {
      const filters = selectedProject ? { project_id: selectedProject } : {}
      const result = await getAllSprints(filters)
      if (Array.isArray(result)) setSprints([...result].reverse())
    } catch (err) {}
    setLoading(false)
  }

  function openCreateForm() {
    setName(""); setGoal(""); setStartDate(""); setEndDate(""); setStatus("planned")
    setMessage("")
    setShowForm(true)
  }

  async function handleCreate() {
    if (!selectedProject) { setMessage("Select a project first."); return }
    if (!name.trim()) { setMessage("Sprint name is required."); return }
    if (!startDate || !endDate) { setMessage("Start and end dates are required."); return }
    if (new Date(endDate) < new Date(startDate)) { setMessage("End date cannot be before start date."); return }
    try {
      await createSprint({ name, project_id: selectedProject, goal, start_date: startDate, end_date: endDate, status })
      setMessage("Sprint created successfully!")
      setShowForm(false)
      fetchSprints()
    } catch (err) {
      setMessage(err.message || "Failed to create sprint")
    }
  }

  async function handleAddIssue(sprintId) {
    const issueId = selectedIssue[sprintId]
    if (!issueId) { setMessage("Please select an issue."); return }
    try {
      await addIssueToSprint(sprintId, issueId)
      setMessage("Issue added to sprint!")
      setSelectedIssue(prev => ({ ...prev, [sprintId]: "" }))
      fetchSprints()
    } catch (err) { setMessage(err.message || "Failed to add issue") }
  }

  async function handleStatusChange(sprintId, newStatus) {
    try { await updateSprintStatus(sprintId, newStatus); fetchSprints() }
    catch (err) { setMessage(err.message || "Failed to update sprint status") }
  }

  function startEdit(sprint) {
    setEditingSprint(sprint.id)
    setEditGoal(sprint.goal || "")
    setEditStartDate(sprint.start_date || "")
    setEditEndDate(sprint.end_date || "")
    setOpenMenu(null)
  }

  async function handleSaveEdit(sprintId) {
    if (editStartDate && editEndDate && new Date(editEndDate) < new Date(editStartDate)) {
      setMessage("End date cannot be before start date.")
      return
    }
    try {
      await updateSprint(sprintId, { goal: editGoal, start_date: editStartDate || null, end_date: editEndDate || null })
      setEditingSprint(null)
      fetchSprints()
    } catch (err) { setMessage(err.message || "Failed to update sprint") }
  }

  async function confirmDeleteSprint() {
    try {
      await deleteSprint(deleteTarget.id)
      setOpenMenu(null)
      setDeleteTarget(null)
      fetchSprints()
    } catch (err) {
      setMessage(err.message || "Failed to delete sprint")
      setDeleteTarget(null)
    }
  }

  const statusColors = { planned: "#94a3b8", active: "var(--color-primary)", completed: "#22c55e" }
  const totalPages = Math.ceil(sprints.length / PAGE_SIZE) || 1
  const pagedSprints = sprints.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <Layout>
      <div className="sprints-container">
        <div className="sprints-header">
          <h2>Sprints</h2>
          {canCreate && <button className="sprints-button new-btn" onClick={openCreateForm}>+ New Sprint</button>}
        </div>

        <div className="issues-filters">
          <select className="sprints-select" value={selectedProject} onChange={e => setSelectedProject(e.target.value)}>
            <option value="">All Projects</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>

        {message && <p className={`sprints-message ${message.includes("required") || message.includes("Failed") || message.includes("select") || message.includes("active") || message.includes("End date") ? "sprints-error" : ""}`}>{message}</p>}

        <div className="sprints-list">
          {loading ? <p>Loading...</p> : pagedSprints.length === 0 ? <p>No sprints found.</p> : (
            pagedSprints.map(sprint => {
              const projectName = projects.find(p => p.id === sprint.project_id)?.name
              const sprintIssueOptions = availableIssues.filter(
                i => i.project_id === sprint.project_id && i.status !== "DONE" && !sprint.issues.includes(i.id)
              )
              const isCompleted = sprint.status === "completed"

              return (
                <div key={sprint.id} className="sprint-card">
                  <div className="sprint-card-top">
                    <div>
                      <strong className="issue-title-link" onClick={() => navigate(`/sprints/${sprint.id}`)}>{sprint.name}</strong>
                      {!selectedProject && projectName && <span className="issue-project-tag">{projectName}</span>}
                    </div>
                    {isAdmin && !isCompleted ? (
                      <select className="sprints-select" value={sprint.status} onChange={(e) => handleStatusChange(sprint.id, e.target.value)}
                        style={{ backgroundColor: statusColors[sprint.status] || "#94a3b8", color: "#fff", fontWeight: "600" }}>
                        <option value="planned">Planned</option><option value="active">Active</option><option value="completed">Completed</option>
                      </select>
                    ) : (
                      <span
                        className="sprint-status"
                        style={{ backgroundColor: statusColors[sprint.status] || "#94a3b8", cursor: isCompleted ? "pointer" : "default" }}
                        onClick={() => isCompleted && setCompletedNotice(sprint.name)}
                      >
                        {sprint.status}
                      </span>
                    )}
                    {isAdmin && !isCompleted && (
                      <div className="row-menu-wrapper">
                        <button className="row-menu-btn" onClick={() => setOpenMenu(openMenu === sprint.id ? null : sprint.id)}>⋮</button>
                        {openMenu === sprint.id && (
                          <div className="row-menu-dropdown">
                            <button onClick={() => startEdit(sprint)}>Edit</button>
                            <button className="row-menu-delete" onClick={() => { setDeleteTarget(sprint); setOpenMenu(null) }}>Delete</button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  {sprint.goal && <p className="sprint-goal">{sprint.goal}</p>}
                  {sprint.start_date && sprint.end_date && <p className="sprint-goal">{sprint.start_date} → {sprint.end_date}</p>}
                  <p className="sprint-issues-count">Issues in sprint: {sprint.issues.length}</p>
                  {canAddIssue && !isCompleted && (
                    <div className="sprint-add-issue">
                      <select className="sprints-select" value={selectedIssue[sprint.id] || ""}
                        onChange={e => setSelectedIssue(prev => ({ ...prev, [sprint.id]: e.target.value }))}>
                        <option value="">Select issue to add</option>
                        {sprintIssueOptions.map(issue => (
                          <option key={issue.id} value={issue.id}>{issue.title}</option>
                        ))}
                      </select>
                      <button className="add-issue-btn" onClick={() => handleAddIssue(sprint.id)}>Add Issue</button>
                    </div>
                  )}

                  {editingSprint === sprint.id && (
                    <div className="modal-overlay" onClick={() => setEditingSprint(null)}>
                      <div className="modal-card" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                          <h3>Edit Sprint</h3>
                          <button className="modal-close" onClick={() => setEditingSprint(null)}>×</button>
                        </div>
                        <div className="modal-body">
                          <label>Sprint Name (locked)</label>
                          <input className="sprints-input" value={sprint.name} disabled />

                          <label>Goal</label>
                          <textarea className="sprints-input" rows={2} value={editGoal} onChange={e => setEditGoal(e.target.value)} />

                          <div className="modal-row">
                            <div>
                              <label>Start Date</label>
                              <input className="sprints-input" type="date" min={todayStr} value={editStartDate} onChange={e => setEditStartDate(e.target.value)} />
                            </div>
                            <div>
                              <label>End Date</label>
                              <input className="sprints-input" type="date" min={editStartDate || todayStr} value={editEndDate} onChange={e => setEditEndDate(e.target.value)} />
                            </div>
                          </div>

                          {message && <p className="sprints-error">{message}</p>}
                          <div className="modal-actions">
                            <button className="back-btn" onClick={() => setEditingSprint(null)}>Cancel</button>
                            <button className="sprints-button" onClick={() => handleSaveEdit(sprint.id)}>Save</button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>

        {totalPages > 1 && (
          <div className="pagination-controls">
            <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>Previous</button>
            <span>Page {page} of {totalPages}</span>
            <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next</button>
          </div>
        )}
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create Sprint</h3>
              <button className="modal-close" onClick={() => setShowForm(false)}>×</button>
            </div>
            <div className="modal-body">
              <label>Project *</label>
              <select className="sprints-select" value={selectedProject} onChange={e => setSelectedProject(e.target.value)}>
                <option value="">Select project</option>
                {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
              <label>Sprint Name *</label>
              <input className="sprints-input" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Sprint 2" />
              <label>Goal</label>
              <textarea className="sprints-input" rows={2} value={goal} onChange={e => setGoal(e.target.value)} />
              <div className="modal-row">
                <div>
                  <label>Start Date</label>
                  <input className="sprints-input" type="date" min={todayStr} value={startDate} onChange={e => setStartDate(e.target.value)} />
                </div>
                <div>
                  <label>End Date</label>
                  <input className="sprints-input" type="date" min={startDate || todayStr} value={endDate} onChange={e => setEndDate(e.target.value)} />
                </div>
              </div>
              <label>Status</label>
              <select className="sprints-select" value={status} onChange={e => setStatus(e.target.value)}>
                <option value="planned">Planned</option>
                <option value="active">Active</option>
              </select>
              {message && <p className="sprints-error">{message}</p>}
              <div className="modal-actions">
                <button className="back-btn" onClick={() => setShowForm(false)}>Cancel</button>
                <button className="sprints-button" onClick={handleCreate}>Create Sprint</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {deleteTarget && (
        <ConfirmDialog
          message={`Delete "${deleteTarget.name}" permanently? This cannot be undone.`}
          confirmLabel="Delete"
          danger
          onConfirm={confirmDeleteSprint}
          onCancel={() => setDeleteTarget(null)}
        />
      )}

      {completedNotice && (
        <ConfirmDialog
          message={`"${completedNotice}" is already completed and can no longer be changed.`}
          confirmLabel="OK"
          onConfirm={() => setCompletedNotice(null)}
        />
      )}
    </Layout>
  )
}

export default SprintsPage