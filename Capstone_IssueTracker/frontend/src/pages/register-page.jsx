import { useState } from "react"
import { Link } from "react-router-dom"
import { registerUser } from "../services/api"
import "./register-page.css"

function RegisterPage() {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [errors, setErrors] = useState({})
  const [message, setMessage] = useState("")

  function validate() {
    const newErrors = {}

    if (!name.trim()) {
      newErrors.name = "Full name is required."
    }

    if (!email.trim()) {
      newErrors.email = "Email is required."
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Enter a valid email address."
    }

    if (!password) {
      newErrors.password = "Password is required."
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters long."
    } else if (!/[A-Z]/.test(password)) {
      newErrors.password = "Password must contain one uppercase letter."
    } else if (!/[a-z]/.test(password)) {
      newErrors.password = "Password must contain one lowercase letter."
    } else if (!/[0-9]/.test(password)) {
      newErrors.password = "Password must contain one digit."
    } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      newErrors.password = "Password must contain one special character."
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleRegister() {
    setMessage("")
    if (!validate()) return

    try {
      await registerUser(name, email, password)
      setMessage("Registration successful! Please login.")
      setName("")
      setEmail("")
      setPassword("")
    } catch (err) {
      setMessage(err.message || "Registration failed")
    }
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <h2 className="register-title">Create Account</h2>

        <div>
          <input
            className={`register-input ${errors.name ? "register-input-error" : ""}`}
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          {errors.name && <p className="register-error-text">{errors.name}</p>}
        </div>

        <div>
          <input
            className={`register-input ${errors.email ? "register-input-error" : ""}`}
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {errors.email && <p className="register-error-text">{errors.email}</p>}
        </div>

        <div>
          <input
            className={`register-input ${errors.password ? "register-input-error" : ""}`}
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {errors.password && <p className="register-error-text">{errors.password}</p>}
        </div>

        <button className="register-button" onClick={handleRegister}>Register</button>

        {message && <p className="register-message">{message}</p>}

        <p className="register-link">
          Already have an account?{" "}
          <Link className="register-link-text" to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}

export default RegisterPage