import { useState } from "react"
import { registerUser } from "../services/api"

function RegisterPage({ onNavigate }) {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [message, setMessage] = useState("")

  async function handleRegister() {
    const result = await registerUser(name, email, password)
    if (result.id) {
      setMessage("Registration successful! Please login.")
    } else {
      setMessage(result.detail || "Registration failed")
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Create Account</h2>
        <input
          style={styles.input}
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          style={styles.input}
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          style={styles.input}
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button style={styles.button} onClick={handleRegister}>
          Register
        </button>
        {message && <p style={styles.message}>{message}</p>}
        <p style={styles.link}>
          Already have an account?{" "}
          <span style={styles.linkText} onClick={() => onNavigate("login")}>
            Login
          </span>
        </p>
      </div>
    </div>
  )
}

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#f0f2f5"
  },
  card: {
    backgroundColor: "#fff",
    padding: "40px",
    borderRadius: "8px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
    width: "360px",
    display: "flex",
    flexDirection: "column",
    gap: "16px"
  },
  title: {
    textAlign: "center",
    color: "#333"
  },
  input: {
    padding: "10px",
    borderRadius: "4px",
    border: "1px solid #ccc",
    fontSize: "14px"
  },
  button: {
    padding: "10px",
    backgroundColor: "#4f46e5",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    fontSize: "16px",
    cursor: "pointer"
  },
  message: {
    textAlign: "center",
    color: "green"
  },
  link: {
    textAlign: "center",
    fontSize: "14px"
  },
  linkText: {
    color: "#4f46e5",
    cursor: "pointer",
    fontWeight: "bold"
  }
}

export default RegisterPage