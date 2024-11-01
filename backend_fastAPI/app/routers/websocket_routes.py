import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket import ws_manager_playlist, ws_manager_chat

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


# Chat WebSocket endpoint with user-specific connections
@router.websocket("/ws/chat/{user_id}")
async def chat_websocket_endpoint(user_id: str, websocket: WebSocket):
    await ws_manager_chat.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            print(message_data)

            # DO LOGIC HERE / CALL RASA?

            bot_response = message_data.get("message")

            # Send bot's response back to the user
            await ws_manager_chat.send_message(user_id, json.dumps({"message": bot_response}))

    except WebSocketDisconnect:
        ws_manager_chat.disconnect(user_id)
