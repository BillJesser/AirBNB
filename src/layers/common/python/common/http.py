from __future__ import annotations

import os
import random
import time
from typing import Any, Dict, Optional

import requests


class HttpError(Exception):
    pass


def http_get(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: int = 10) -> dict:
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        if not resp.ok:
            raise HttpError(f"GET {url} -> {resp.status_code}: {resp.text}")
        return resp.json()
    except requests.RequestException as e:
        raise HttpError(str(e))

