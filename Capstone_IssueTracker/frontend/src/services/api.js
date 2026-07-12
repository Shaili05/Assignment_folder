import { _get, _post, _patch } from "./api-manager"

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

export async function getIssues(projectId) {
  return _get(`/issues/project/${projectId}`, true)
}

export async function createIssue(payload) {
  return _post("/issues/", payload, true)
}

export async function updateIssueStatus(issueId, status) {
  return _patch(`/issues/${issueId}/status`, { status }, true)
}