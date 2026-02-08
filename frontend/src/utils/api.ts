const API_BASE_URL = "http://localhost:8000/api/v1";

export async function streamChatCompletion(
  formData: FormData,
  abortSignal: AbortSignal
): Promise<ReadableStream<Uint8Array>> {
  const response = await fetch(`${API_BASE_URL}/chats/completion`, {
    method: "POST",
    body: formData,
    signal: abortSignal,
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`
    }
  });

  if (!response.body) {
    throw new Error("No response stream");
  }

  return response.body;
}

export async function stopChatCompletion(): Promise<void> {
  await fetch(`${API_BASE_URL}/chats/completion/stop`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`
    }
  });
}
