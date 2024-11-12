import React, { useState, useEffect, useRef, useCallback } from "react";
import "./CustomChatWidget.css";

interface CustomChatWidgetProps {
  reconnectAll: () => void; // Add prop to trigger reconnection of all WebSockets
}

// Custom hook to manage WebSocket connection
const useWebSocket = (userId: number) => {
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

const CustomChatWidget: React.FC<CustomChatWidgetProps> = ({ reconnectAll }) => {
  const [input, setInput] = useState("");
  const [messageHistory, setMessageHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1); // Track position in message history
  
  const userId = 1;
  const { messages, setMessages, loading, setLoading, disconnected, establishConnection, hasConnected, ws_chat } = useWebSocket(userId);

  // Reference to scroll to the bottom of the messages
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Function to scroll to the bottom
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  };

  useEffect(() => {
    scrollToBottom(); // Scroll to the bottom every time messages change
  }, [messages, loading, disconnected, hasConnected]); // Runs when messages change

  function connect(){
    establishConnection()
    reconnectAll()
  }

  const handleSendMessage = useCallback(() => {
    if (input.trim() !== "" && ws_chat.current && !disconnected) {
      setMessages((prevMessages) => [...prevMessages, { sender: "user", text: input }]);
      ws_chat.current.send(JSON.stringify({ message: input }));

      // Update message history
      setMessageHistory(prevHistory => [...prevHistory, input]);
      setHistoryIndex(-1); // Reset history index after sending a message

      setInput("");
      setLoading(true);
    }
  }, [input, setMessages, ws_chat, disconnected]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleSendMessage();
    } else if (event.key === "ArrowUp") {
      // Navigate up in history
      if (historyIndex < messageHistory.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setInput(messageHistory[messageHistory.length - 1 - newIndex]);
      }
    } else if (event.key === "ArrowDown") {
      // Navigate down in history
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInput(messageHistory[messageHistory.length - 1 - newIndex]);
        
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInput("");
      }
    }
  }, [handleSendMessage, historyIndex, messageHistory]);

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
        {/* This div ensures the page scrolls to the bottom */}
        <div ref={messagesEndRef} />
      </div>
      {/* Only show the disconnected message if has connected */}
      {hasConnected && disconnected && (
        <div className="message system">
          <span>The chat connection has been closed.</span>
            <button onClick={connect} className="reconnect-button">
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