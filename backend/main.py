from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from tasks import process_rag_query
import redis.asyncio as redis
import asyncio
import json
from contextlib import asynccontextmanager

connections = {}
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client
    redis_client = await redis.from_url("redis://localhost:6379")
    print("✅ Redis client connected")
    
    yield
    
    # Shutdown
    if redis_client: #Close redis before shutting down
        await redis_client.close()
        print("❌ Redis client closed")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

async def listen_for_result_with_progress(client_id: str, task_id: str, timeout: int = 300):
    """Listen for both progress updates AND final result"""
    pubsub = redis_client.pubsub()
    # Subscribe to both progress and result channels
    await pubsub.subscribe(f"task_progress:{task_id}", f"task_result:{task_id}")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        async for message in pubsub.listen():
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                if client_id in connections:
                    await connections[client_id].send_text(json.dumps({
                        "type": "error",
                        "message": "Task timeout"
                    }))
                break
            
            if message["type"] == "message":
                data = json.loads(message["data"])
                
                # Send update to frontend
                if client_id in connections:
                    # Determine message type
                    if "result" in data:
                        # Final result
                        await connections[client_id].send_text(json.dumps({
                            "type": "result",
                            "message": data["result"]
                        }))
                        break  # Stop listening after final result
                    elif "status" in data:
                        # Progress update
                        await connections[client_id].send_text(json.dumps({
                            "type": "progress",
                            "status": data["status"],
                            "message": data["message"]
                        }))
                        
    finally:
        await pubsub.unsubscribe(f"task_progress:{task_id}", f"task_result:{task_id}")
        await pubsub.close()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connections[client_id] = websocket
    print(f"✅ Client {client_id} connected")
    
    try:
        while True:
            # Wait for question from client
            question = await websocket.receive_text()
            print(f"📩 Received from {client_id}: {question}")
            
            # Send task to Celery
            celery_result = process_rag_query.delay(client_id, question)
            print(f"🚀 Task queued with ID: {celery_result.id}")
            
            # Listen for progress updates and final result
            await listen_for_result_with_progress(client_id, celery_result.id)
            print(f"✅ Task {celery_result.id} completed for {client_id}")

    except WebSocketDisconnect:
        print(f"❌ Client {client_id} disconnected")
    finally:
        if client_id in connections:
            del connections[client_id]

@app.get("/")
async def root():
    return {"message": "WebSocket RAG Server is running"}