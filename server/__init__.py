from fastapi import APIRouter, Depends, WebSocket
from asyncpg.exceptions import UniqueViolationError
from auth import TokenData, token_data, has_perm, AuthScope, User
from commons import success_short, error_short, APIResponse
from .tables import Server
from uuid import uuid4
from .agent_rpc import AgentRPCController
import aio_pika
from pydantic import BaseModel
from typing import List
from agents import agent_pool
from .log_streaming import LogStreamManager

class State:
    STOPPING = "stopping"
    STOPPED = "offline"
    STARTING = "starting"
    STARTED = "online"

router = APIRouter(prefix="/server", tags=["server"])
rpc = AgentRPCController()
streams = LogStreamManager()

async def setup_server():
    connection = await aio_pika.connect_robust("amqp://default:password@127.0.0.1/")
    await rpc.setup(connection)
    await streams.setup()

@router.post("/create")
async def handle_server_create(slug: str, data: TokenData = Depends(token_data)):
    if not has_perm(AuthScope.User.CREATE_SERVER, data.scopes):
        return error_short("permission not granted", 403)
    user = await User.objects().where(User.username == data.username).first()
    server = Server(slug=slug, uuid=uuid4(), owner=user)
    try:
        await Server.insert(server)
    except:
        return error_short("server with slug aldready exists", 403)

    return success_short("server created successfully")

class ServerListInfo(BaseModel):
    slug: str
    state: str
    uuid: str

class ServerListResponse(APIResponse):
    data: List[ServerListInfo]

server_list_responses = {
        200: {
            "description": "List servers current user owns and their current states",
            "model": ServerListResponse
            }
        }

@router.get("/list", responses=server_list_responses)
async def handle_server_list(data: TokenData = Depends(token_data)):
    servers = await Server.select(
            Server.slug,
            Server.state,
            Server.uuid
            ).where(Server.owner.username == data.username)
    return success_short(data=servers)

server_start_responses = {
        200: {
            "description": "Success",
            "model": APIResponse
            },
        403: {
            "description": "Invalid Permissions",
            "model": APIResponse
            },
        404: {
            "description": "Server not found",
            "model": APIResponse
            },
        409: {
            "description": "Invalid server state",
            "model": APIResponse
            }
        }

@router.post("/start", responses=server_start_responses)
async def handle_server_start(slug: str, data: TokenData = Depends(token_data)):
    server = await Server.select(Server.uuid, Server.state, Server.owner.username).where(Server.slug == slug).first()
    if server is None:
        return error_short("server not found", 404)
    if not (server["owner.username"] == data.username):
        return error_short("you do not own this server", 403)
    if (server["state"] != State.STOPPED):
        return error_short("server aldready starting, started or offline", 409)
    agent = agent_pool.allocate()
    response = await rpc.StartServer(agent.rpc_queue, server["uuid"].hex)
    run_id = response["ID"]


    await Server.update(state = State.STARTING, run_id = run_id).where(
            Server.slug == slug,
            )
    try:
        return success_short("server starting", response=response)
    except TimeoutError:
        return error_short("move to websocket channel", code=206, channel_id="TODO")


@router.post("/stop")
async def handle_server_stop(slug: str, data: TokenData = Depends(token_data)):
    server = await Server.select(
            Server.run_id,
            Server.owner.username
            ).where(Server.slug == slug).first()
    if server is None:
        return error_short("server not found", 404)
    if not (server["owner.username"] == data.username):
        return error_short("you do not own this server", 403)
    await Server.update(state = State.STOPPED, run_id = None).where(
            Server.slug == slug
            )
    try:
        response = await rpc.StopServer("start." + server["run_id"], server["run_id"])
        return success_short("server stopped", response = response)
    except TimeoutError:
        return error_short("move to websocket channel", code=206, channel_id="TODO")

@router.websocket("/logs")
async def handle_logs(run_id: str, ws: WebSocket):
    await ws.accept()
    sub = await streams.subscribe("run." + run_id)
    while True:
        text = await sub.wait()
        await ws.send_text(text)

    await ws.close()
