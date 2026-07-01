from datetime import datetime

def issue_helper(issue) -> dict:
    return {
        "id": str(issue["_id"]),
        "title": issue["title"],
        "description": issue.get("description", ""),
        "issue_type": issue["issue_type"],
        "priority": issue["priority"],
        "status": issue["status"],
        "project_id": issue["project_id"],
        "assignee_id": issue.get("assignee_id"),
        "created_by": issue["created_by"]
    }

def create_issue_document(title: str, description: str, issue_type: str,
                           priority: str, project_id: str,
                           assignee_id: str, created_by: str) -> dict:
    return {
        "title": title,
        "description": description,
        "issue_type": issue_type,
        "priority": priority,
        "status": "BACKLOG",
        "project_id": project_id,
        "assignee_id": assignee_id,
        "created_by": created_by,
        "created_at": datetime.utcnow()
    }