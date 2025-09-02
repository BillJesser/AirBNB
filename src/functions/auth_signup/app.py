import json
import os
import re
from typing import Any, Dict

import boto3
from common.auth import hash_password, AuthError
from common.serialization import to_jsonable


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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
        if not _EMAIL_RE.match(email):
            return _response(400, {"message": "Invalid email"})
        pw_hash = hash_password(password)

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

