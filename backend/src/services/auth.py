from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Optional, Protocol
from uuid import UUID, uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.auth import TokenData, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
DEFAULT_EXPIRE_MINUTES = 60 * 24


class UserAlreadyExistsError(Exception):
    """Raised when registering an email that already exists."""


class AuthRepository(Protocol):
    def get_by_email(self, email: str) -> Optional[dict]:
        ...

    def insert_user(
        self,
        user_id: UUID,
        email: str,
        display_name: str,
        password_hash: str,
    ) -> dict:
        ...


class PostgresAuthRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def get_by_email(self, email: str) -> Optional[dict]:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, email, display_name, password_hash,
                        created_at
                    FROM users
                    WHERE email = %s
                    """,
                    (email,),
                )
                return cursor.fetchone()

    def insert_user(
        self,
        user_id: UUID,
        email: str,
        display_name: str,
        password_hash: str,
    ) -> dict:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (
                        id, email, display_name, password_hash
                    ) VALUES (%s, %s, %s, %s)
                    RETURNING id, email, display_name, created_at
                    """,
                    (user_id, email, display_name, password_hash),
                )
                return cursor.fetchone()


@lru_cache
def get_auth_repository() -> AuthRepository:
    return PostgresAuthRepository(postgres_url=get_settings().postgres_url)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    return pwd_context.verify(password, password_hash)


def create_access_token(
    data: dict,
    secret_key: str,
    expires_minutes: int = DEFAULT_EXPIRE_MINUTES,
) -> str:
    to_encode = dict(data)
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def decode_token(token: str, secret_key: str) -> TokenData:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except JWTError as error:
        raise ValueError("Invalid token") from error
    user_id = payload.get("sub")
    email = payload.get("email")
    if user_id is None or email is None:
        raise ValueError("Invalid token payload")
    return TokenData(user_id=UUID(user_id), email=email)


def create_user(
    email: str,
    display_name: str,
    password: str,
    repository: Optional[AuthRepository] = None,
) -> UserResponse:
    repo = repository or get_auth_repository()
    if repo.get_by_email(email) is not None:
        raise UserAlreadyExistsError(email)
    row = repo.insert_user(
        user_id=uuid4(),
        email=email,
        display_name=display_name,
        password_hash=hash_password(password),
    )
    return UserResponse.model_validate(row)


def authenticate_user(
    email: str,
    password: str,
    repository: Optional[AuthRepository] = None,
) -> Optional[UserResponse]:
    repo = repository or get_auth_repository()
    row = repo.get_by_email(email)
    if row is None:
        return None
    if not verify_password(password, row.get("password_hash") or ""):
        return None
    return UserResponse.model_validate(row)
