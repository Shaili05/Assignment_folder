from src.config.constants import DEFAULT_ROLE, ROLES
from src.exceptions.exceptions import InvalidRoleError


def get_role(role):
    if role not in ROLES:
        raise InvalidRoleError(f"Unknown role '{role}'. Valid roles: {', '.join(ROLES)}")
    return ROLES[role]


def allowed_tools(role):
    return list(get_role(role)["tools"])


def can_call(role, tool_name):
    return tool_name in get_role(role)["tools"]


def audit_access(role):
    return get_role(role)["audit_view"]
