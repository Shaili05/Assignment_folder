import { useState, useEffect } from "react"
import { useNavigate, useLocation, Link } from "react-router-dom"
import "./Layout.css"
import { getMyIssues } from "../services/api"

function Layout({ children }) {
  const navigate = useNavigate()
  const location = useLocation()

  const userStr = localStorage.getItem("user")
  const user = userStr ? JSON.parse(userStr) : null

  const [hasMyWork, setHasMyWork] = useState(false)

  useEffect(() => {
    if (user?.role === "admin" || user?.role === "member") {
      getMyIssues().then(result => {
        if (Array.isArray(result) && result.length > 0) setHasMyWork(true)
      }).catch(() => {})
    }
  }, [])

  function handleLogout() {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    navigate("/login")
  }

  const navItems = [
    { path: "/dashboard", label: "Dashboard", icon: "▦" },
    { path: "/projects", label: "Projects", icon: "▤" },
  ]
  if (hasMyWork) {
    navItems.push({ path: "/my-work", label: "My Assigned Work", icon: "◈" })
  }
  if (user?.role === "admin") {
    navItems.push({ path: "/users", label: "Users", icon: "◇" })
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-icon">◆</span>
          <span className="logo-text">IssueTracker</span>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? "nav-item-active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer">
          {user && (
            <div className="user-info">
              <div className="user-avatar">{user.name?.[0]?.toUpperCase() || "U"}</div>
              <div className="user-details">
                <p className="user-name">{user.name}</p>
                <p className="user-role">{user.role}</p>
              </div>
            </div>
          )}
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </aside>
      <div className="main-wrapper">
        <header className="topbar">
          <div className="topbar-search">
            <span className="search-icon">⌕</span>
            <input className="search-input" placeholder="Search..." />
          </div>
        </header>
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout