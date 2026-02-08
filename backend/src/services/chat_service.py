import os 
from typing import Optional, List, Dict, AsyncIterator
from fastapi import UploadFile, HTTPException

from src.providers.gemini import GeminiProvider
from src.providers.groq import GroqProvider

class ChatService:
    def __init__(self) -> None:
        # We store all successfully initialized providers in a dictionary
        self.providers = {}
        
        # Try to initialize Gemini
        if os.getenv("GEMINI_API_KEY"):
            try:
                self.providers["gemini"] = GeminiProvider()
            except Exception as e:
                print(f"Failed to init Gemini: {e}")

        # Try to initialize Groq
        if os.getenv("GROQ_API_KEY"):
            try:
                self.providers["groq"] = GroqProvider()
            except Exception as e:
                print(f"Failed to init Groq: {e}")

    def available_provider(self) -> Optional[str]:
        """Returns the first available provider name for default use."""
        if "gemini" in self.providers:
            return "gemini"
        if "groq" in self.providers:
            return "groq"
        return None

    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        image_files: Optional[List[UploadFile]] = None,
        requested_provider: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Routes the request to the specific provider requested.
        This allows the Controller to implement fallback logic.
        """
        # Determine which provider to use
        provider_key = requested_provider.lower() if requested_provider else self.available_provider()
        
        provider = self.providers.get(provider_key)
        
        if not provider:
            raise HTTPException(
                status_code=400, 
                detail=f"Provider '{provider_key}' is not initialized or available."
            )

        # Stream the response from the chosen provider
        async for chunk in provider.stream_completion(messages, image_files):
            yield chunk