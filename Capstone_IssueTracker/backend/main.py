from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, projects, issues

app = FastAPI(
    title="Issue & Sprint Management System",
    description="A Jira-like project management API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(issues.router)

@app.get("/")
def health_check():
    return {"status": "running", "message": "Issue Tracker API is up"}