import { useState, useEffect } from "react"
import Layout from "../components/Layout"
import { getAllUsers, updateUserRole, getAssignedCounts, deleteUser } from "../services/api"
import "./users-page.css"

function UsersPage() {
  const [users, setUsers] = useState([])
  const [counts, setCounts] = useState({})
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState("")

  const userStr = localStorage.getItem("user")
  const currentUser = userStr ? JSON.parse(userStr) : null

  useEffect(() => { fetchAll() }, [])

  async function fetchAll() {
    try {
      const u = await getAllUsers()
      if (Array.isArray(u)) setUsers(u)
    } catch (err) {}
    try {
      const c = await getAssignedCounts()
      if (c && typeof c === "object") setCounts(c)
    } catch (err) {}
    setLoading(false)
  }

  async function handleRoleChange(userId, newRole) {
    try {
      await updateUserRole(userId, newRole)
      setMessage("Role updated successfully.")
      fetchAll()
    } catch (err) {
      setMessage(err.message || "Failed to update role")
    }
  }

  async function handleDeleteUser(userId, userName) {
    if (!window.confirm(`Delete ${userName}'s account permanently? This cannot be undone.`)) return
    try {
      await deleteUser(userId)
      setMessage("User deleted successfully.")
      fetchAll()
    } catch (err) {
      setMessage(err.message || "Failed to delete user")
    }
  }

  return (
    <Layout>
      <div className="users-container">
        <h1 className="users-title">Manage Users</h1>
        {message && <p className="users-message">{message}</p>}
        <div className="users-list">
          {loading ? <p className="muted-text">Loading...</p> : (
            <table className="users-table">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Assigned Work</th><th>Role</th><th>Action</th></tr>
              </thead>
              <tbody>
                {users.map(u => {
                  const isSelf = u.id === currentUser?.user_id
                  return (
                    <tr key={u.id}>
                      <td>{u.name}</td>
                      <td>{u.email}</td>
                      <td>
                        <span className="work-count-badge">
                          {counts[u.id] || 0} active {counts[u.id] === 1 ? "issue" : "issues"}
                        </span>
                      </td>
                      <td>
                        {isSelf ? (
                          <span className="role-locked">{u.role} (you)</span>
                        ) : (
                          <select
                            className="role-select"
                            value={u.role}
                            onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          >
                            <option value="admin">Admin</option>
                            <option value="member">Member</option>
                            <option value="viewer">Viewer</option>
                          </select>
                        )}
                      </td>
                      <td>
                        {u.role !== "admin" && (
                          <button className="row-menu-delete" onClick={() => handleDeleteUser(u.id, u.name)}>Delete</button>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default UsersPage