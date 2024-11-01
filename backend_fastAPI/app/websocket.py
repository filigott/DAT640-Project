import json
from fastapi import WebSocket
from typing import List, Dict

# Playlist connection manager
class PlaylistWSConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


# Chat connection manager with user-specific connections
class ChatWSConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}  # Maps user ID to WebSocket connection

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.connections:
            del self.connections[user_id]

    async def send_message(self, user_id: str, message: str):
        if user_id in self.connections:
            await self.connections[user_id].send_text(message)


ws_manager_playlist = PlaylistWSConnectionManager()
ws_manager_chat = ChatWSConnectionManager()

# For notifying frontend clients to update local state of matching playlist
async def ws_push_playlist_update(playlist_id: int = 1):
    message = {"updated_playlist_id": playlist_id}
    await ws_manager_playlist.broadcast(json.dumps(message))

# For sending message through custom chat widget
async def ws_chat_message(chat_message: str, user_id: int = 1):
    message = {"message": chat_message}
    await ws_manager_chat.send_message(user_id, json.dumps(message))

def get_ws_manager_playlist() -> PlaylistWSConnectionManager:
    return ws_manager_playlist

def get_ws_manager_chat() -> ChatWSConnectionManager:
    return ws_manager_chat
