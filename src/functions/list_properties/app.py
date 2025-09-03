import json
import os
import urllib.parse
import urllib.request


def _response(status: int, body: dict | list):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event, context):
    # Optional passthrough of query params to provider
    query = (event or {}).get("queryStringParameters") or {}
    base_url = os.environ.get("LISTINGS_URL")
    if not base_url:
        return _response(500, {"message": "LISTINGS_URL not configured"})

    url = base_url
    if query:
        q = urllib.parse.urlencode(query)
        sep = '&' if ('?' in url) else '?'
        url = f"{url}{sep}{q}"

    req = urllib.request.Request(url)
    token = os.environ.get("PROVIDER_API_KEY") or os.environ.get("RAID_API_KEY") or os.environ.get("APIFY_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("X-API-Key", token)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, dict) and isinstance(data.get("results"), list):
                return _response(200, data["results"])
            if isinstance(data, list):
                return _response(200, data)
            return _response(200, [data])
    except Exception as e:
        return _response(500, {"message": str(e)})
