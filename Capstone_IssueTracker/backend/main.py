from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, projects, issues, sprints
import os
from services.user_service import register_user, get_user_by_email
from schemas.user_schema import UserRegister, UserRole
import base64


app = FastAPI(
    title="Issue & Sprint Management System",
    description="A Jira-like project management API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def seed_default_admin():
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
    admin_name = os.getenv("DEFAULT_ADMIN_NAME", "Platform Admin")

    if not admin_email or not admin_password:
        print("WARNING: DEFAULT_ADMIN_EMAIL / DEFAULT_ADMIN_PASSWORD not set in .env — skipping admin seed.")
        return

    existing = get_user_by_email(admin_email)
    if existing:
        return

    admin_payload = UserRegister(
        name=admin_name,
        email=admin_email,
        password=base64.b64encode(admin_password.encode()).decode(),
        role=UserRole.admin
    )
    register_user(admin_payload)
    print(f"Default admin seeded: {admin_payload.email}")

    
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(issues.router)
app.include_router(sprints.router)

@app.get("/")
def health_check():
    return {"status": "running", "message": "Issue Tracker API is up"}