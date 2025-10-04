from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


clients:dict[str,WebSocket] ={}

@app.websocket("/w/{client}")
async def websocket_endpoint(websocket:WebSocket,client):
    try:
           await websocket.accept()
           client_id = client
           clients[client_id]= websocket
           time_connected = time.time()
           message_by_user= await websocket.receive_text()
           print("The message by the user is ",message_by_user)
           print(f"client with client id {client_id} connected at {time_connected}" )
           print("All clients", list(clients.keys()))
           print("All websocket connections", list(clients.values()))
        
    except Exception as e:
        print("Disconnencted")    

        

