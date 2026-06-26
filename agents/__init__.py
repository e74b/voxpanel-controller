import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractChannel
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Security
from auth import TokenData, get_token, Permission
from typing import Annotated
from commons import error_short, success_short
from datetime import datetime
import secrets
from .tables import Agent

class LoginRequestPacket(BaseModel):
    Token: str

class LoginResponsePacket(BaseModel):
    Success: bool
    Name: str
    Queue: str

class ConnectedAgent:
    channel: AbstractChannel
    name: str
    rpc_queue: str

class PoolController:
    agents = []

    def append(self, node: ConnectedAgent):
        self.agents.append(node)

    def allocate(self) -> ConnectedAgent:
        # future resource based allocation may be done
        # for now it just returns the first item in the pool
        if len(self.agents) < 1:
            raise RuntimeError("No available agents")

        return self.agents[0]


agent_pool = PoolController()

async def login_callback(message: AbstractIncomingMessage):
    global agent_pool
    raw_message = message.body.decode()
    await message.ack()
    request = LoginRequestPacket.parse_raw(raw_message)
    agent = await Agent.objects().where(Agent.token == request.Token).first()
    if agent is None:
        print("Login denied")
        response = LoginResponsePacket(Success=False, Name="", Queue="")
        await message.channel.basic_publish(
                response.model_dump_json().encode(),
                routing_key=message.reply_to
                )
        return
    print(f"Logged in as {agent.agent_name}")
    queue = await message.channel.queue_declare(durable=True, auto_delete=True, exclusive=False)
    await message.channel.queue_bind(queue.queue, "control", queue.queue)
    response = LoginResponsePacket(Success=True, Name=agent.agent_name, Queue=queue.queue)

    await message.channel.basic_publish(
            response.model_dump_json().encode(),
            routing_key=message.reply_to
            )

    await Agent.update(last_ping=datetime.now()).where(Agent.token == request.Token)
    connected_agent = ConnectedAgent()
    connected_agent.name = agent.agent_name
    connected_agent.channel = await message.channel.connection.channel()
    connected_agent.rpc_queue = queue.queue
    agent_pool.append(connected_agent)

async def agent_login_handler():
    print("Starting login handler")
    connection = await aio_pika.connect_robust("amqp://default:password@127.0.0.1/")
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
            "formation",
            "fanout",
            durable=True,
            auto_delete=False,
            arguments={ "x-message-ttl": 0 }
            )
    queue = await channel.declare_queue("formation-control", durable=True)
    await queue.bind(exchange, "formation-control")
    print("reached consume")
    await queue.consume(login_callback)

router = APIRouter(prefix="/agents", tags=["agent"])

@router.put("/create")
async def handle_agent_create(agent_name: str, token: Annotated[TokenData, Security(get_token, scopes=[Permission.AGENT_CREATE])]):
    token = secrets.token_urlsafe(32)
    agent = Agent(agent_name=agent_name, token=token, last_ping=None)
    await Agent.insert(agent)

    return success_short("agent successfully created", token=token, agent_name=agent_name, code=201)
        

@router.get("/list")
async def handle_agent_list(token: Annotated[TokenData, Security(get_token, scopes=[Permission.AGENT_LIST])]):
    names = [ dict(name = agent["agent_name"], last_ping = agent["last_ping"])
            for agent in await Agent.select()]

    return names

