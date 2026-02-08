from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.services.auth_service import AuthService
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY not set in environment")

# Use the same AuthService as routes
auth_service: AuthService = AuthService(secret_key=JWT_SECRET_KEY)

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)] = None,
) -> str:
    """
    Validate Bearer token and return user_id.
    Raises 401 if missing or invalid.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    raw_token = credentials.credentials
    payload = auth_service.verify_token(raw_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return user_id
