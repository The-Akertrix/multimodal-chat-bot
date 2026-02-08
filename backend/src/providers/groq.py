from typing import AsyncGenerator, Optional, List, Dict
from fastapi import UploadFile
from .base import BaseProvider
import aiohttp
import os
import json

class GroqProvider(BaseProvider):
    name = "groq"

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY must be set")
        base_url = "https://api.groq.com/openai/v1"
        super().__init__(api_key, base_url)

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        image_files: Optional[List[UploadFile]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        await self.init_session()
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "stream": True
        }

        async with self.session.post(url, json=payload, timeout=60) as resp:
            resp.raise_for_status()
            buffer = ""
            async for chunk in resp.content.iter_any():
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:])
                            text = data['choices'][0]['delta'].get('content')
                            if text: yield text
                        except:
                            continue