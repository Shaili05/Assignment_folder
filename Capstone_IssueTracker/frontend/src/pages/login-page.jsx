import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { loginUser } from "../services/api"
import { validateLogin } from "../utils/validations"
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

function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  function validate() {
    const newErrors = validateLogin(email, password)
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleLogin() {
    setMessage("")
    if (!validate()) return
    try {
      const encodedPassword = btoa(password)
      const result = await loginUser({ email, password: encodedPassword })
      localStorage.setItem("token", result.access_token)
      localStorage.setItem("user", JSON.stringify({
        user_id: result.user_id,
        name: result.name,
        email: result.email,
        role: result.role
      }))
      navigate("/projects")
    } catch (err) {
      setMessage(err.message || "Login failed")
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-left">
        <div className="auth-brand">
          <span className="auth-brand-icon">⚡</span>
          <h2>Issue & Sprint Management</h2>
        </div>
        <p className="auth-tagline">Track issues, manage sprints and collaborate with your team in one place.</p>
        <div className="auth-illustration">
          <div className="illustration-box">
            <p>📋 Plan → 🔨 Build → ✅ Ship</p>
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-form-container">
          <h2 className="auth-title">Welcome Back</h2>
          <p className="auth-subtitle">Sign in to your account</p>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              className={`form-input ${errors.email ? "input-error" : ""}`}
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
            {errors.email && <p className="error-text">{errors.email}</p>}
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="pw-input-wrapper">
              <input
                className={`form-input ${errors.password ? "input-error" : ""}`}
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
              <span className="pw-eye" onClick={() => setShowPassword(p => !p)}>
                <EyeIcon open={showPassword} />
              </span>
            </div>
            {errors.password && <p className="error-text">{errors.password}</p>}
          </div>

          <button className="auth-btn" onClick={handleLogin}>Sign In</button>

          {message && <p className="auth-message error-text">{message}</p>}

          <p className="auth-link">
            Don't have an account?{" "}
            <Link to="/register" className="auth-link-text">Create account</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage