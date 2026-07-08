from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import get_password_hash, verify_password
from app.core.exceptions import ConflictError
from app.models.user import User
from app.schemas.auth import UserCreate


async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none() is not None:
        raise ConflictError("A user with this email already exists")

    user = User(email=user_in.email, hashed_password=get_password_hash(user_in.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
