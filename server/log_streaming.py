import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractIncomingMessage
from asyncio import Queue
from config import RMQ_URL


class LogSubscription:
    channel: AbstractChannel
    queue: Queue

    async def setup(self, queue):
        self.queue = Queue()
        queue = await self.channel.get_queue(queue)
        await queue.consume(self._on_message)

    async def _on_message(self, message: AbstractIncomingMessage):
        line = message.body.decode()
        await self.queue.put(line)

    async def wait(self) -> str:
        return await self.queue.get()


class LogStreamManager:
    connection: AbstractConnection = None  # Make connection a static variable

    async def setup(self):
        self.connection = await aio_pika.connect_robust(RMQ_URL)

    async def subscribe(self, queue) -> LogSubscription:
        subscription = LogSubscription()
        subscription.channel = await self.connection.channel()
        await subscription.setup(queue)
        return subscription
