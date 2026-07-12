from datetime import datetime

def sprint_helper(sprint) -> dict:
    return {
        "id": str(sprint["_id"]),
        "name": sprint["name"],
        "project_id": sprint["project_id"],
        "goal": sprint.get("goal", ""),
        "status": sprint["status"],
        "start_date": sprint.get("start_date"),
        "end_date": sprint.get("end_date"),
        "issues": sprint.get("issues", [])
    }

def create_sprint_document(name: str, project_id: str, goal: str, start_date: str, end_date: str) -> dict:
    return {
        "name": name,
        "project_id": project_id,
        "goal": goal,
        "status": "planned",
        "start_date": start_date,
        "end_date": end_date,
        "issues": [],
        "created_at": datetime.utcnow()
    }