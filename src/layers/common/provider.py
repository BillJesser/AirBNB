from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .http import http_get


class ProviderError(Exception):
    pass


def _headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    # Support common auth patterns without over-configuring
    token = os.environ.get("PROVIDER_API_KEY") or os.environ.get("RAID_API_KEY") or os.environ.get("APIFY_TOKEN")
    if token:
        # Add both styles; upstream will use what it expects and ignore extras
        headers["Authorization"] = f"Bearer {token}"
        headers["X-API-Key"] = token
    # Allow explicit override of header name
    header_name = os.environ.get("PROVIDER_AUTH_HEADER")
    if header_name and token:
        headers[header_name] = token
    return headers


def _require(var: str) -> str:
    v = os.environ.get(var)
    if not v:
        raise ProviderError(f"Missing required environment variable: {var}")
    return v


def list_listings(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Fetch a list of listings from external provider.

    Required env vars:
      - LISTINGS_URL: full URL to provider search/list endpoint
      - One of PROVIDER_API_KEY, RAID_API_KEY, APIFY_TOKEN (optional if endpoint is public)
    """
    url = _require("LISTINGS_URL")
    data = http_get(url, headers=_headers(), params=params)
    # Try to normalize: if provider returns {"results": [...]}, unwrap it
    if isinstance(data, dict) and "results" in data and isinstance(data["results"], list):
        return data["results"]
    if isinstance(data, list):
        return data
    # Fallback: wrap single object
    return [data]


def get_listing(listing_id: str) -> Dict[str, Any]:
    """Fetch a single listing by ID.

    Required env vars:
      - LISTING_URL: URL template with optional {id} placeholder
    """
    template = _require("LISTING_URL")
    url = template.format(id=listing_id)
    data = http_get(url, headers=_headers())
    if isinstance(data, dict):
        return data
    raise ProviderError("Unexpected provider response shape for single listing")

