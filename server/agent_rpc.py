from ipc import IPCEngine
from aio_pika import ExchangeType


class AgentRPCController:
    def __init__(self):
        self.engine = IPCEngine()
        super().__init__()

    async def setup(self):
        await self.engine.setup("amqp://default:password@127.0.0.1")
        self.exchange = await self.engine.channel.declare_exchange(
            "control", type=ExchangeType.TOPIC, durable=True
        )
        await self.engine.setup_bindings(self.exchange)

    async def StartServer(self, queue: str, uuid: str, timeout=5):
        return await self.engine.rpc(
            "start_server", {"uuid": uuid}, queue, self.exchange
        )

        return await self._request(agent, "start_server", {"uuid": uuid})

    async def StopServer(self, queue: str, id, timeout=15):
        return await self.engine.rpc("stop_server", {"id": id}, queue, self.exchange)
