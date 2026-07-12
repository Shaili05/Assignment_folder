# Project model - defines how project data is stored and retrieved from MongoDB

def project_helper(project) -> dict:
    """Convert MongoDB project document to a clean dictionary"""
    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "description": project["description"],
        "project_key": project["project_key"],
        "members": project.get("members", []),
        "owner_id": project["owner_id"]
    }

def create_project_document(name: str, description: str, project_key: str, members: list, owner_id: str) -> dict:
    """Create a new project document for MongoDB"""
    return {
        "name": name,
        "description": description,
        "project_key": project_key,
        "members": members,
        "owner_id": owner_id
    }