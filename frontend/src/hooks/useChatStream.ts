import { streamChatCompletion } from "../utils/api";
import { addMessage, updateLastAssistantMessage } from "../store/chatStore";

export async function handleStreamingChat(
  formData: FormData,
  abortSignal: AbortSignal,
  onUpdate: () => void
): Promise<void> {
  addMessage({ role: "assistant", content: "" });
  onUpdate();

  const stream = await streamChatCompletion(formData, abortSignal);
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let assistantText = "";

  function processEvent(eventText: string) {
    const data = eventText.replace(/^data:\s?/, "").trim();
    if (data === "[DONE]") return;

    try {
      const payload = JSON.parse(data);
      if (payload.type === "chunk") {
        assistantText += String(payload.content ?? "");
      } else if (payload.type === "info" || payload.type === "error") {
        assistantText += `\n[System: ${payload.content}]\n`;
      }
      updateLastAssistantMessage(assistantText);
      onUpdate();
    } catch (e) { /* Buffer fragment */ }
  }

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    
    let boundary;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      processEvent(buffer.slice(0, boundary));
      buffer = buffer.slice(boundary + 2);
    }
  }
}