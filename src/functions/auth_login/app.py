import base64
import hmac
import hashlib
import json
import os
import time
from typing import Any, Dict

import boto3


def _response(status: int, body: Dict[str, Any]):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


class AuthError(Exception):
    pass


def _verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iter_s, salt_b64, hash_b64 = stored.split("$")
        if scheme != "pbkdf2":
            return False
        iterations = int(iter_s)
        salt = base64.urlsafe_b64decode(salt_b64 + "==")
        expected = base64.urlsafe_b64decode(hash_b64 + "==")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def _jwt_encode(payload: Dict[str, Any], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    def b64(obj):
        return base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode()).rstrip(b"=")
    header_b64 = b64(header)
    payload_b64 = b64(payload)
    signing_input = header_b64 + b"." + payload_b64
    sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=")
    return (signing_input + b"." + sig_b64).decode()


def handler(event, context):
    try:
        body = event.get("body") or "{}"
        data = json.loads(body)
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not email or not password:
            return _response(400, {"message": "Email and password required"})

        table_name = os.environ["USERS_TABLE_NAME"]
        ddb = boto3.resource("dynamodb").Table(table_name)
        item = ddb.get_item(Key={"email": email}).get("Item")
        if not item:
            return _response(401, {"message": "Invalid credentials"})

        if not _verify_password(password, item.get("password_hash") or ""):
            return _response(401, {"message": "Invalid credentials"})

        now = int(time.time())
        payload = {"sub": email, "iat": now, "exp": now + 3600}
        token = _jwt_encode(payload, os.environ.get("JWT_SECRET", "dev-change-me"))
        return _response(200, {"token": token})
    except AuthError as e:
        return _response(400, {"message": str(e)})
    except Exception:
        return _response(500, {"message": "Internal error"})
