from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.config import get_settings
settings = get_settings()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(str(password or "").strip())
def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(str(plain_password or "").strip(), password_hash)
def create_access_token(subject: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": exp}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
