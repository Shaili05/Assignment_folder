import { useState, useEffect } from "react"
import { getProjects, createProject } from "../services/api"

function ProjectsPage({ onNavigate }) {
  const [projects, setProjects] = useState([])
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [projectKey, setProjectKey] = useState("")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProjects()
  }, [])

  async function fetchProjects() {
    const token = localStorage.getItem("token")
    const result = await getProjects(token)
    if (Array.isArray(result)) {
      setProjects(result)
    }
    setLoading(false)
  }

  async function handleCreate() {
    const token = localStorage.getItem("token")
    const result = await createProject({ name, description, project_key: projectKey }, token)
    if (result.id) {
      setMessage("Project created successfully!")
      setName("")
      setDescription("")
      setProjectKey("")
      fetchProjects()
    } else {
      setMessage(result.detail || "Failed to create project")
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>Projects</h2>
        <button style={styles.logoutBtn} onClick={() => {
          localStorage.removeItem("token")
          onNavigate("login")
        }}>Logout</button>
      </div>

      <div style={styles.form}>
        <h3>Create New Project</h3>
        <input style={styles.input} placeholder="Project Name" value={name} onChange={e => setName(e.target.value)} />
        <input style={styles.input} placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} />
        <input style={styles.input} placeholder="Project Key (e.g. PROJ)" value={projectKey} onChange={e => setProjectKey(e.target.value)} />
        <button style={styles.button} onClick={handleCreate}>Create Project</button>
        {message && <p style={styles.message}>{message}</p>}
      </div>

      <div style={styles.list}>
        <h3>All Projects</h3>
        {loading ? <p>Loading...</p> : projects.length === 0 ? <p>No projects yet.</p> : (
          projects.map(project => (
            <div key={project.id} style={styles.card}>
              <strong>{project.name}</strong>
              <span style={styles.key}>[{project.project_key}]</span>
              <p>{project.description}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

const styles = {
  container: { maxWidth: "800px", margin: "0 auto", padding: "20px" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" },
  form: { backgroundColor: "#fff", padding: "20px", borderRadius: "8px", boxShadow: "0 2px 10px rgba(0,0,0,0.1)", marginBottom: "20px", display: "flex", flexDirection: "column", gap: "10px" },
  input: { padding: "10px", borderRadius: "4px", border: "1px solid #ccc", fontSize: "14px" },
  button: { padding: "10px", backgroundColor: "#4f46e5", color: "#fff", border: "none", borderRadius: "4px", fontSize: "16px", cursor: "pointer" },
  logoutBtn: { padding: "8px 16px", backgroundColor: "#ef4444", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" },
  message: { color: "green", textAlign: "center" },
  list: { backgroundColor: "#fff", padding: "20px", borderRadius: "8px", boxShadow: "0 2px 10px rgba(0,0,0,0.1)" },
  card: { padding: "12px", borderBottom: "1px solid #eee", display: "flex", gap: "10px", alignItems: "center" },
  key: { backgroundColor: "#e0e7ff", color: "#4f46e5", padding: "2px 8px", borderRadius: "4px", fontSize: "12px" }
}

export default ProjectsPage