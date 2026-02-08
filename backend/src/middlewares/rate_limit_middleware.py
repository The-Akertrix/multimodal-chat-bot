from fastapi import HTTPException

from src.services.rate_limit_service import RateLimitService

rate_limit_service: RateLimitService = RateLimitService()

def enforce_rate_limit(user_id: str) -> None:
    """Enforce rate limit for user.

    Args:
        user_id: Identifier of user.

    Raises:
        HTTPException: If user exceeded limit.
    """
    try:
        rate_limit_service.check_rate_limit(user_id)
    except Exception as rate_error:
        raise HTTPException(status_code=429, detail=str(rate_error)) from rate_error
