from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_access_token
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.database.session import get_db
from app.models.user import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if token is None:
        raise UnauthorizedError("Not authenticated")

    try:
        email = decode_access_token(token)
    except ValueError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    return user
