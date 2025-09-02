import json
from common.serialization import to_jsonable
from common.provider import list_listings, ProviderError


def _response(status: int, body: dict | list):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=to_jsonable),
    }


def handler(event, context):
    try:
        # Optional passthrough of query params to provider
        query = (event or {}).get("queryStringParameters") or {}
        items = list_listings(query)
        return _response(200, items)
    except ProviderError as e:
        return _response(500, {"message": str(e)})
