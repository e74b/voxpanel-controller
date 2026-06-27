from .tables import User, Scope
from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    SecurityScopes,
)
from fastapi.exceptions import HTTPException
from commons import success_short, error_short, APIResponse
from typing import Annotated, List
from .scopes import Permission, scope_docs
import hashlib
import jwt
from pydantic import BaseModel

OSL_TOKEN = "28a42ae5c72119d32ba65399699c26b903ee4ffc431607997b92e02b0d246b5d"

router = APIRouter(prefix="/auth", tags=["auth"])
oauth = OAuth2PasswordBearer(tokenUrl="/auth/login", scopes=scope_docs)

## PUT /signup


class SignupForm(BaseModel):
    username: str
    password: str


signup_responses = {
    201: {"description": "User successfully created", "model": APIResponse},
    409: {"description": "User aldready exists", "model": APIResponse},
}


@router.put("/signup", responses=signup_responses)
async def create_user(form: SignupForm):
    """Create a new user with no permissions."""
    user = User(username=form.username, password=form.password)
    try:
        await user.insert(user)
        return success_short(code=201)
    except:
        return error_short("user exists", code=409)


# POST /login


class LoginSuccessResponseForm(APIResponse):
    token_type: str
    access_token: str


login_responses = {
    200: {
        "description": "Successful Authentication",
        "model": LoginSuccessResponseForm,
    },
    403: {"description": "Authentication Failure", "model": APIResponse},
}


@router.post("/login", responses=login_responses)
async def login_user(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await User.select().where(User.username == form.username).first()
    if user is None:
        return error_short(detail="auth failure", code=403)

    scopes = await Scope.select(Scope.scope).where(Scope.user.username == form.username)
    requested_scopes = set(form.scopes)
    granted_scopes = {scope["scope"] for scope in scopes}

    token_data = {
        "username": form.username,
        "scopes": list(
            requested_scopes.intersection(granted_scopes)
        ),  # grant only what is given AND what is asked
    }
    # TODO: Set iat and exp token
    token = jwt.encode(token_data, OSL_TOKEN)
    return success_short(token_type="bearer", access_token=token, **token_data)


# GET /scopes


class TokenData:
    username: str
    scopes: List[str]

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def token_data(token: str = Depends(oauth)) -> TokenData:
    raw_data = jwt.decode(token, OSL_TOKEN, algorithms=["HS256"])
    data = TokenData(**raw_data)
    return data


def get_token(
    scopes: SecurityScopes, token: Annotated[TokenData, Depends(token_data)]
) -> TokenData:
    granted = set(token.scopes)
    required = set(scopes.scopes)

    if Permission.ADMIN in granted:
        return token

    if required.issubset(granted):
        return token
    else:
        raise HTTPException(403)


@router.get("/scopes")
async def handle_auth_scopes(token: TokenData = Depends(token_data)):
    return token.scopes
