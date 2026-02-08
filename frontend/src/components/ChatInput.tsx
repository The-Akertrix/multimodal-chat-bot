import { useState } from "react";
import ImagePreview from "./ImagePreview";
import ModelSelector from "./ModelSelector";
import { ModelProvider } from "../utils/types";

interface Props {
  onSend: (text: string, image: File | null, provider: ModelProvider) => void;
}

export default function ChatInput({ onSend }: Props): JSX.Element {
  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [provider, setProvider] = useState<ModelProvider>("gemini");

  const handleSend = () => {
    onSend(text, imageFile, provider);
    setText("");
    setImageFile(null);
  };

  return (
    <footer className="chat-input-area">
      {/* Absolute positioned selector to match top-right of the card */}
      <div className="selector-wrapper">
        <ModelSelector selected={provider} onChange={setProvider} />
      </div>

      <div className="input-controls">
        <label className="icon-btn image-upload">
          <input 
            type="file" 
            accept="image/*" 
            onChange={(e) => setImageFile(e.target.files?.[0] ?? null)} 
          />
          <span className="icon">🖼️</span>
        </label>
        
        <div className="text-wrapper">
          <textarea 
            placeholder="Type a message..." 
            value={text} 
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
          />
          {imageFile && <ImagePreview file={imageFile} />}
        </div>

        <button className="icon-btn send-btn" onClick={handleSend} disabled={!text.trim() && !imageFile}>
          <span className="icon">🚀</span>
        </button>
      </div>
    </footer>
  );
}