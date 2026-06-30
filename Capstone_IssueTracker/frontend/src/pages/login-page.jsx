import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { loginUser } from "../services/api"
import "./login-page.css"

function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState("")

  function validate() {
    const newErrors = {}

    if (!email.trim()) {
      newErrors.email = "Email is required."
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Enter a valid email address."
    }

    if (!password) {
      newErrors.password = "Password is required."
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleLogin() {
    setMessage("")
    if (!validate()) return

    try {
      const result = await loginUser(email, password)
      localStorage.setItem("token", result.access_token)
      navigate("/login")
    } catch (err) {
      setMessage(err.message || "Login failed")
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h2 className="login-title">Issue Tracker Login</h2>

        <div>
          <input
            className="login-input"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {errors.email && <p className="login-error-text">{errors.email}</p>}
        </div>

        <div>
          <input
            className="login-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {errors.password && <p className="login-error-text">{errors.password}</p>}
        </div>

        <button className="login-button" onClick={handleLogin}>Login</button>

        {message && <p className="login-message">{message}</p>}

        <p className="login-link">
          Don't have an account?{" "}
          <Link className="login-link-text" to="/register">Register</Link>
        </p>
      </div>
    </div>
  )
}

export default LoginPage