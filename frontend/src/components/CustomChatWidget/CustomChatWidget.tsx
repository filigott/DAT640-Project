import React, { useState, useEffect, useRef, useCallback } from "react";
import "./CustomChatWidget.css";

// Custom hook to manage WebSocket connection
const useWebSocket = (userId: string) => {
  const ws_chat = useRef<WebSocket | null>(null);
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [disconnected, setDisconnected] = useState(false);
  const [hasConnected, setHasConnected] = useState(false);

  const establishConnection = useCallback(() => {
    if (ws_chat.current) {
      ws_chat.current.close(); // Close any existing connection
    }

    ws_chat.current = new WebSocket(`ws://localhost:8000/ws/chat/${userId}`);

    ws_chat.current.onopen = () => {
      console.log("CustomChatWidget connected to WebSocket server");
      setDisconnected(false);
      setHasConnected(true)
    };

    ws_chat.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data);

      // Display the bot's message
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", text: data.message },
      ]);

      // Check if the server sent an exit message
      if (data.action === "exit") {
        // Send acknowledgment for exit
        ws_chat.current?.send(JSON.stringify({ message: "exit-ack" }));
      }

      setLoading(false);
    };

    ws_chat.current.onclose = () => {
      console.log("CustomChatWidget disconnected from WebSocket server");
      setDisconnected(true); // Set to true when disconnected
      setLoading(false);
    };
  }, [userId]);

  useEffect(() => {
    establishConnection();

    return () => {
      if (ws_chat.current) {
        ws_chat.current.close();
      }
    };
  }, [establishConnection]);

  return { messages, setMessages, loading, setLoading, disconnected, establishConnection, hasConnected, ws_chat };
};

const CustomChatWidget: React.FC = () => {
  const [input, setInput] = useState("");
  const userId = "user-123";

  const { messages, setMessages, loading, setLoading, disconnected, establishConnection, hasConnected, ws_chat } = useWebSocket(userId);

  const handleSendMessage = useCallback(() => {
    if (input.trim() !== "" && ws_chat.current && !disconnected) {
      setMessages((prevMessages) => [...prevMessages, { sender: "user", text: input }]);
      ws_chat.current.send(JSON.stringify({ message: input }));
      setInput("");
      setLoading(true);
    }
  }, [input, setMessages, ws_chat]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleSendMessage();
    }
  }, [handleSendMessage]);

  return (
    <div className="chatbot-container">
      <div className="chatbot-banner">
        <h2>Music Recommendation Chat Widget</h2>
      </div>
      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <span>{msg.text}</span>
          </div>
        ))}
        {loading && <div className="loading">Typing...</div>}
      </div>
      {/* Only show the disconnected message if has connected */}
      {hasConnected && disconnected && (
        <div className="message system">
          <span>The chat connection has been closed.</span>
          <button onClick={establishConnection} className="reconnect-button">
            Reconnect
          </button>
        </div>
      )}
      <div className="chatbot-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
        />
        <button disabled={disconnected} onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default CustomChatWidget;
