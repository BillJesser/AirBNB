from __future__ import annotations

from decimal import Decimal


def to_jsonable(obj):
    if isinstance(obj, Decimal):
        # Prefer int when possible to avoid 1.0 style floats
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    if isinstance(obj, set):
        return list(obj)
    return str(obj)

