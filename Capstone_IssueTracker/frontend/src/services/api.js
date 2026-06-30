import { _get, _post } from "./api-manager"

export async function registerUser(name, email, password) {
  return _post("/users/register", { name, email, password })
}

export async function loginUser(email, password) {
  return _post("/users/login", { email, password })
}

export async function getProjects(token) {
  return _get("/projects/", token)
}

export async function createProject(data, token) {
  return _post("/projects/", data, token)
}