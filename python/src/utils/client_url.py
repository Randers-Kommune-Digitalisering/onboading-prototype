from __future__ import annotations
from urllib.parse import urlparse
from flask import has_request_context, request

from utils.config import ONBOARDING_BASE_URL


def get_client_base_url(default_base_url: str | None = None) -> str:
    """
    Return the client-facing base URL for the current request using `Origin` header (browser) if it is a valid http/https origin.
    """

    fallback = (default_base_url or ONBOARDING_BASE_URL).rstrip("/")

    if not has_request_context():
        return fallback

    origin = (request.headers.get("Origin") or "").strip()
    if origin and origin.lower() != "null":
        parsed = urlparse(origin)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")

    return fallback
