from typing import AsyncIterator, Dict, List, Optional, Literal
import json
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    Request,
)
from fastapi.responses import StreamingResponse

from src.controllers.chat_controller import handle_chat_completion
from src.middlewares.auth_middleware import get_current_user
from src.middlewares.file_validation_middleware import validate_image_files
from src.middlewares.rate_limit_middleware import enforce_rate_limit

chat_router: APIRouter = APIRouter(prefix="/api/v1/chats")

@chat_router.post("/completion")
async def create_chat_completion(
    request: Request,
    # 1. Enforce that only 'gemini' or 'groq' are accepted as providers
    model_provider: Literal["gemini", "groq"] = Form(...),
    messages_json: str = Form(...),
    # 2. Specifically typed for image uploads
    image_files: Optional[List[UploadFile]] = File(default=None),
    user_id: str = Depends(get_current_user),
) -> StreamingResponse:
    """
    Stream a multimodal chat completion restricted to Gemini and Groq providers.
    """
    enforce_rate_limit(user_id)
    messages = _parse_messages(messages_json)
    
    # Process the UploadFile list for images
    files_list = image_files or []

    if files_list:
        validate_image_files(files_list)

    async def event_stream() -> AsyncIterator[bytes]:
        try:
            async for chunk in handle_chat_completion(
                model_provider=model_provider,
                messages=messages,
                image_files=files_list or None,
            ):
                if await request.is_disconnected():
                    break
                
                # Check if chunk is already SSE formatted (e.g., from fallback info)
                if chunk.startswith("data:"):
                    yield chunk.encode("utf-8")
                else:
                    # Normalize raw text into standard JSON chunk format
                    payload = {"type": "chunk", "content": chunk}
                    yield f"data: {json.dumps(payload)}\n\n".encode("utf-8")

            if not await request.is_disconnected():
                yield b"data: [DONE]\n\n"

        except Exception as e:
            # Graceful error reporting via SSE
            error_payload = {"type": "error", "content": f"Streaming failed: {str(e)}"}
            yield f"data: {json.dumps(error_payload)}\n\n".encode("utf-8")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no", # Critical for real-time delivery in Docker
        },
    )

@chat_router.delete("/completion/stop")
async def stop_chat_completion() -> Dict[str, str]:
    """
    Endpoint for explicit cancellation. 
    The stream itself is managed by the request.is_disconnected() check.
    """
    return {"status": "stopped"}



def _parse_messages(messages_json: str) -> List[Dict[str, str]]:
    """Helper to parse the messages_json Form field into a list of dicts."""
    try:
        import json
        return json.loads(messages_json)
    except Exception:
        return [{"role": "user", "content": messages_json}]