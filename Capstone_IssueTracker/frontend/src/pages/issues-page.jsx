import { useState, useEffect } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import Layout from "../components/Layout"
import ConfirmDialog from "../components/ConfirmDialog"
import { getAllIssues, getProjects, createIssue, updateIssueStatus, getProjectMembers, reassignIssue, updateIssue, deleteIssue, getSprints, addIssueToSprint } from "../services/api"
import "./issues-page.css"
import "../styles/modal.css"

function orderByHierarchy(list) {
  const byParent = {}
  list.forEach(i => {
    const key = i.parent_id || "root"
    if (!byParent[key]) byParent[key] = []
    byParent[key].push(i)
  })
  const result = []
  function addChildren(parentId) {
    (byParent[parentId] || []).forEach(child => {
      result.push(child)
      addChildren(child.id)
    })
  }
  addChildren("root")
  return result
}

function IssuesPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null
  const canCreate = user?.role === "admin" || user?.role === "member"
  const canUpdateStatus = user?.role === "admin" || user?.role === "member"
  const isAdmin = user?.role === "admin"

  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(
    searchParams.get("project_id") || localStorage.getItem("activeProjectFilter") || ""
  )
  const [issues, setIssues] = useState([])
  const [members, setMembers] = useState([])
  const [membersByProject, setMembersByProject] = useState({})

  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [issueType, setIssueType] = useState("task")
  const [priority, setPriority] = useState("medium")
  const [assigneeId, setAssigneeId] = useState("")
  const [parentId, setParentId] = useState("")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)

  const [editingIssue, setEditingIssue] = useState(null)
  const [editDescription, setEditDescription] = useState("")
  const [editPriority, setEditPriority] = useState("medium")
  const [editParentId, setEditParentId] = useState("")
  const [editSprintId, setEditSprintId] = useState("")
  const [editSprints, setEditSprints] = useState([])
  const [openMenu, setOpenMenu] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null)

  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [page, setPage] = useState(1)
  const PAGE_SIZE = 10

  const assignableMembers = members.filter(m => m.role !== "viewer")
  const storyIssuesForProject = issues.filter(i => i.issue_type === "story" && i.project_id === selectedProject)

  useEffect(() => { fetchProjects() }, [])

  useEffect(() => {
    if (projects.length > 0) fetchAllMembers()
  }, [projects])

  useEffect(() => {
    if (selectedProject) {
      localStorage.setItem("activeProjectFilter", selectedProject)
      fetchMembers(selectedProject)
    } else {
      localStorage.removeItem("activeProjectFilter")
      setMembers([])
    }
    setPage(1)
    fetchIssues()
  }, [selectedProject, searchTerm, statusFilter])

  async function fetchProjects() {
    try {
      const result = await getProjects()
      if (Array.isArray(result)) setProjects(result)
    } catch (err) {}
  }

  async function fetchAllMembers() {
    const map = {}
    for (const p of projects) {
      try {
        const m = await getProjectMembers(p.id)
        if (Array.isArray(m)) map[p.id] = m
      } catch (err) {}
    }
    setMembersByProject(map)
  }

  async function fetchMembers(projectId) {
    try {
      const m = await getProjectMembers(projectId)
      if (Array.isArray(m)) setMembers(m)
    } catch (err) {}
  }

  async function fetchIssues() {
    setLoading(true)
    try {
      const filters = {
        ...(selectedProject ? { project_id: selectedProject } : {}),
        ...(searchTerm ? { search: searchTerm } : {}),
        ...(statusFilter ? { status: statusFilter } : {})
      }
      const result = await getAllIssues(filters)
      if (Array.isArray(result)) setIssues([...result].reverse())
    } catch (err) {
      setMessage("Failed to load issues")
    }
    setLoading(false)
  }

  function getMemberName(projectId, memberId) {
    const list = membersByProject[projectId] || []
    const found = list.find(m => m.id === memberId)
    return found ? found.name : null
  }

  function openCreateForm() {
    setAssigneeId(""); setParentId(""); setTitle(""); setDescription("")
    setMessage("")
    setShowForm(true)
  }

  async function handleCreate() {
    if (!selectedProject) { setMessage("Select a project first."); return }
    if (!title.trim()) { setMessage("Title is required."); return }
    try {
      await createIssue({
        title, description, issue_type: issueType, priority,
        project_id: selectedProject,
        assignee_id: assigneeId || null,
        parent_id: parentId || null
      })
      setMessage("Issue created successfully!")
      setTitle(""); setDescription(""); setAssigneeId(""); setParentId("")
      setShowForm(false)
      fetchIssues()
    } catch (err) {
      setMessage(err.message || "Failed to create issue")
    }
  }

  async function handleStatusUpdate(issueId, newStatus) {
    try { await updateIssueStatus(issueId, newStatus); fetchIssues() }
    catch (err) { setMessage(err.message || "Failed to update status") }
  }

  async function handleReassign(issueId, newAssigneeId) {
    if (!newAssigneeId) return
    try { await reassignIssue(issueId, newAssigneeId); fetchIssues() }
    catch (err) { setMessage(err.message || "Failed to reassign issue") }
  }

  async function startEdit(issue) {
    setEditingIssue(issue.id)
    setEditDescription(issue.description || "")
    setEditPriority(issue.priority)
    setEditParentId(issue.parent_id || "")
    setEditSprintId("")
    setOpenMenu(null)
    try {
      const s = await getSprints(issue.project_id)
      if (Array.isArray(s)) setEditSprints(s.filter(sp => sp.status !== "completed"))
    } catch (err) { setEditSprints([]) }
  }

  async function handleSaveEdit(issue) {
    try {
      await updateIssue(issue.id, {
        description: editDescription,
        priority: editPriority,
        issue_type: issue.issue_type,
        parent_id: editParentId || null
      })
      if (editSprintId) {
        await addIssueToSprint(editSprintId, issue.id)
      }
      setEditingIssue(null)
      fetchIssues()
    } catch (err) { setMessage(err.message || "Failed to update issue") }
  }

  async function confirmDeleteIssue() {
    try {
      await deleteIssue(deleteTarget.id)
      setOpenMenu(null)
      setDeleteTarget(null)
      fetchIssues()
    } catch (err) {
      setMessage(err.message || "Failed to delete issue")
      setDeleteTarget(null)
    }
  }

  const statusColors = { BACKLOG: "#94a3b8", TODO: "#60a5fa", IN_PROGRESS: "#f59e0b", DONE: "#22c55e" }
  const orderedIssues = orderByHierarchy(issues)
  const totalPages = Math.ceil(orderedIssues.length / PAGE_SIZE) || 1
  const pagedIssues = orderedIssues.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <Layout>
      <div className="issues-container">
        <div className="issues-header">
          <h2>Issues</h2>
          {canCreate && (
            <button className="issues-button new-btn" onClick={openCreateForm}>+ New Issue</button>
          )}
        </div>

        <div className="issues-filters">
          <select className="issues-select" value={selectedProject} onChange={e => setSelectedProject(e.target.value)}>
            <option value="">All Projects</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <input
            className="issues-input"
            placeholder="Search by title or description..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
          <select className="issues-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="BACKLOG">Backlog</option>
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="DONE">Done</option>
          </select>
        </div>

        {message && <p className={`issues-message ${message.includes("required") || message.includes("Failed") || message.includes("Select") ? "issues-error" : ""}`}>{message}</p>}

        <div className="issues-list">
          {loading ? <p>Loading...</p> : pagedIssues.length === 0 ? <p>No issues found.</p> : (
            pagedIssues.map(issue => {
              const nextStatus = { BACKLOG: "TODO", TODO: "IN_PROGRESS", IN_PROGRESS: "DONE", DONE: null }[issue.status]
              const assigneeName = getMemberName(issue.project_id, issue.assignee_id)
              const projectName = projects.find(p => p.id === issue.project_id)?.name

              return (
                <div key={issue.id} className={`issue-card ${issue.parent_id ? "issue-card-child" : ""}`}>
                  <div className="issue-card-top">
                    {issue.parent_id && <span className="child-marker">↳</span>}
                    <span className="issue-title issue-title-link" onClick={() => navigate(`/issues/${issue.id}`)}>{issue.title}</span>
                    <span className="issue-status" style={{ backgroundColor: statusColors[issue.status] || "#94a3b8" }}>{issue.status}</span>
                    {isAdmin && (
                      <div className="row-menu-wrapper">
                        <button className="row-menu-btn" onClick={() => setOpenMenu(openMenu === issue.id ? null : issue.id)}>⋮</button>
                        {openMenu === issue.id && (
                          <div className="row-menu-dropdown">
                            <button onClick={() => startEdit(issue)}>Edit</button>
                            <button className="row-menu-delete" onClick={() => { setDeleteTarget(issue); setOpenMenu(null) }}>Delete</button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="issue-card-bottom">
                    {!selectedProject && projectName && <span className="issue-project-tag">{projectName}</span>}
                    <span className="issue-type">{issue.issue_type}</span>
                    <span className="issue-priority">Priority: {issue.priority}</span>
                    <span className="issue-assignee">Assigned to: {assigneeName || (issue.assignee_id ? "Unknown user" : "Unassigned")}</span>
                    {canUpdateStatus && nextStatus && (
                      <button className="status-btn" onClick={() => handleStatusUpdate(issue.id, nextStatus)}>Move to {nextStatus.replace("_", " ")}</button>
                    )}
                    {isAdmin && assignableMembers.length > 0 && selectedProject && (
                      <select className="reassign-select" value="" onChange={(e) => handleReassign(issue.id, e.target.value)}>
                        <option value="">Reassign to...</option>
                        {assignableMembers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                      </select>
                    )}
                  </div>

                  {editingIssue === issue.id && (
                    <div className="modal-overlay" onClick={() => setEditingIssue(null)}>
                      <div className="modal-card" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                          <h3>Edit Issue</h3>
                          <button className="modal-close" onClick={() => setEditingIssue(null)}>×</button>
                        </div>
                        <div className="modal-body">
                          <label>Title (locked)</label>
                          <input className="issues-input" value={issue.title} disabled />

                          <label>Type (locked)</label>
                          <input className="issues-input" value={issue.issue_type} disabled style={{ textTransform: "capitalize" }} />

                          <label>Description</label>
                          <textarea className="issues-input" rows={3} value={editDescription} onChange={e => setEditDescription(e.target.value)} />

                          <label>Priority</label>
                          <select className="issues-select" value={editPriority} onChange={e => setEditPriority(e.target.value)}>
                            <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option>
                          </select>

                          <label>Parent Story</label>
                          <select className="issues-select" value={editParentId} onChange={e => setEditParentId(e.target.value)}>
                            <option value="">No parent story</option>
                            {storyIssuesForProject.filter(s => s.id !== issue.id).map(s => <option key={s.id} value={s.id}>{s.title}</option>)}
                          </select>

                          <label>Add to Sprint</label>
                          <select className="issues-select" value={editSprintId} onChange={e => setEditSprintId(e.target.value)}>
                            <option value="">Don't add to a sprint</option>
                            {editSprints.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                          </select>

                          {message && <p className="issues-error">{message}</p>}
                          <div className="modal-actions">
                            <button className="back-btn" onClick={() => setEditingIssue(null)}>Cancel</button>
                            <button className="issues-button" onClick={() => handleSaveEdit(issue)}>Save</button>
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
              <h3>Create Issue</h3>
              <button className="modal-close" onClick={() => setShowForm(false)}>×</button>
            </div>
            <div className="modal-body">
              <label>Project *</label>
              <select className="issues-select" value={selectedProject} onChange={e => setSelectedProject(e.target.value)}>
                <option value="">Select project</option>
                {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>

              <label>Title *</label>
              <input className="issues-input" value={title} onChange={e => setTitle(e.target.value)} />

              <label>Description</label>
              <textarea className="issues-input" rows={3} value={description} onChange={e => setDescription(e.target.value)} />

              <div className="modal-row">
                <div>
                  <label>Type</label>
                  <select className="issues-select" value={issueType} onChange={e => setIssueType(e.target.value)}>
                    <option value="bug">Bug</option><option value="task">Task</option><option value="story">Story</option>
                  </select>
                </div>
                <div>
                  <label>Priority</label>
                  <select className="issues-select" value={priority} onChange={e => setPriority(e.target.value)}>
                    <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option>
                  </select>
                </div>
              </div>

              <label>Assignee</label>
              <select className="issues-select" value={assigneeId} onChange={e => setAssigneeId(e.target.value)} disabled={!selectedProject}>
                <option value="">{selectedProject ? "Unassigned" : "Select a project first"}</option>
                {assignableMembers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>

              <label>Parent Story</label>
              <select className="issues-select" value={parentId} onChange={e => setParentId(e.target.value)} disabled={!selectedProject}>
                <option value="">{selectedProject ? "No parent story" : "Select a project first"}</option>
                {storyIssuesForProject.map(s => <option key={s.id} value={s.id}>{s.title}</option>)}
              </select>

              {message && <p className="issues-error">{message}</p>}
              <div className="modal-actions">
                <button className="back-btn" onClick={() => setShowForm(false)}>Cancel</button>
                <button className="issues-button" onClick={handleCreate}>Create Issue</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {deleteTarget && (
        <ConfirmDialog
          message={`Delete "${deleteTarget.title}" permanently? This cannot be undone.`}
          confirmLabel="Delete"
          danger
          onConfirm={confirmDeleteIssue}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </Layout>
  )
}

export default IssuesPage