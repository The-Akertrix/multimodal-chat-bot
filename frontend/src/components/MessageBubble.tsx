import { marked } from "marked";
import { ChatMessage } from "../utils/types";

export default function MessageBubble({ message }: { message: ChatMessage }): JSX.Element {
  // Parsing markdown content into safe HTML
  const parsedContent = marked.parse(message.content) as string;

  return (
    <div className={`message-row ${message.role}`}>
      <div className={`bubble ${message.role}`}>
        {message.imageUrl && (
          <img className="msg-img" src={message.imageUrl} alt="upload" />
        )}
        <div 
          className="markdown-body" 
          dangerouslySetInnerHTML={{ __html: parsedContent }} 
        />
      </div>
    </div>
  );
}