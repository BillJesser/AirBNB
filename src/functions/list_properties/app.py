import json
import os
from common.db import get_table
from common.serialization import to_jsonable


def _response(status: int, body: dict | list):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=to_jsonable),
    }


def handler(event, context):
    table = get_table(os.environ["TABLE_NAME"]) 

    # Simple scan; for production, consider GSI/queries and pagination
    resp = table.scan(Limit=100)
    items = resp.get("Items", [])
    return _response(200, items)
