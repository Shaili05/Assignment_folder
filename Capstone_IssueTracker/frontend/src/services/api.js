import { _get, _post } from "./api-manager"

export async function registerUser(payload) {
  return _post("/users/register", payload)
}

export async function loginUser(payload) {
  return _post("/users/login", payload)
}

export async function getProjects() {
  return _get("/projects/", true)
}

export async function createProject(payload) {
  return _post("/projects/", payload, true)
}