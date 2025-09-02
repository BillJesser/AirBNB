import json
import os
from typing import Any, Dict

import boto3
from common.auth import verify_password, issue_jwt, AuthError
from common.serialization import to_jsonable


def _response(status: int, body: Dict[str, Any]):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=to_jsonable),
    }


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

        if not verify_password(password, item.get("password_hash") or ""):
            return _response(401, {"message": "Invalid credentials"})

        token = issue_jwt(email)
        return _response(200, {"token": token})
    except AuthError as e:
        return _response(400, {"message": str(e)})
    except Exception:
        return _response(500, {"message": "Internal error"})

