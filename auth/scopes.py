from typing import List


class Permission:
    ADMIN = "su:adm"
    SERVER_CREATE = "server:create"
    SERVER_DELETE = "server:delete"
    SERVER_MANUAL_ASSIGN = "server:manual_assign"
    AGENT_CREATE = "agent:create"
    AGENT_DELETE = "agent:delete"
    AGENT_LIST = "agent:list"


scope_docs = {
    Permission.ADMIN: "Super user permissions",
    Permission.SERVER_CREATE: "Create servers",
    Permission.SERVER_DELETE: "Delete servers you do not own",
    Permission.SERVER_MANUAL_ASSIGN: "Manually assign agent to server",
    Permission.AGENT_CREATE: "Create agent login tokens",
    Permission.AGENT_LIST: "List all available agents",
    Permission.AGENT_DELETE: "Delete agent login tokens",
}
