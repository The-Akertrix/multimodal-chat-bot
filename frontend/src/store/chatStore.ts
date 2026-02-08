import { ChatMessage } from "../utils/types";

let messages: ChatMessage[] = [];

export function getMessages(): ChatMessage[] {
  return messages;
}

export function addMessage(message: ChatMessage): void {
  messages = [...messages, message];
}

export function updateLastAssistantMessage(content: string): void {
  messages = messages.map((message, index) =>
    index === messages.length - 1 && message.role === "assistant"
      ? { ...message, content }
      : message
  );
}
