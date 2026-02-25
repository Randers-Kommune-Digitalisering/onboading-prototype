from datetime import datetime

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from python.src.models import Base, Mail, MailAttachment
from python.src.utils import mail_service


class _TestDbClient:
    def __init__(self, engine):
        self.engine = engine

    def get_session(self):
        return Session(self.engine)


def test_delete_planned_mail_deletes_attachments(monkeypatch):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    test_db_client = _TestDbClient(engine)
    monkeypatch.setattr(mail_service, "db_client", test_db_client)

    # Seed: one unsent mail with one attachment
    session = test_db_client.get_session()
    mail = Mail(
        created=datetime.now(),
        subject="Subject",
        body="Body",
        recipient="someone@example.com",
        isSent=False,
    )
    mail.attachments.append(MailAttachment(filename="a.txt", file_data="ZGF0YQ=="))
    session.add(mail)
    session.commit()
    mail_id = mail.MailID
    session.close()

    # Call under a Flask app context (jsonify requires it)
    app = Flask(__name__)
    with app.app_context():
        _, status = mail_service.delete_planned_mail(mail_id)
        assert status == 200

    # Verify both mail and attachments are gone
    session = test_db_client.get_session()
    assert session.query(Mail).filter_by(MailID=mail_id).first() is None
    assert session.query(MailAttachment).filter_by(MailID=mail_id).count() == 0
    session.close()
