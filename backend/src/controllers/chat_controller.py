import json
from typing import AsyncIterator, Dict, List, Optional
from fastapi import UploadFile, HTTPException
from src.services.chat_service import ChatService

chat_service: ChatService | None = None

async def handle_chat_completion(
    model_provider: Optional[str],
    messages: List[Dict[str, str]],
    image_files: Optional[List[UploadFile]] = None,
) -> AsyncIterator[str]:
    global chat_service
    if chat_service is None:
        chat_service = ChatService()

    # Determine primary and fallback providers
    primary = (model_provider.lower() if model_provider 
               else chat_service.available_provider().lower())
    fallback = "groq" if primary == "gemini" else "gemini"

    try:
        # Attempt primary provider
        async for chunk in chat_service.generate_streaming_response(
            messages=messages,
            image_files=image_files,
            requested_provider=primary
        ):
            yield chunk

    except Exception as e:
        print(f"DEBUG: Primary {primary} failed ({str(e)}). Attempting fallback to {fallback}...")
        
        # Send an info notification to the UI
        yield f"data: {json.dumps({'type': 'info', 'content': f'Switching to {fallback} due to provider error...'})}\n\n"

        try:
            # Attempt fallback provider
            async for chunk in chat_service.generate_streaming_response(
                messages=messages,
                image_files=image_files,
                requested_provider=fallback
            ):
                yield chunk
        except Exception as final_error:
            raise HTTPException(
                status_code=503,
                detail=f"Both providers failed. Final error: {str(final_error)}"
            )