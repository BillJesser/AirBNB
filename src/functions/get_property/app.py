import json
import os
import urllib.request


def _response(status: int, body: dict | list):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event, context):
    path_params = (event or {}).get("pathParameters") or {}
    prop_id = path_params.get("id")
    if not prop_id:
        return _response(400, {"message": "Missing path parameter: id"})

    template = os.environ.get("LISTING_URL")
    if not template:
        return _response(500, {"message": "LISTING_URL not configured"})
    url = template.format(id=prop_id)

    req = urllib.request.Request(url)
    token = os.environ.get("PROVIDER_API_KEY") or os.environ.get("RAID_API_KEY") or os.environ.get("APIFY_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("X-API-Key", token)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, dict):
                return _response(200, data)
            return _response(200, {"data": data})
    except Exception as e:
        return _response(500, {"message": str(e)})
