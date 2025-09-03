import base64
import hmac
import hashlib
import json
import os
import re
import secrets
import time
from typing import Any, Dict

import boto3


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _response(status: int, body: Dict[str, Any]):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


class AuthError(Exception):
    pass


def _hash_password(password: str, iterations: int = 100_000) -> str:
    if not password or len(password) < 8:
        raise AuthError("Password must be at least 8 characters")
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2${iterations}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(dk).decode()}"


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
        if not _EMAIL_RE.match(email):
            return _response(400, {"message": "Invalid email"})
        pw_hash = _hash_password(password)

        table_name = os.environ["USERS_TABLE_NAME"]
        ddb = boto3.resource("dynamodb").Table(table_name)
        # Conditional create to avoid overwriting existing user
        ddb.put_item(
            Item={
                "email": email,
                "password_hash": pw_hash,
            },
            ConditionExpression="attribute_not_exists(email)",
        )
        return _response(201, {"message": "User created"})
    except AuthError as e:
        return _response(400, {"message": str(e)})
    except Exception as e:
        # ConditionalCheckFailedException → user exists
        msg = str(e)
        if "ConditionalCheckFailedException" in msg:
            return _response(409, {"message": "User already exists"})
        return _response(500, {"message": "Internal error"})
