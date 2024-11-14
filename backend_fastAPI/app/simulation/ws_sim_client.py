import json
import websockets
import asyncio

class WebSocketClient:
    def __init__(self, user_id, ws_url):
        self.user_id = user_id
        self.ws_url = ws_url
        self.ws_connection = None
        self.connected = False

    async def connect(self):
        """Establish the WebSocket connection."""
        try:
            self.ws_connection = await websockets.connect(f"{self.ws_url}/chat/{self.user_id}")
            self.connected = True
            print(f"[Client {self.user_id}] Connected to WebSocket")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"[Client {self.user_id}] Connection closed unexpectedly: {e}")
            self.connected = False  # Set connected to False immediately on failure
        except Exception as e:
            print(f"[Client {self.user_id}] Failed to connect: {e}")
            self.connected = False  # Ensure connected is set to False on any error

    async def send_message(self, message):
        """Send a message through the WebSocket connection."""
        if not self.connected:
            print(f"[Client {self.user_id}] WebSocket not connected, cannot send message.")
            return

        try:
            print(f"[Client {self.user_id}] Sending message: {message}")
            await self.ws_connection.send(json.dumps({"message": message}))
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"[Client {self.user_id}] Connection closed while sending message: {e}")
            self.connected = False  # Exit and prevent further actions if closed
        except Exception as e:
            print(f"[Client {self.user_id}] Error while sending message: {e}")
            self.connected = False  # Immediately set connected to False if an error occurs

    async def receive_response(self):
        """Receive a response from the WebSocket connection."""
        if not self.connected:
            print(f"[Client {self.user_id}] WebSocket not connected, cannot receive response.")
            return None
        
        try:
            response = await self.ws_connection.recv()
            data = json.loads(response)
            resp = data.get("message")
            print(f"[Client {self.user_id}] Received response: {resp}")
            return resp
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"[Client {self.user_id}] Connection closed while receiving response: {e}")
            self.connected = False  # Prevent further attempts to receive if closed
        except Exception as e:
            print(f"[Client {self.user_id}] Error while receiving response: {e}")
            self.connected = False  # Ensure connected is False if an error occurs
        return None

    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if not self.connected:
            print(f"[Client {self.user_id}] WebSocket is already disconnected.")
            return

        try:
            await self.send_message("exit")
            await self.ws_connection.close()
            self.connected = False
            print(f"[Client {self.user_id}] Disconnected from WebSocket")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"[Client {self.user_id}] Connection was already closed: {e}")
            self.connected = False  # Mark as disconnected if it wasn’t already
        except Exception as e:
            print(f"[Client {self.user_id}] Error while disconnecting: {e}")
            self.connected = False  # Ensure the connected state is False on error
