from __future__ import annotations

from typing import Any, Optional

from flask import request, session as flask_session

from models import Forløb, Opgave
from utils.config import KEYCLOAK_CLIENT_ID


def _norm_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value.lower() or None


def get_current_user_email() -> Optional[str]:
    """Returns the authenticated user's email.

    - In production (Keycloak enabled), prefer the server-side session userinfo.
    - In tests/dev, fall back to the `usermail` header.
    """

    user: Any = flask_session.get("user")
    if isinstance(user, dict):
        email = user.get("email") or user.get("preferred_username")
        email = _norm_email(email)
        if email:
            return email

    return _norm_email(request.headers.get("usermail"))


def _get_current_user_roles() -> list[str]:
    user: Any = flask_session.get("user")
    if isinstance(user, dict):
        roles = (
            user.get("resource_access", {})
            .get(KEYCLOAK_CLIENT_ID, {})
            .get("roles", [])
        )
        if isinstance(roles, list):
            return [str(r) for r in roles]

    # Dev/test convenience: allow injecting roles via header.
    raw = request.headers.get("roles")
    if raw:
        return [r.strip() for r in raw.split(",") if r.strip()]

    return []


def is_current_user_admin() -> bool:
    """Returns True if the current user should be treated as admin."""

    # When Keycloak is enabled, prefer server-side session roles.
    user: Any = flask_session.get("user")
    if isinstance(user, dict):
        return any(role.lower() == "admin" for role in _get_current_user_roles())

    # Dev/test fallback (no server-side session): preserve legacy `adminmail`.
    if request.headers.get("adminmail"):
        return True

    return any(role.lower() == "admin" for role in _get_current_user_roles())


def user_can_access_forloeb(
    session,
    forloeb_id: int,
    user_email: Optional[str],
    forloeb: Optional[Forløb] = None,
) -> bool:
    """Non-admin access rule for a forløb.

    Allowed if:
    - user_email matches forløb.usermail, OR
    - user_email matches ansvarligEmail on at least one opgave in the forløb.
    """

    user_email_norm = _norm_email(user_email)
    if not user_email_norm:
        return False

    if forloeb is None:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id).first()

    if not forloeb:
        return False

    if _norm_email(getattr(forloeb, "usermail", None)) == user_email_norm:
        return True

    ansvarlig_exists = (
        session.query(Opgave)
        .filter(
            Opgave.ForløbID == forloeb_id,
            Opgave.ansvarligEmail.ilike(user_email_norm),
        )
        .first()
        is not None
    )

    return ansvarlig_exists
