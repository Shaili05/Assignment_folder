const BASE_URL = import.meta.env.VITE_API_BASE_URL

function getToken() {
  return localStorage.getItem("token")
}

async function handleResponse(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong")
  }
  return data
}

export async function _get(endpoint, requireAuth = false) {
  const headers = {}
  if (requireAuth) {
    headers.Authorization = `Bearer ${getToken()}`
  }
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "GET",
    headers
  })
  return handleResponse(response)
}

export async function _post(endpoint, body, requireAuth = false) {
  const headers = { "Content-Type": "application/json" }
  if (requireAuth) {
    headers.Authorization = `Bearer ${getToken()}`
  }
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  })
  return handleResponse(response)
}

export async function _delete(endpoint, requireAuth = false) {
  const headers = {}
  if (requireAuth) {
    headers.Authorization = `Bearer ${getToken()}`
  }
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "DELETE",
    headers
  })
  return handleResponse(response)
}

export async function _patch(endpoint, body, requireAuth = false) {
  const headers = { "Content-Type": "application/json" }
  if (requireAuth) {
    headers.Authorization = `Bearer ${getToken()}`
  }
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "PATCH",
    headers,
    body: JSON.stringify(body)
  })
  return handleResponse(response)
}