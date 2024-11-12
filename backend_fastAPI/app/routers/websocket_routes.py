import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from requests import Session

from app.chat_mediator import ChatWSMediator
from ..database import get_db
from ..websocket import ws_manager_playlist


router = APIRouter()

# Playlist WebSocket endpoint
@router.websocket("/ws/playlist")
async def playlist_websocket_endpoint(websocket: WebSocket):
    await ws_manager_playlist.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        ws_manager_playlist.disconnect(websocket)


@router.websocket("/ws/chat/{user_id}")
async def chat_websocket_endpoint(user_id: int, websocket: WebSocket, db: Session = Depends(get_db)):
    chat_handler = ChatWSMediator(user_id, websocket, db)
    await chat_handler.handle_connection()
