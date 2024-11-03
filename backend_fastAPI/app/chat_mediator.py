import json
from fastapi import WebSocket, WebSocketDisconnect
from requests import Session
from app.chat_agent import ChatAgent
from .websocket import ws_manager_chat

class ChatWSMediator:
    def __init__(self, user_id: str, websocket: WebSocket, db: Session):
        self.user_id = user_id
        self.websocket = websocket
        self.chat_agent = ChatAgent(db)
        self.awaiting_ack = False

    async def handle_connection(self):
        await ws_manager_chat.connect(self.user_id, self.websocket)
        if not ws_manager_chat.has_sent_welcome(self.user_id):
            await self.send_welcome_message()
            ws_manager_chat.set_welcome_sent(self.user_id)

        try:
            while True:
                data = await self.websocket.receive_text()
                await self.handle_message(data)
        except WebSocketDisconnect:
            print("WS disconnect")

    async def handle_message(self, data: str):
        message_data = json.loads(data)
        user_message = message_data.get("message")

        print("Handle message: ", user_message)

        # Store the result of processing the message
        processed_response = await self.chat_agent.process_message(user_message)

        print("Chat agent response:", processed_response)

        # Check if the processed response indicates an exit command
        if processed_response == "exit":
            await self.send_exit_message()
            self.awaiting_ack = True
            return

        # Finish disconnect after client acks
        if self.awaiting_ack and user_message == "exit-ack":
            print("Goodbye acknowledged by client.")
            await ws_manager_chat.disconnect(self.user_id)
            return
            
        await ws_manager_chat.send_message(self.user_id, json.dumps({"action": "message", "message": processed_response}))


    async def send_welcome_message(self):
        welcome_message = self.chat_agent.welcome()
        await ws_manager_chat.send_message(self.user_id, json.dumps({"action": "welcome", "message": welcome_message}))

    async def send_exit_message(self):
        goodbye_message = self.chat_agent.goodbye()
        await ws_manager_chat.send_message(self.user_id, json.dumps({"action": "exit", "message": goodbye_message}))
