import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { loginUser } from "../services/api"
import { validateLogin } from "../utils/validations"
import "./login-page.css"

function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState("")

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
      navigate("/dashboard")
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
            <input
              className={`form-input ${errors.password ? "input-error" : ""}`}
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
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