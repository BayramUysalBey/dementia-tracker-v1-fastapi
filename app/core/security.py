from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from app.core.settings import settings


password_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:  
    return password_hashing.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hashing.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt