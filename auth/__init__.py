from .tables import User, Scope
from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from commons import success_short, error_short, APIResponse 
from typing import Annotated, List
from .scopes import has_perm, AuthScope, scope_docs
import hashlib
import jwt
from pydantic import BaseModel

OSL_TOKEN = "28a42ae5c72119d32ba65399699c26b903ee4ffc431607997b92e02b0d246b5d"

router = APIRouter(prefix="/auth", tags=["auth"])
oauth = OAuth2PasswordBearer(tokenUrl="/auth/login")

class LoginForm(BaseModel):
    username: str
    password: str

@router.post("/signup", response_model=APIResponse)
async def create_user(form: LoginForm):
    user = User(username=form.username, password=form.password)
    try:
        await user.insert(user)
        return success_short()
    except:
        return error_short("user exists")

class LoginSuccessResponseForm(APIResponse):
    token_type: str
    access_token: str

login_responses = {
        200: {
            "description": "Successful Authentication",
            "model": LoginSuccessResponseForm
            },
        403: {
            "description": "Authentication Failure",
            "model": APIResponse
            }
        }

@router.post("/login", responses=login_responses)
async def login_user(form: Annotated[OAuth2PasswordRequestForm, Depends()]): 
    user = await User.select().where(User.username == form.username).first()
    if user is None:
        return error_short(detail="auth failure", code=403) 

    scopes = await Scope.select(Scope.scope).where(Scope.user.username == form.username)
    scopes = [scope["scope"] for scope in scopes]

    token_data = {
            "username": form.username,
            "scopes": scopes,
            }
    # TODO: Set iat and exp token
    token = jwt.encode(token_data, OSL_TOKEN)
    return success_short(token_type="bearer", access_token=token, **token_data)

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

@router.get("/scopes")
async def handle_auth_scopes(token: TokenData = Depends(token_data)):
    return token.scopes
