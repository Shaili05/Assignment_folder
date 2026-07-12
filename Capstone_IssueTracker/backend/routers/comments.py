from fastapi import APIRouter, Depends
from schemas.comment_schema import CommentCreate, CommentResponse
from services.comment_service import add_comment, get_comments_for_issue, update_comment, delete_comment
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/issues", tags=["Comments"])

@router.post("/{issue_id}/comments", response_model=CommentResponse)
def create_comment(issue_id: str, body: CommentCreate, current_user: dict = Depends(get_current_user)):
    return add_comment(
        issue_id,
        body.content,
        current_user.get("user_id")
    )

@router.get("/{issue_id}/comments")
def list_comments(issue_id: str, current_user: dict = Depends(get_current_user)):
    return get_comments_for_issue(issue_id)

@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def edit_comment(comment_id: str, body: CommentCreate, current_user: dict = Depends(get_current_user)):
    return update_comment(comment_id, body.content, current_user.get("user_id"))

@router.delete("/comments/{comment_id}")
def remove_comment(comment_id: str, current_user: dict = Depends(get_current_user)):
    return delete_comment(comment_id, current_user.get("user_id"), current_user.get("role"))