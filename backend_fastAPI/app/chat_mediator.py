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
            self.chat_agent.welcome()
            ws_manager_chat.set_welcome_sent(self.user_id)
            await self.send_response_queue() # Send welcome message directly

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

        # Finish disconnect after client acks
        if self.awaiting_ack and user_message == "exit-ack":
            print("Goodbye acknowledged by client.")
            await ws_manager_chat.disconnect(self.user_id)
            return

        # Process the message with the chat agent
        await self.chat_agent.process_message(user_message)

        # Send all messages currently in the response queue
        await self.send_response_queue()


    async def send_response_queue(self):
        """Send all messages in the response queue."""
        while self.chat_agent.response_queue:
            next_response = self.chat_agent.response_queue.popleft()  # Dequeue each response message

            print("Next response sending to chat:", next_response)

            # Check if the next response indicates an exit command
            if next_response.get("action") == "exit":
                self.awaiting_ack = True
      
            await ws_manager_chat.send_message(
                self.user_id, json.dumps(next_response)
            )