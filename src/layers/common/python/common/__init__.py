"""Common utilities package for Lambda layer.

Avoid importing submodules here to prevent pulling heavy dependencies
unless a consumer explicitly imports them, e.g.:
  from common.http import http_get
  from common.auth import issue_jwt
"""

__all__ = []
