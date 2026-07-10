from datetime import datetime

def comment_helper(comment) -> dict:
    return {
        "id": str(comment["_id"]),
        "issue_id": comment["issue_id"],
        "author_id": comment["author_id"],
        "author_name": comment.get("author_name", "Unknown"),
        "content": comment["content"],
        "created_at": comment["created_at"]
    }

def create_comment_document(issue_id: str, author_id: str, author_name: str, content: str) -> dict:
    return {
        "issue_id": issue_id,
        "author_id": author_id,
        "author_name": author_name,
        "content": content,
        "created_at": datetime.utcnow().isoformat()
    }