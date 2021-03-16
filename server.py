from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/index.html")
async def index():
		return HTMLResponse(open('./index.html', 'r').read())

@app.get("/chatroom.html")
async def chat():
		return HTMLResponse(open('./chatroom.html', 'r').read())

class ConnectionManager:
		def __init__(self):
				self.active_connections: List[WebSocket] = []

		async def connect(self, websocket: WebSocket):
				await websocket.accept()
				self.active_connections.append(websocket)

		def disconnect(self, websocket: WebSocket):
				self.active_connections.remove(websocket)

		async def send_personal_message(self, message: str, websocket: WebSocket):
				await websocket.send_text(message)

		async def broadcast(self, message: str):
				for connection in self.active_connections:
						await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
		await manager.connect(websocket)
		await manager.broadcast(f"~#{client_id} has joined the chat.")
		try:
				while True:
						data = await websocket.receive_text()
						if data and data != "``":
							await manager.broadcast(f"{client_id}: {data}")
		except WebSocketDisconnect:
				manager.disconnect(websocket)
				await manager.broadcast(f"~#{client_id} has left the chat.")