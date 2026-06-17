from typing import List

class _SU:
    ADMIN = "su:adm"
    
class _User:
    CREATE_SERVER = "user:server:create"

class AuthScope:
    Admin = _SU
    User = _User

scope_docs = {
        "su:adm": "Admin scopes, grants permissions for everything.",
        "user:server:create": "Permission to create servers"
        }

def has_perm(scope: str, granted: List[str]):
    if AuthScope.Admin.ADMIN in granted:
        return True
    return scope in granted
