const BASE_URL = "http://localhost:8000/api"

export async function registerUser(name, email, password) {
  const response = await fetch(`${BASE_URL}/users/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password })
  })
  return response.json()
}

export async function loginUser(email, password) {
  const response = await fetch(`${BASE_URL}/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
  return response.json()
}

export async function getProjects(token) {
  const response = await fetch(`${BASE_URL}/projects/`, {
    headers: { "Authorization": `Bearer ${token}` }
  })
  return response.json()
}

export async function createProject(data, token) {
  const response = await fetch(`${BASE_URL}/projects/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
    body: JSON.stringify(data)
  })
  return response.json()
}