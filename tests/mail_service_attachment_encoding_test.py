import base64
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, Mail, MailAttachment
from controllers import mail_controller as mail_service


class _TestDbClient:
    def __init__(self, engine):
        self.engine = engine

    def get_session(self):
        return Session(self.engine)


def test_plan_mail_encodes_bytes_attachment_to_base64(monkeypatch):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    test_db_client = _TestDbClient(engine)
    monkeypatch.setattr(mail_service, "db_client", test_db_client)

    raw = b"hello"
    attachment = {"filename": "greeting.txt", "content": raw}

    mail_service.plan_mail(
        recipient_email="someone@example.com",
        subject="Subject",
        message="Body",
        attachment=attachment,
    )

    session = test_db_client.get_session()
    stored = session.query(MailAttachment).first()
    assert stored is not None
    assert isinstance(stored.file_data, str)
    assert stored.file_data == base64.b64encode(raw).decode("ascii")
    session.close()


def test_plan_mail_keeps_string_attachment_as_is(monkeypatch):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    test_db_client = _TestDbClient(engine)
    monkeypatch.setattr(mail_service, "db_client", test_db_client)

    b64 = base64.b64encode(b"data").decode("ascii")
    attachment = {"filename": "a.bin", "content": b64}

    mail_service.plan_mail(
        recipient_email="someone@example.com",
        subject="Subject",
        message="Body",
        attachment=attachment,
    )

    session = test_db_client.get_session()
    stored = session.query(MailAttachment).first()
    assert stored is not None
    assert stored.file_data == b64
    session.close()


def test_get_planned_mails_normalizes_legacy_bytes_in_db(monkeypatch):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    test_db_client = _TestDbClient(engine)
    monkeypatch.setattr(mail_service, "db_client", test_db_client)

    raw = b"legacy"
    session = test_db_client.get_session()
    mail = Mail(
        created=datetime.now(),
        subject="Subject",
        body="Body",
        recipient="someone@example.com",
        isSent=False,
    )
    mail.attachments.append(MailAttachment(filename="x.bin", file_data=raw))
    session.add(mail)
    session.commit()
    session.close()

    mails = mail_service.get_planned_mails()
    assert len(mails) == 1
    assert len(mails[0]["attachments"]) == 1
    assert mails[0]["attachments"][0]["file_data"] == base64.b64encode(raw).decode("ascii")


def test_send_mail_transports_attachments_as_json_byte_array(monkeypatch):
    captured = {"init": None, "send": None}

    class _FakeEmailSender:
        def __init__(
            self,
            smtp_server=None,
            smtp_port=None,
            sender_email=None,
            sender_password=None,
            sender_name=None,
            reply_to_email=None,
            reply_to_name=None,
        ):
            captured["init"] = {
                "smtp_server": smtp_server,
                "smtp_port": smtp_port,
                "sender_email": sender_email,
                "sender_password": sender_password,
                "sender_name": sender_name,
                "reply_to_email": reply_to_email,
                "reply_to_name": reply_to_name,
            }

        def send_email(self, **kwargs):
            captured["send"] = kwargs

    monkeypatch.setattr(mail_service, "MAIL_SMTP_SERVER", "smtp.test")
    monkeypatch.setattr(mail_service, "MAIL_SMTP_PORT", 25)
    monkeypatch.setattr(mail_service, "MAIL_SMTP_SENDER", "sender@example.com")
    monkeypatch.setattr(mail_service, "MAIL_SMTP_PASSWORD", "secret")
    monkeypatch.setattr(mail_service, "EmailSender", _FakeEmailSender)

    raw = b"ABC"
    b64 = base64.b64encode(raw).decode("ascii")
    ok = mail_service.send_mail(
        "to@example.com",
        "Subject",
        "Body",
        attachments=[{"filename": "a.bin", "file_data": b64}],
    )
    assert ok is True

    assert captured["init"]["smtp_server"] == "smtp.test"
    assert captured["init"]["smtp_port"] == 25
    assert captured["init"]["sender_email"] == "sender@example.com"
    assert captured["init"]["sender_password"] == "secret"
    assert captured["send"]["recipients"] == "to@example.com"
    assert captured["send"]["subject"] == "Subject"
    assert captured["send"]["body"] == "Body"
    assert captured["send"]["attachments"] == [("a.bin", raw)]
