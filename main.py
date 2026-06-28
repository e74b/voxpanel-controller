from fastapi import FastAPI, Depends
from fastapi.routing import Mount
from contextlib import asynccontextmanager
import aio_pika

from auth import router as auth_router
from server import router as server_router
from agents import router as agent_router

from server import setup_server
from auth import oauth
from agents import agent_login_handler

from piccolo_admin.endpoints import create_admin
from piccolo.engine import engine_finder
import asyncio

async def database_connection_test():
    engine = engine_finder()
    await engine.start_connection_pool()

async def lifespan(app: FastAPI):
    await database_connection_test()
    await setup_server()
    asyncio.create_task(agent_login_handler())
    yield


from auth import User, Scope
from server import Server

routes = [
    Mount(
        path="/admin",
        app=create_admin(tables=[User, Scope, Server], site_name="Piccolo Admin"),
    )
]

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(server_router)
app.include_router(agent_router)
