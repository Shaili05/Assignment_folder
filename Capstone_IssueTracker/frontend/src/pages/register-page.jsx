import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { registerUser } from "../services/api"
import { validateRegister } from "../utils/validations"
import "./login-page.css"

function EyeIcon({ open }) {
  return open ? (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.5 18.5 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
      <line x1="1" y1="1" x2="23" y2="23"></line>
    </svg>
  ) : (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
      <circle cx="12" cy="12" r="3"></circle>
    </svg>
  )
}

function RegisterPage() {
  const navigate = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [role, setRole] = useState("member")
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState("")
  const [showPassword, setShowPassword] = useState(false)

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
            <div className="pw-input-wrapper">
              <input
                className={`form-input ${errors.password ? "input-error" : ""}`}
                type={showPassword ? "text" : "password"}
                placeholder="Enter strong password"
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
              <span className="pw-eye" onClick={() => setShowPassword(p => !p)}>
                <EyeIcon open={showPassword} />
              </span>
            </div>
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