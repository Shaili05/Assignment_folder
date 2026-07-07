import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { registerUser } from "../services/api"
import { validateRegister } from "../utils/validations"
import "./login-page.css"

function RegisterPage() {
  const navigate = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [role, setRole] = useState("member")
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState("")

  function validate() {
    const newErrors = validateRegister(name, email, password)
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleRegister() {
    setMessage("")
    if (!validate()) return
    try {
      const encodedPassword = btoa(password)
      await registerUser({ name, email, password: encodedPassword, role })
      setMessage("Registration successful! Please login.")
      setName(""); setEmail(""); setPassword("")
    } catch (err) {
      setMessage(err.message || "Registration failed")
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-left">
        <div className="auth-brand">
          <span className="auth-brand-icon">⚡</span>
          <h2>Issue & Sprint Management</h2>
        </div>
        <p className="auth-tagline">Join your team and start tracking issues, managing sprints and shipping faster.</p>
        <div className="auth-illustration">
          <div className="illustration-box">
            <p>🎯 Assign → 📊 Track → 🚀 Deliver</p>
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-form-container">
          <h2 className="auth-title">Create Account</h2>
          <p className="auth-subtitle">Register to get started</p>

          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input className={`form-input ${errors.name ? "input-error" : ""}`} type="text" placeholder="Enter your name" value={name} onChange={e => setName(e.target.value)} />
            {errors.name && <p className="error-text">{errors.name}</p>}
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input className={`form-input ${errors.email ? "input-error" : ""}`} type="email" placeholder="Enter your email" value={email} onChange={e => setEmail(e.target.value)} />
            {errors.email && <p className="error-text">{errors.email}</p>}
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input className={`form-input ${errors.password ? "input-error" : ""}`} type="password" placeholder="Enter strong password" value={password} onChange={e => setPassword(e.target.value)} />
            {errors.password && <p className="error-text">{errors.password}</p>}
          </div>

          <div className="form-group">
            <label className="form-label">Role</label>
            <select className="form-input" value={role} onChange={e => setRole(e.target.value)}>
              <option value="member">Member</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          <button className="auth-btn" onClick={handleRegister}>Register</button>

          {message && (
            <p className={`auth-message ${message.includes("successful") ? "" : "error-text"}`}
               style={message.includes("successful") ? { color: "#16a34a", textAlign: "center", marginTop: "12px" } : {}}>
              {message}
            </p>
          )}

          <p className="auth-link">
            Already have an account?{" "}
            <Link to="/login" className="auth-link-text">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage