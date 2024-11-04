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
        self.active_connections: Dict[str, Dict] = {} # Maps userId to WS and other custom fields such as welcome_sent

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {"websocket": websocket, "welcome_sent": False}
        else:
            self.active_connections[user_id]["websocket"] = websocket

    async def disconnect(self, user_id: str):
        await self.active_connections[user_id]["websocket"].close()
        self.active_connections.pop(user_id, None)

    async def send_message(self, user_id: str, message: json):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]["websocket"]
            await websocket.send_text(message)

    def has_sent_welcome(self, user_id: str) -> bool:
        return self.active_connections.get(user_id, {}).get("welcome_sent", False)
            
    def set_welcome_sent(self, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id]["welcome_sent"] = True


ws_manager_playlist = PlaylistWSConnectionManager()
ws_manager_chat = ChatWSConnectionManager()

# For notifying frontend clients to update local state of matching playlist
async def ws_push_playlist_update(playlist_id: int = 1):
    message = {"updated_playlist_id": playlist_id}
    await ws_manager_playlist.broadcast(json.dumps(message))

def get_ws_manager_playlist() -> PlaylistWSConnectionManager:
    return ws_manager_playlist

def get_ws_manager_chat() -> ChatWSConnectionManager:
    return ws_manager_chat
