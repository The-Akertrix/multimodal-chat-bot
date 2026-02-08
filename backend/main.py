from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.routes.auth_routes import auth_router
from src.routes.chat_routes import chat_router

load_dotenv()

def create_application() -> FastAPI:
    application: FastAPI = FastAPI(
        title="GC 2026 Multimodal Chatbot",
    )

    # Updated CORS to handle both localhost and 127.0.0.1 for Docker stability 
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(auth_router)
    application.include_router(chat_router)

    return application

app: FastAPI = create_application()