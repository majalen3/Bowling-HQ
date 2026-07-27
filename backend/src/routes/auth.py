from fastapi import APIRouter, HTTPException, status

from src.config import get_settings
from src.models.auth import Token, UserCreate, UserLogin, UserResponse
from src.services.auth import (
    UserAlreadyExistsError,
    authenticate_user,
    create_access_token,
    create_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserCreate) -> UserResponse:
    try:
        return create_user(
            email=payload.email,
            display_name=payload.display_name,
            password=payload.password,
        )
    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from error


@router.post("/login", response_model=Token)
def login(payload: UserLogin) -> Token:
    user = authenticate_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        secret_key=get_settings().secret_key,
    )
    return Token(access_token=token)
