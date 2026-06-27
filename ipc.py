import aio_pika
import json
import uuid
import asyncio
from aio_pika.abc import (
    AbstractConnection,
    AbstractChannel,
    AbstractQueue,
    ExchangeType,
    AbstractExchange,
    AbstractIncomingMessage,
)
from pydantic import BaseModel
import logging
import time
import dataclasses


@dataclasses.dataclass()
class RpcState:
    deadline: int
    future: asyncio.Future


class IPCEngine:
    NAME = "rpc"  # name for logger
    connection: AbstractConnection
    channel: AbstractChannel
    rpc_queue: AbstractQueue
    rpc_state: dict[str, RpcState]
    logger: logging.Logger

    async def setup(self, connect_url: str):
        self.connection = await aio_pika.connect_robust(connect_url)
        self.channel = await self.connection.channel()
        self.rpc_queue = await self.channel.declare_queue(durable=True)
        self.rpc_state = {}
        self.logger = logging.getLogger(self.NAME)

    async def setup_bindings(self, exchange: AbstractExchange):
        self.control_exchange = exchange
        await self.rpc_queue.bind(self.control_exchange, self.rpc_queue.name)
        await self.rpc_queue.consume(self._rpc_recv)

    async def rpc(
        self,
        command: str,
        arguments: dict,
        routing: str,
        exchange: AbstractExchange,
        timeout=5,
    ):
        body = {"Cmd": command, "Arg": arguments}
        json_body = json.dumps(body)
        correlation_id = uuid.uuid4().hex
        print(self.rpc_queue.name)
        message = aio_pika.Message(
            body=json_body.encode(),
            reply_to=self.rpc_queue.name,
            correlation_id=correlation_id,
        )

        state = RpcState(future=asyncio.Future(), deadline=time.monotonic() + timeout)
        self.rpc_state[correlation_id] = state

        try:
            await exchange.publish(message, routing)
        except:
            self.rpc_state.pop(correlation_id)
            raise

        result = await asyncio.wait_for(
            self.rpc_state[correlation_id].future,
            self.rpc_state[correlation_id].deadline - time.monotonic(),
        )
        return result

    async def _rpc_recv(self, message: AbstractIncomingMessage):
        if message.correlation_id not in self.rpc_state:
            self.logger.warning(
                f"received invalid rpc response addrto={message.correlation_id}"
            )
            return

        future = self.rpc_state[message.correlation_id].future
        if future.done():
            self.logger.warning(
                f"received multiple responses for rpc req addrto={message.correlation_id}"
            )
            return

        is_meta = message.headers.get("x-meta", False)

        try:
            body = json.loads(message.body.decode())
        except json.JSONDecodeError:
            self.logger.error(
                f"failed to decode as json addrto={message.correlation_id}"
            )
            return

        if not is_meta:
            future.set_result(body)
            self.rpc_state.pop(message.correlation_id)
            return

        if not (("Cmd" in body) and ("Arg" in body)):
            self.logger.warning("received invalid meta message. ignoring")
            return

        if body["Cmd"] == "ttl-extend":
            if "time" not in body["Arg"]:
                self.logger.warning("no time parameter in ttl-extend. ignoring")
                return
            self.rpc_state[message.correlation_id].deadline += body["time"]
        else:
            self.logger.warning("unknown meta command")

    async def gather(self):
        raise NotImplementedError()

    async def stream(self):
        raise NotImplementedError()

    async def cleanup(self):
        await self.rpc_queue.delete()
        await self.channel.close()
        await self.connection.close()


async def rabbitmq_setup(rmq_url: str):
    connection = await aio_pika.connect_robust(rmq_url)
    channel = await connection.channel()

    await channel.declare_exchange("logs", ExchangeType.FANOUT)
    control_exchange = await channel.declare_exchange("control", ExchangeType.TOPIC)
    agent_global_messaging = await channel.declare_queue("", durable=True)
    await agent_global_messaging.bind(
        control_exchange, routing_key="control-global", arguments={"x-message-ttl": 60}
    )
    await channel.declare_exchange(
        "server", ExchangeType.DIRECT, arguments={"x-message-ttl": 60}
    )

    await channel.close()
    await connection.close()
