import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from requests import Session
from ..database import get_db
from ..websocket import ws_manager_playlist, ws_manager_chat
from ..chat_agent.chat_agent import ChatAgent


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
async def chat_websocket_endpoint(user_id: str, websocket: WebSocket, db: Session = Depends(get_db)):
    await ws_manager_chat.connect(user_id, websocket)
    chat_agent = ChatAgent(db)
    awaiting_ack = False

    try:
        # Send welcome message only if it hasn't been sent for this user
        if not ws_manager_chat.has_sent_welcome(user_id):
            await ws_manager_chat.send_message(user_id, json.dumps({"action": "welcome", "message": chat_agent.welcome()}))
            ws_manager_chat.set_welcome_sent(user_id)

        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message")

            # Check for manual exit response
            if chat_agent.process_message(user_message) == "exit":
                await ws_manager_chat.send_message(user_id, json.dumps({"action": "exit", "message": chat_agent.goodbye()}))
                awaiting_ack = True
                continue

            if awaiting_ack and user_message == "exit-ack":
                print("Goodbye acknowledged by client.")
                await ws_manager_chat.disconnect(user_id)
                return
            
            # Process the message through ChatAgent
            chat_response = chat_agent.process_message(user_message)
            print("Chat agent response:", chat_response)

            # Send bot's response back to the user
            await ws_manager_chat.send_message(user_id, json.dumps({"action": "message", "message": chat_response}))


    except WebSocketDisconnect:
        print("WS disconnected.")
