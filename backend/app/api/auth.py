from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.authentication import get_current_user
from app.auth.jwt import create_access_token
from app.core.exceptions import UnauthorizedError
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, UserCreate, UserRead
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    return await register_user(db, user_in)


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)) -> Token:
    user = await authenticate_user(db, credentials.email, credentials.password)
    if user is None:
        raise UnauthorizedError("Incorrect email or password")

    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
