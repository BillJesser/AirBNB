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
    path_params = (event or {}).get("pathParameters") or {}
    prop_id = path_params.get("id")
    if not prop_id:
        return _response(400, {"message": "Missing path parameter: id"})

    item = table.get_item(Key={"id": prop_id}).get("Item")
    if not item:
        return _response(404, {"message": "Not found"})
    return _response(200, item)
