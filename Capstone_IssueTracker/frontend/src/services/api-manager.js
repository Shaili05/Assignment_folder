const BASE_URL = import.meta.env.VITE_API_BASE_URL

async function handleResponse(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong")
  }
  return data
}

export async function _get(endpoint, token) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "GET",
    headers
  })
  return handleResponse(response)
}

export async function _post(endpoint, body, token) {
  const headers = { "Content-Type": "application/json" }
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  })
  return handleResponse(response)
}

export async function _delete(endpoint, token) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "DELETE",
    headers
  })
  return handleResponse(response)
}