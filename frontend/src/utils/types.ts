export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  imageUrl?: string;
}

export type ModelProvider = "gemini" | "groq";
