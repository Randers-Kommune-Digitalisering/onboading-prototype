import os
import re
import smtplib
from html import unescape
from typing import Sequence

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr


class EmailSender:
    """Send email via SMTP.

    Drop-in replacement for `rkdigi.EmailSender` (rk-digi 1.1.0).

    Fixes:
    - Constructs HTML messages as `multipart/alternative` (plain + html) and
      wraps in `multipart/mixed` when attachments exist.
      This prevents clients (Gmail/Outlook) from displaying *both* parts or
      treating the HTML part as an attachment (e.g. `ATTT00001.htm`).
    - Generates plain text from HTML (not Markdown).
    """

    def __init__(
        self,
        smtp_server: str | None = None,
        smtp_port: int | None = None,
        sender_email: str | None = None,
        sender_password: str | None = None,
        sender_name: str | None = None,
        reply_to_email: str | None = None,
        reply_to_name: str | None = None,
    ):
        self._smtp_server = smtp_server or os.environ.get("SMTP_SERVER", "smtp.randers.dk")
        self._smtp_port = smtp_port or int(os.environ.get("SMTP_PORT", 25))

        self.sender_email = sender_email
        self._sender_password = sender_password

        self.sender: str | tuple[str, str] = ""
        if sender_email:
            if not self._check_address_header(sender_email):
                raise ValueError(f"Invalid sender email address: {sender_email}")
            self.sender = (sender_name, sender_email) if sender_name else sender_email

        self.reply_to: str | tuple[str, str] = ""
        if reply_to_email:
            if not self._check_address_header(reply_to_email):
                raise ValueError(f"Invalid reply-to email address: {reply_to_email}")
            self.reply_to = (reply_to_name, reply_to_email) if reply_to_name else reply_to_email

        if not self._can_connect():
            raise ConnectionError(
                f"Cannot connect to SMTP server {self._smtp_server}:{self._smtp_port}"
            )

    def _check_address_header(self, address: str | tuple[str, str]) -> bool:
        if isinstance(address, str):
            return "@" in address
        if isinstance(address, tuple) and len(address) == 2:
            return "@" in address[1]
        return False

    def _can_connect(self) -> bool:
        try:
            with smtplib.SMTP(host=self._smtp_server, port=self._smtp_port, timeout=5) as server:
                server.ehlo()
            return True
        except Exception:
            return False

    def _is_html(self, body: str) -> bool:
        if not body:
            return False
        lower = body.lower()
        if "<html" in lower:
            return True
        return bool(
            re.search(
                r"<\s*(p|br|div|span|table|a|body|head|style|strong|em|ul|ol|li)\b",
                lower,
            )
        )

    def _html_to_text(self, html: str) -> str:
        if not html:
            return ""

        text = html
        text = re.sub(
            r"<\s*script[^>]*>.*?<\s*/\s*script\s*>",
            "",
            text,
            flags=re.I | re.S,
        )
        text = re.sub(
            r"<\s*style[^>]*>.*?<\s*/\s*style\s*>",
            "",
            text,
            flags=re.I | re.S,
        )

        # Preserve links as: label (url)
        link_pattern = re.compile(
            r"<\s*a\b[^>]*?href\s*=\s*(['\"])(.*?)\1[^>]*>(.*?)<\s*/\s*a\s*>",
            flags=re.I | re.S,
        )

        def link_repl(match: re.Match) -> str:
            href = (match.group(2) or "").strip()
            label_html = match.group(3) or ""
            label = re.sub(r"<[^>]+>", "", label_html)
            label = unescape(label).strip()
            if not label:
                return href
            if label == href:
                return href
            return f"{label} ({href})"

        text = link_pattern.sub(link_repl, text)

        # Basic block separators
        text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.I)
        text = re.sub(r"<\s*/\s*p\s*>", "\n\n", text, flags=re.I)
        text = re.sub(r"<\s*/\s*div\s*>", "\n", text, flags=re.I)

        # Drop remaining tags.
        text = re.sub(r"<[^>]+>", "", text)
        text = unescape(text)

        # Normalize whitespace.
        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    def _normalize_recipients(
        self,
        recipients: str | tuple[str, str] | Sequence[str | tuple[str, str]] | None,
    ) -> list[str | tuple[str, str]]:
        if recipients is None:
            return []
        if isinstance(recipients, (str, tuple)):
            return [recipients]
        return list(recipients)

    def _normalize_cc(
        self,
        cc: str | tuple[str, str] | Sequence[str | tuple[str, str]] | None,
    ) -> list[str | tuple[str, str]]:
        if cc is None:
            return []
        if isinstance(cc, (str, tuple)):
            return [cc]
        return list(cc)

    def _build_message(
        self,
        sender: str | tuple[str, str],
        reply_to: str | tuple[str, str],
        recipients: list[str | tuple[str, str]],
        subject: str,
        body: str,
        cc: str | tuple[str, str] | Sequence[str | tuple[str, str]] | None,
        attachments: Sequence[str | tuple[str, bytes]] | None,
    ) -> tuple[MIMEMultipart, str, Sequence[str]]:
        attachments = attachments or []
        cc_list = self._normalize_cc(cc)
        to_headers = recipients + cc_list

        for addr in [sender] + to_headers + ([reply_to] if reply_to else []):
            if not self._check_address_header(addr):
                raise ValueError(f"Invalid email address: {addr}")

        msg = MIMEMultipart("mixed")
        msg["From"] = formataddr(sender) if isinstance(sender, tuple) else sender
        if reply_to:
            msg["Reply-To"] = formataddr(reply_to) if isinstance(reply_to, tuple) else reply_to
        if recipients:
            msg["To"] = ", ".join(
                formataddr(a) if isinstance(a, tuple) else a for a in recipients
            )
        if cc_list:
            msg["Cc"] = ", ".join(
                formataddr(a) if isinstance(a, tuple) else a for a in cc_list
            )
        msg["Subject"] = subject or ""

        if self._is_html(body):
            alt = MIMEMultipart("alternative")
            alt.attach(MIMEText(self._html_to_text(body), "plain", "utf-8"))
            alt.attach(MIMEText(body, "html", "utf-8"))
            msg.attach(alt)
        else:
            msg.attach(MIMEText(body or "", "plain", "utf-8"))

        for att in attachments:
            if isinstance(att, str):
                with open(att, "rb") as f:
                    content = f.read()
                filename = os.path.basename(att)
            elif (
                isinstance(att, tuple)
                and len(att) == 2
                and isinstance(att[0], str)
                and isinstance(att[1], (bytes, bytearray, memoryview))
            ):
                filename, content = att[0], bytes(att[1])
            else:
                raise ValueError(
                    "Attachments must be file paths (str) or (filename, bytes) tuples."
                )

            part = MIMEBase("application", "octet-stream")
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
            msg.attach(part)

        from_addr = sender[1] if isinstance(sender, tuple) else sender
        to_addrs = [a[1] if isinstance(a, tuple) else a for a in to_headers]
        return msg, from_addr, to_addrs

    def send_email(
        self,
        recipients: str | tuple[str, str] | list[str | tuple[str, str]],
        sender: str | tuple[str, str] = "",
        reply_to: str | tuple[str, str] = "",
        subject: str = "",
        body: str = "",
        cc: str | tuple[str, str] | Sequence[str | tuple[str, str]] | None = None,
        attachments: Sequence[str | tuple[str, bytes]] | None = None,
    ) -> None:
        with smtplib.SMTP(host=self._smtp_server, port=self._smtp_port, timeout=60) as server:
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except smtplib.SMTPException:
                # STARTTLS may be unsupported on some port 25 setups.
                pass

            if self.sender_email and self._sender_password:
                if sender:
                    raise ValueError(
                        "Cannot specify sender when using authenticated email sending."
                    )
                server.login(user=self.sender_email, password=self._sender_password)

            resolved_sender = sender or self.sender or self.sender_email
            if not resolved_sender:
                raise ValueError("A sender must be specified.")

            recipients_list = self._normalize_recipients(recipients)
            if not recipients_list and not cc:
                raise ValueError(
                    "At least one recipient (recipients or cc) must be specified."
                )

            msg, from_addr, to_addrs = self._build_message(
                sender=resolved_sender,
                reply_to=reply_to or self.reply_to,
                recipients=recipients_list,
                subject=subject,
                body=body,
                cc=cc,
                attachments=attachments,
            )

            server.sendmail(from_addr=from_addr, to_addrs=to_addrs, msg=msg.as_string())

    async def send_email_async(
        self,
        sender: str = "",
        reply_to: str | tuple[str, str] | None = None,
        recipients: str | tuple[str, str] | Sequence[str | tuple[str, str]] | None = None,
        subject: str = "",
        body: str = "",
        cc: str | tuple[str, str] | Sequence[str | tuple[str, str]] | None = None,
        attachments: Sequence[str | tuple[str, bytes]] | None = None,
    ) -> None:
        import aiosmtplib

        if self.sender_email and self._sender_password and sender:
            raise ValueError(
                "Cannot specify sender when using authenticated email sending."
            )

        resolved_sender = sender or self.sender or self.sender_email
        if not resolved_sender:
            raise ValueError("A sender must be specified.")

        recipients_list = self._normalize_recipients(recipients)
        if not recipients_list and not cc:
            raise ValueError(
                "At least one recipient (recipients or cc) must be specified."
            )

        msg, from_addr, to_addrs = self._build_message(
            sender=resolved_sender,
            reply_to=reply_to or self.reply_to,
            recipients=recipients_list,
            subject=subject,
            body=body,
            cc=cc,
            attachments=attachments,
        )

        smtp_kwargs: dict[str, object] = {
            "hostname": self._smtp_server,
            "port": self._smtp_port,
            "start_tls": True,
        }
        if self.sender_email and self._sender_password:
            smtp_kwargs["username"] = self.sender_email
            smtp_kwargs["password"] = self._sender_password

        async with aiosmtplib.SMTP(**smtp_kwargs) as server:
            await server.send_message(msg, from_addr=from_addr, to_addrs=to_addrs)


__all__ = ["EmailSender"]
