from rpc_client import RPCClient

class AgentRPCController(RPCClient):
    RPC_EXCHANGE = "control-exchange"
    RPC_QUEUE = "control"
    def __init__(self):
        super().__init__()
    async def Ping(self, agent: str, timeout = 5):
        return await self._request(agent, "ping", {})

    async def GetRunning(self, agent: str, timeout=5):
        return await self._request(agent, "get_running", {}, timeout=timeout)

    async def StartServer(self, agent: str, uuid: str, timeout=5):
        return await self._request(agent, "start_server", {
            "uuid": uuid
            })
        
    async def StopServer(self, agent: str, id, timeout = 15):
        return await self._request(agent, "stop_server", {
            "id": id
            })




