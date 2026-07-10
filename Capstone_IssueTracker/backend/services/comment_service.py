from fastapi import HTTPException
from database import db
from models.comment_model import comment_helper, create_comment_document
from bson import ObjectId

comments_collection = db["comments"]
issues_collection = db["issues"]
users_collection = db["users"]

def add_comment(issue_id: str, content: str, author_id: str):
    try:
        issue = issues_collection.find_one({"_id": ObjectId(issue_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid issue_id format")

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    try:
        user = users_collection.find_one({"_id": ObjectId(author_id)})
    except Exception:
        user = None
    author_name = user["name"] if user else "Unknown User"

    comment_doc = create_comment_document(issue_id, author_id, author_name, content)
    result = comments_collection.insert_one(comment_doc)
    new_comment = comments_collection.find_one({"_id": result.inserted_id})
    return comment_helper(new_comment)

def get_comments_for_issue(issue_id: str):
    comments = comments_collection.find({"issue_id": issue_id}).sort("created_at", 1)
    return [comment_helper(c) for c in comments]

def update_comment(comment_id: str, content: str, current_user_id: str):
    try:
        comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid comment_id format")

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment["author_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own comments")

    comments_collection.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": {"content": content}}
    )
    updated = comments_collection.find_one({"_id": ObjectId(comment_id)})
    return comment_helper(updated)

def delete_comment(comment_id: str, current_user_id: str, current_user_role: str):
    try:
        comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid comment_id format")

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment["author_id"] != current_user_id and current_user_role != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own comments")

    comments_collection.delete_one({"_id": ObjectId(comment_id)})
    return {"message": "Comment deleted successfully"}