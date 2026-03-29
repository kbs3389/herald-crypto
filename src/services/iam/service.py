"""
Herald Crypto Exchange - IAM Service (Agent 08)

Authentication, authorization, and user management.
Supports JWT tokens, user registration, and session management.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from jose import JWTError, jwt
except ImportError:
    from python_jose import jwt
    JWTError = Exception

import bcrypt


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

SECRET_KEY = "herald-crypto-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if credentials is None:
        # Allow demo access without auth
        return {"sub": "demo-user", "username": "demo"}
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


class TokenData:
    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username


class IAMService:
    """In-memory IAM service for authentication and user management."""

    def __init__(self):
        self._users: dict[str, dict] = {}
        self._sessions: dict[str, dict] = {}

    def register_user(self, username: str, password: str, email: str) -> Optional[dict]:
        if username in self._users:
            return None
        user_id = str(uuid4())
        hashed = _hash_password(password)
        user = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": hashed,
            "kyc_level": "NONE",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "two_factor_enabled": False,
        }
        self._users[username] = user
        return user

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        user = self._users.get(username)
        if user is None:
            return None
        if not _verify_password(password, user["password_hash"]):
            return None
        return user

    def get_user(self, username: str) -> Optional[dict]:
        return self._users.get(username)

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        for user in self._users.values():
            if user["user_id"] == user_id:
                return user
        return None

    def update_kyc_level(self, user_id: str, level: str) -> bool:
        for user in self._users.values():
            if user["user_id"] == user_id:
                user["kyc_level"] = level
                return True
        return False
