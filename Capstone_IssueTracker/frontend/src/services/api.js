import { _get, _post, _patch, _delete } from "./api-manager"

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


export async function getSprints(projectId) {
  return _get(`/sprints/project/${projectId}`, true)
}

export async function updateSprintStatus(sprintId, status) {
  return _patch(`/sprints/${sprintId}/status`, { status }, true)
}

export async function createSprint(payload) {
  return _post("/sprints/", payload, true)
}

export async function addIssueToSprint(sprintId, issueId) {
  return _post(`/sprints/${sprintId}/issues/${issueId}`, {}, true)
}


export async function getAllUsers() {
  return _get("/users/", true)
}

export async function updateUserRole(userId, role) {
  return _patch(`/users/${userId}/role`, { role }, true)
}

export async function getProjectMembers(projectId) {
  return _get(`/projects/${projectId}/members`, true)
}


export async function getMyIssues() {
  return _get("/issues/my-issues", true)
}

export async function reassignIssue(issueId, assigneeId) {
  return _patch(`/issues/${issueId}/assign`, { assignee_id: assigneeId }, true)
}


export async function addProjectMember(projectId, userId) {
  return _post(`/projects/${projectId}/members/${userId}`, {}, true)
}

export async function removeProjectMember(projectId, userId) {
  return _delete(`/projects/${projectId}/members/${userId}`, true)
}

export async function getProjectById(projectId) {
  return _get(`/projects/${projectId}`, true)
}

export async function updateProjectDescription(projectId, description) {
  return _patch(`/projects/${projectId}`, { description }, true)
}

export async function deleteProject(projectId) {
  return _delete(`/projects/${projectId}`, true)
}

export async function updateIssue(issueId, payload) {
  return _patch(`/issues/${issueId}`, payload, true)
}

export async function deleteIssue(issueId) {
  return _delete(`/issues/${issueId}`, true)
}

export async function updateSprint(sprintId, payload) {
  return _patch(`/sprints/${sprintId}`, payload, true)
}

export async function deleteSprint(sprintId) {
  return _delete(`/sprints/${sprintId}`, true)
}


export async function getAssignedCounts() {
  return _get("/issues/assigned-counts", true)
}

export async function deleteUser(userId) {
  return _delete(`/users/${userId}`, true)
}