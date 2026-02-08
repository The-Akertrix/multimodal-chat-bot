import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Dict
from fastapi import HTTPException

# Token lifetimes
ACCESS_TOKEN_LIFETIME_MINUTES = 15
REFRESH_TOKEN_LIFETIME_DAYS = 7

class AuthService:
    """Service for handling authentication, JWTs, and refresh token rotation."""

    # In-memory refresh token store: {token_id: user_id}
    _refresh_token_store: Dict[str, str] = {}

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    # ------------------ Access Token ------------------
    def create_access_token(self, user_id: str) -> str:
        """Create a JWT access token for the given user ID."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
        payload = {"sub": user_id, "exp": expire}
        # PyJWT v2+ returns string, no need to decode
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    # ------------------ Refresh Token ------------------
    def create_refresh_token(self, user_id: str) -> str:
        """Create a JWT refresh token and store it for rotation."""
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
        token_id = str(uuid4())  # unique ID for rotation
        payload = {"sub": user_id, "jti": token_id, "exp": expire}

        # Store the token_id for rotation tracking
        self._refresh_token_store[token_id] = user_id

        # PyJWT v2+ returns string
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    # ------------------ Verify Token ------------------
    def verify_token(self, token: str) -> Dict[str, str]:
        """Verify a JWT token and return its payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    # ------------------ Rotate Refresh Token ------------------
    def rotate_refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Use a refresh token to get a new access token + refresh token.
        Implements rotation: old token is revoked immediately.
        """
        payload = self.verify_token(refresh_token)
        token_id = payload.get("jti")
        user_id = payload.get("sub")

        if not token_id or token_id not in self._refresh_token_store:
            raise HTTPException(status_code=401, detail="Refresh token invalid or already used")

        # Revoke old token
        del self._refresh_token_store[token_id]

        # Issue new tokens
        new_access_token = self.create_access_token(user_id)
        new_refresh_token = self.create_refresh_token(user_id)

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}

    # ------------------ Revoke Refresh Token ------------------
    def revoke_refresh_token(self, refresh_token: str):
        """Manually revoke a refresh token (e.g., logout)."""
        payload = self.verify_token(refresh_token)
        token_id = payload.get("jti")
        if token_id in self._refresh_token_store:
            del self._refresh_token_store[token_id]
