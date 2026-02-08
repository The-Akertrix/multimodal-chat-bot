import os
import json
import base64
from typing import AsyncGenerator, Optional
from fastapi import UploadFile
from dotenv import load_dotenv
from .base import BaseProvider

# Load variables from .env
load_dotenv()

class GeminiProvider(BaseProvider):
    name = "gemini"
    model = "gemini-2.0-flash"

    def __init__(self) -> None:
        # Code now correctly pulls the uppercase key from .env
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent"
        super().__init__(api_key, base_url)

    async def stream_completion(
        self,
        messages: list[dict[str, str]],
        image_files: Optional[list[UploadFile]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        await self.init_session()
        url = f"{self.base_url}?alt=sse"

        contents = []
        for msg in messages:
            parts = [{"text": msg.get("content")}]
            contents.append({"role": msg.get("role"), "parts": parts})

        # FIX: Actually attach images to the request
        if image_files:
            for img in image_files:
                img_bytes = await img.read()
                encoded_img = base64.b64encode(img_bytes).decode("utf-8")
                contents[-1]["parts"].append({
                    "inline_data": {
                        "mime_type": img.content_type or "image/jpeg",
                        "data": encoded_img
                    }
                })

        headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}
        
        async with self.session.post(url, json={"contents": contents}, headers=headers) as resp:
            resp.raise_for_status()
            buffer = ""
            async for chunk in resp.content.iter_any():
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:])
                            text = data['candidates'][0]['content']['parts'][0].get('text', '')
                            if text: yield text
                        except: continue