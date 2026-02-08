import { useState, useRef, useEffect } from "react";
import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";
import { getMessages, addMessage } from "../store/chatStore";
import { handleStreamingChat } from "../hooks/useChatStream";
import { stopChatCompletion } from "../utils/api";
import { ModelProvider } from "../utils/types";

interface ChatWindowProps {
  onLogout: () => void;
}

export default function ChatWindow({ onLogout }: ChatWindowProps): JSX.Element {
  const [, forceUpdate] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [getMessages().length, isStreaming]);

  const sendMessage = async (text: string, image: File | null, provider: ModelProvider) => {
    if (!text.trim() && !image) return;

    setIsStreaming(true);
    const controller = new AbortController();
    abortControllerRef.current = controller;

    addMessage({
      role: "user",
      content: text,
      imageUrl: image ? URL.createObjectURL(image) : undefined
    });
    forceUpdate((v) => v + 1);

    const formData = new FormData();
    formData.append("messages_json", JSON.stringify([{ role: "user", content: text }]));
    formData.append("model_provider", provider);
    if (image) formData.append("image_files", image);

    try {
      await handleStreamingChat(formData, controller.signal, () => forceUpdate((v) => v + 1));
    } catch (err: any) {
      if (err.name !== 'AbortError') console.error(err);
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort(); // Cancel local stream
      await stopChatCompletion(); // Backend stop
      setIsStreaming(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-card">
        <header className="chat-header">
          <h1>Multimodal ChatBot</h1>
          <div className="header-actions">
            {isStreaming && <button className="stop-btn" onClick={handleStop} style={{marginRight: '8px'}}>Stop</button>}
            <button className="logout-btn" onClick={onLogout}>Logout</button>
          </div>
        </header>

        <main className="messages-container">
          {getMessages().map((msg, i) => (
            <div key={i} className={`message-row ${msg.role}`}>
              <MessageBubble message={msg} />
            </div>
          ))}
          <div ref={messagesEndRef} />
        </main>

        <ChatInput onSend={sendMessage} />
      </div>
    </div>
  );
}