from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import supabase

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        user = supabase.auth.get_user(credentials.credentials).user
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from error

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return user.id
