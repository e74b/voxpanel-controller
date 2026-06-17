from fastapi import FastAPI, Depends
from fastapi.routing import Mount
from contextlib import asynccontextmanager
import aio_pika

from auth import router as auth_router
from server import router as server_router
from server import setup_server
from auth import oauth

from piccolo_admin.endpoints import create_admin

async def lifespan(app: FastAPI):
    await setup_server()
    yield

from auth import User, Scope
from server import Server

routes = [
        Mount(path="/admin", app=create_admin(
            tables=[User, Scope, Server],
            site_name="Piccolo Admin"
            ))
        ]

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(server_router)

