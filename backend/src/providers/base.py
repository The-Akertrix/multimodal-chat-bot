from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Optional
import asyncio
import aiohttp

class BaseProvider(ABC):
    """
    Abstract base class for AI providers (Gemini, Groq).
    Handles text + image requests, streaming responses, and cancellation.
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key: str = api_key
        self.base_url: str = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def init_session(self) -> None:
        """Initialize aiohttp session if not already done."""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers={"Authorization": f"Bearer {self.api_key}"})

    async def close_session(self) -> None:
        """Close aiohttp session to clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None

    @abstractmethod
    async def stream_completion(
        self, 
        messages: list[dict[str, str]], 
        image_files: Optional[list] = None,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """
        Abstract method to stream a response from the AI provider.

        Args:
            messages (list[dict]): Chat messages with "role" and "content".
            image_files (Optional[list]): List of image UploadFile objects.
            kwargs: Provider-specific options.

        Yields:
            str: Streaming text chunks.
        """
        raise NotImplementedError

    async def cancel_request(self, task: asyncio.Task) -> None:
        """Cancel an in-progress AI request."""
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
