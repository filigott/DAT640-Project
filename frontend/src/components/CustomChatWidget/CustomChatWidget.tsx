import React, { useState, useEffect, useRef } from "react";
import "./CustomChatWidget.css";

const CustomChatWidget: React.FC = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const ws_chat = useRef<WebSocket | null>(null);

  const userId = "user-123"

  useEffect(() => {
    // Establish WebSocket connection on mount
    ws_chat.current = new WebSocket("ws://localhost:8000/ws/chat/" + userId);
    
    ws_chat.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Add the server's response message
       setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", text: data.message }
      ]);

      // Stop loading animation when a response is received
      setLoading(false);
    };

    ws_chat.current.onopen = () => console.log("CustomChatWidget connected to WS server");
    ws_chat.current.onclose = () => console.log("CustomChatWidget disconnected from WebSocket server");

    // Cleanup the WebSocket connection on component unmount
    return () => {
      ws_chat.current?.close();
    };
  }, []);

  const handleSendMessage = () => {
    if (ws_chat.current && input.trim() !== "") {
      setMessages((prevMessages) => [...prevMessages, { sender: "user", text: input }]);

      ws_chat.current.send(JSON.stringify({ message: input }));
      setInput("");
      setLoading(true); // Show loading animation while waiting for a response
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleSendMessage();
    }
  };

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
      <div className="chatbot-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default CustomChatWidget;
