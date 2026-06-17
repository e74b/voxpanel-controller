import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from asyncio import Future
import asyncio
import uuid
import json
import time
from typing import Dict

class RPCClient:

    open_requests: Dict[str, Future] = {}
    RPC_EXCHANGE: str
    RPC_QUEUE: str

    async def setup(self, connection: AbstractRobustConnection):
        self.connection = connection
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(self.RPC_EXCHANGE)
        self.recv_queue = await self.channel.declare_queue("", exclusive=True)

        self.control = await self.channel.declare_queue(self.RPC_QUEUE, durable=True, arguments={ "x-message-ttl": 0 })
        await self.control.bind(self.RPC_EXCHANGE)
        await self.recv_queue.bind(self.RPC_EXCHANGE, self.recv_queue.name)
        await self.recv_queue.consume(self._on_message, no_ack=True)

    async def _on_message(self, message: AbstractIncomingMessage):
        if message.correlation_id not in self.open_requests:
            print("WRN: Received message with unrelated correleation id")
            print(message.body.decode())
            return
        if self.open_requests[message.correlation_id].done():
            return
        try:
            str_message = message.body.decode()
            dict_message: dict= json.loads(str_message)
            self.open_requests[message.correlation_id].set_result(dict_message)
        except Exception as e:
            self.open_requests[message.correlation_id].set_exception(e)

    async def _request(self, agent: str, command: str, arguments: dict, timeout = 5):
        correlation_id = uuid.uuid4().hex
        self.open_requests[correlation_id] = Future()

        body = {
                "Cmd": command,
                "Arg": arguments
                }
        message = aio_pika.Message(
                body = json.dumps(body).encode(),
                correlation_id=correlation_id,
                reply_to=self.recv_queue.name,
                headers={"x-message-ttl": 0}
                )
        await self.exchange.publish(message, agent)

        try:
            result = await asyncio.wait_for(self.open_requests[correlation_id], timeout)
            isComplete = result.get("Complete", True)
            # Just to get around timeouts for slow operations
            if not isComplete:
                print("Waiting for slow request.")
                self.open_requests[correlation_id] = Future()
                start = time.perf_counter()
                slow_result = await self.open_requests[correlation_id]
                stop = time.perf_counter()

                return {**slow_result, "time": stop - start}
        finally:
            self.open_requests.pop(correlation_id)

        return result


