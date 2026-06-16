"""Local shim for the external `rk-digi` / `rkdigi` package.

This workspace only uses `EmailSender`. We provide a compatible implementation
here so we can fix MIME construction bugs deterministically (without patching
site-packages inside `.venv`).
"""

from .email_handling import EmailSender

__all__ = ["EmailSender"]
