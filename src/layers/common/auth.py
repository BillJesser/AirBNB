import os
import time
from typing import Optional

import bcrypt
import jwt


class AuthError(Exception):
    pass


def _get_jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise AuthError("JWT_SECRET not configured")
    return secret


def hash_password(password: str) -> str:
    if not password or len(password) < 8:
        raise AuthError("Password must be at least 8 characters")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def issue_jwt(sub: str, ttl_seconds: int = 3600, extra: Optional[dict] = None) -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + ttl_seconds,
    }
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, _get_jwt_secret(), algorithm="HS256")
    # PyJWT >= 2 returns str
    return token if isinstance(token, str) else token.decode("utf-8")

