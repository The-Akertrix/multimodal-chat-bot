import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.auth_service import AuthService

from dotenv import load_dotenv
load_dotenv()

# Load secret from environment variable
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY not set in environment")

auth_service: AuthService = AuthService(secret_key=JWT_SECRET_KEY)

# Admin credentials (in-memory, for this task only)
ADMIN_USER_ID = "admin-user"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpass"

auth_router: APIRouter = APIRouter(prefix="/api/v1/auth")


# -------------------- Request/Response Models --------------------

class LoginRequest(BaseModel):
    """Login request payload."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT access + refresh token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Payload for rotating refresh token."""
    refresh_token: str


# -------------------- Routes --------------------

@auth_router.post("/login", response_model=TokenResponse)
async def login_user(payload: LoginRequest) -> TokenResponse:
    """
    Authenticate admin user and issue JWT tokens.

    Args:
        payload (LoginRequest): Admin login credentials.

    Returns:
        TokenResponse: Access and refresh JWT tokens.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    if payload.username != ADMIN_USERNAME or payload.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate tokens
    access_token = auth_service.create_access_token(ADMIN_USER_ID)
    refresh_token = auth_service.create_refresh_token(ADMIN_USER_ID)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(payload: RefreshRequest) -> TokenResponse:
    """
    Rotate refresh token and return a new pair of JWT tokens.

    Args:
        payload (RefreshRequest): Refresh token payload.

    Returns:
        TokenResponse: New access and refresh tokens.

    Raises:
        HTTPException: 401 if refresh token is invalid or revoked.
    """
    tokens = auth_service.rotate_refresh_token(payload.refresh_token)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"]
    )
