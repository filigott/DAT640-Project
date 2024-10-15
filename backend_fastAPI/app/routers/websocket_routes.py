from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..websocket import get_ws_manager

router = APIRouter()

@router.websocket("/ws/playlist")
async def websocket_endpoint(websocket: WebSocket):
    ws_manager = get_ws_manager()
    await ws_manager.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)