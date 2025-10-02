
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from redis_connection import redis_client
from contextlib import asynccontextmanager

connections = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(result_listener())
    try:
        yield
    finally:
        task.cancel()
        await task

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

async def result_listener():
    loop = asyncio.get_event_loop()
    print("Result listener started")  # Add this line
    while True:
        try:  # Add try-except block
            task_data = await loop.run_in_executor(None, lambda: redis_client.blpop("ready_tasks", timeout=0))
            if task_data:
                _, result_json = task_data
                result = json.loads(result_json)
                client_id = result["client_id"]
                message = result["result"]
                print(f"Received result for client {client_id}: {message}")  # Add this line

                if client_id in connections:
                    try:
                        await connections[client_id].send_text(message)
                        print(f"Sent message to client {client_id}")  # Add this line
                    except Exception as e:
                        print(f"Error sending to client {client_id}: {str(e)}")  # Add this line
                        del connections[client_id]
                else:
                    print(f"Client {client_id} not found in connections")  # Add this line
        except Exception as e:
            print(f"Error in result listener: {str(e)}")  # Add this line

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            task = {"client_id": client_id, "payload": data}
            redis_client.rpush("tasks", json.dumps(task))
            await websocket.send_text("Task received and queued")
    except WebSocketDisconnect:
        del connections[client_id]

