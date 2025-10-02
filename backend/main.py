from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from tasks import process_task
import asyncio

connections = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connections[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            # Send task to Celery
            celery_result = process_task.delay(client_id, data)
            await websocket.send_text("Task received and queued")

            # Optionally, poll for result (or use a separate listener)
            while not celery_result.ready():
                await asyncio.sleep(0.5)
            result = celery_result.result
            if client_id in connections:
                await connections[client_id].send_text(result["result"])
    except WebSocketDisconnect:
        del connections[client_id]
