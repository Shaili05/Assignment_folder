import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { registerUser } from "../services/api"
import { validateRegister } from "../utils/validations"
import "./register-page.css"

function RegisterPage() {
  const navigate = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
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
      await registerUser({ name, email, password: encodedPassword })
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