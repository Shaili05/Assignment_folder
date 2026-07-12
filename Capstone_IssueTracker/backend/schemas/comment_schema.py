from pydantic import BaseModel

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: str
    issue_id: str
    author_id: str
    author_name: str
    content: str
    created_at: str