# TO BE DELETED
# NON ESSENTIAL POC

import pika
import uuid
import json
from asyncio import Event, Future, wait_for
from typing import Dict
import time
from threading import Thread

class AgentRPCController():
    def __init__(self, pika_connection: pika.BlockingConnection) -> None:
        self.connection = pika_connection
        self.correlations: Dict[str, Future] = {}

        self.channel = self.connection.channel()
        self.recv_queue = self.channel.queue_declare("", exclusive=True)
        self.channel.queue_bind(self.recv_queue.method.queue, "control-exchange", routing_key=self.recv_queue.method.queue)
        self.channel.basic_consume(
                self.recv_queue.method.queue,
                self._on_recv
                )

    def _on_recv(self, channel: pika.channel.Channel, spec: pika.spec.Basic.Deliver, props: pika.spec.BasicProperties, data: bytes):
        print(f"Message received: {data.decode()}")
        print(self.correlations.keys())
        if (props.correlation_id not in self.correlations):
            print("WRN unrelated function received")
            return

        try:
            string_data = data.decode()
            json_data = json.loads(string_data)
            self.correlations[props.correlation_id].set_result(json_data)
        except Exception as e:
            self.correlations[props.correlation_id].set_exception(e)
        print(f"Completed {props.correlation_id}")

    async def Ping(self, agent: str):
        corr_id = uuid.uuid4().hex
        data = {
                "Cmd": "ping",
                "Arg": {}
                }
        json_data = json.dumps(data)
        self.correlations[corr_id] = Future()
        
        self.channel.basic_publish("control-exchange", agent, json_data.encode(), pika.spec.BasicProperties(
            correlation_id=corr_id,
            reply_to=self.recv_queue.method.queue
            ))
        print(f"Ping sent off! {corr_id}")

        try:
            status = await wait_for(self.correlations[corr_id], 5)
            return status
        finally:
            self.correlations.pop(corr_id)


####

from fastapi import FastAPI

credentials = pika.PlainCredentials("default", "password")
parameters = pika.ConnectionParameters(
        host="127.0.0.1",
        credentials=credentials
        )
connection = pika.BlockingConnection(parameters)

app = FastAPI()
rpc_client = AgentRPCController("agent-1", connection)


@app.get("/")
async def handle_get_index():
    try:
        response = await rpc_client.Ping()
    except TimeoutError:
        return {"status": "timeout"}


    return dict(status="success", response=response)
