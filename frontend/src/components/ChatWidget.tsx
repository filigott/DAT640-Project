// src/components/ChatWidget.tsx
import React, { useEffect } from "react";

const ChatWidget: React.FC = () => {
  useEffect(() => {
    // Load the chat widget script
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "https://cdn.jsdelivr.net/npm/iaigroup-chatwidget@latest/build/bundle.min.js";
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []); // Run once when component mounts

  return (
    <div
      id="chatWidgetContainer"
      data-name="Chatbot"
      data-server-url="http://127.0.0.1:5000"
      data-use-feedback
      data-use-login
    />
  );
};

export default ChatWidget;
