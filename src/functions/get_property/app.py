import json
from common.serialization import to_jsonable
from common.provider import get_listing, ProviderError


def _response(status: int, body: dict | list):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=to_jsonable),
    }


def handler(event, context):
    path_params = (event or {}).get("pathParameters") or {}
    prop_id = path_params.get("id")
    if not prop_id:
        return _response(400, {"message": "Missing path parameter: id"})
    try:
        item = get_listing(prop_id)
        return _response(200, item)
    except ProviderError as e:
        return _response(500, {"message": str(e)})
