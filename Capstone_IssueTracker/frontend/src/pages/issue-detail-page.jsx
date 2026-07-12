import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import Layout from "../components/Layout"
import ConfirmDialog from "../components/ConfirmDialog"
import { getIssueById, getProjectById, getProjectMembers, getAllSprints, getComments, addComment, updateComment, deleteComment } from "../services/api"
import "./project-detail-page.css"

function IssueDetailPage() {
  const navigate = useNavigate()
  const { issueId } = useParams()

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null

  const [issue, setIssue] = useState(null)
  const [projectName, setProjectName] = useState("")
  const [sprintName, setSprintName] = useState("")
  const [members, setMembers] = useState([])
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState("")
  const [editingComment, setEditingComment] = useState(null)
  const [editContent, setEditContent] = useState("")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)
  const [deleteCommentTarget, setDeleteCommentTarget] = useState(null)

  useEffect(() => { fetchAll() }, [issueId])

  async function fetchAll() {
    try {
      const i = await getIssueById(issueId)
      setIssue(i)
      const p = await getProjectById(i.project_id)
      setProjectName(p.name)
      const m = await getProjectMembers(i.project_id)
      if (Array.isArray(m)) setMembers(m)
      const allSprints = await getAllSprints({})
      const found = Array.isArray(allSprints) ? allSprints.find(s => s.issues.includes(issueId)) : null
      if (found) setSprintName(found.name)
    } catch (err) {
      setMessage("Failed to load issue")
      setLoading(false)
      return
    }
    try {
      const c = await getComments(issueId)
      if (Array.isArray(c)) setComments(c)
    } catch (err) {}
    setLoading(false)
  }

  function getMemberName(memberId) {
    const found = members.find(m => m.id === memberId)
    return found ? found.name : null
  }

  async function handleAddComment() {
    if (!newComment.trim()) return
    try {
      await addComment(issueId, newComment)
      setNewComment("")
      const c = await getComments(issueId)
      if (Array.isArray(c)) setComments(c)
    } catch (err) {
      setMessage(err.message || "Failed to add comment")
    }
  }

  function startEditComment(c) {
    setEditingComment(c.id)
    setEditContent(c.content)
  }

  async function handleSaveComment(commentId) {
    try {
      await updateComment(commentId, editContent)
      setEditingComment(null)
      const c = await getComments(issueId)
      if (Array.isArray(c)) setComments(c)
    } catch (err) {
      setMessage(err.message || "Failed to update comment")
    }
  }

  async function confirmDeleteComment() {
    try {
      await deleteComment(deleteCommentTarget)
      const c = await getComments(issueId)
      if (Array.isArray(c)) setComments(c)
    } catch (err) {
      setMessage(err.message || "Failed to delete comment")
    }
    setDeleteCommentTarget(null)
  }

  if (loading) return <Layout><p className="muted-text">Loading...</p></Layout>
  if (!issue) return <Layout><p className="muted-text">{message || "Issue not found."}</p></Layout>

  const assigneeName = getMemberName(issue.assignee_id)

  return (
    <Layout>
      <div className="detail-container">
        <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>

        <div className="detail-header-card">
          <div className="detail-title-row">
            <h1 className="detail-title">{issue.title}</h1>
            <span className="detail-key" style={{ textTransform: "capitalize" }}>{issue.issue_type}</span>
          </div>
          <p className="detail-desc">{issue.description || "No description provided."}</p>

          <p><strong>Project:</strong> {projectName}</p>
          <p><strong>Status:</strong> {issue.status}</p>
          <p><strong>Priority:</strong> {issue.priority}</p>
          <p><strong>Sprint:</strong> {sprintName || "Not in a sprint"}</p>
          <p><strong>Assigned to:</strong> {assigneeName || issue.assignee_id || "Unassigned"}</p>
          {message && <p className="detail-message">{message}</p>}
        </div>

        <div className="detail-members-card">
          <h3 className="form-heading">Project Members</h3>
          {members.length === 0 ? (
            <p className="muted-text">No members on this project.</p>
          ) : (
            members.map(m => (
              <div key={m.id} className="detail-member-row">
                <span>{m.name} {m.id === issue.assignee_id && <em style={{ color: "var(--color-primary)" }}>(assignee)</em>}</span>
                <span className="detail-member-role">{m.role}</span>
              </div>
            ))
          )}
        </div>

        <div className="detail-members-card">
          <h3 className="form-heading">Comments ({comments.length})</h3>

          {comments.length === 0 ? (
            <p className="muted-text">No comments yet.</p>
          ) : (
            comments.map(c => (
              <div key={c.id} className="detail-member-row" style={{ flexDirection: "column", alignItems: "flex-start", gap: 6 }}>
                {editingComment === c.id ? (
                  <>
                    <textarea className="projects-input comment-textarea" rows={4} value={editContent} onChange={e => setEditContent(e.target.value)} />
                    <div style={{ display: "flex", gap: 8 }}>
                      <button className="issue-btn" onClick={() => handleSaveComment(c.id)}>Save</button>
                      <button className="back-btn" onClick={() => setEditingComment(null)}>Cancel</button>
                    </div>
                  </>
                ) : (
                  <>
                    <strong>{c.author_name}</strong>
                    <span>{c.content}</span>
                    {c.author_id === user?.user_id && (
                      <div style={{ display: "flex", gap: 8 }}>
                        <button className="issue-btn" onClick={() => startEditComment(c)}>Edit</button>
                        <button className="remove-btn" onClick={() => setDeleteCommentTarget(c.id)}>Delete</button>
                      </div>
                    )}
                  </>
                )}
              </div>
            ))
          )}

          <textarea
            className="projects-input comment-textarea"
            placeholder="Add a comment..."
            rows={5}
            value={newComment}
            onChange={e => setNewComment(e.target.value)}
            style={{ marginTop: 12 }}
          />
          <button className="issues-button" style={{ marginTop: 8 }} onClick={handleAddComment}>Post Comment</button>
        </div>
      </div>

      {deleteCommentTarget && (
        <ConfirmDialog
          message="Delete this comment? This cannot be undone."
          confirmLabel="Delete"
          danger
          onConfirm={confirmDeleteComment}
          onCancel={() => setDeleteCommentTarget(null)}
        />
      )}
    </Layout>
  )
}

export default IssueDetailPage