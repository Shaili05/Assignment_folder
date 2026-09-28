"""
roles.py

Mocked role-based access. A real deployment would read the role from a login,
here the dashboard passes it in. A role decides which tools the agent may call
and how much of the audit log the user can see.
"""

ALL_TOOLS = ["sentiment_trend", "flagged_reviews", "generate_summary_report", "search_reviews"]

ROLES = {
    "brand_manager": {
        "label": "Brand manager",
        "tools": ALL_TOOLS,
        "audit_view": "full",
        "can_draft_replies": True,
    },
    "support_team": {
        "label": "Support team",
        "tools": ["flagged_reviews", "search_reviews"],
        "audit_view": "own_summary",
        "can_draft_replies": True,
    },
}

DEFAULT_ROLE = "brand_manager"


def get_role(role):
    if role not in ROLES:
        raise ValueError(f"Unknown role '{role}'. Valid roles: {', '.join(ROLES)}")
    return ROLES[role]


def allowed_tools(role):
    return list(get_role(role)["tools"])


def can_call(role, tool_name):
    return tool_name in get_role(role)["tools"]


def audit_access(role):
    return get_role(role)["audit_view"]


