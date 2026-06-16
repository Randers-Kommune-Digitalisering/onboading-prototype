from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Forløbsskabelon(Base):
    __tablename__ = 'Forløbsskabelon'
    ForløbsskabelonID = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    varighed = Column(Integer, nullable=False)
    opgave = relationship('Opgave', back_populates='forløbsskabelon', cascade='all, delete')
    opgave_grupper = relationship('OpgaveGruppe', back_populates='forløbsskabelon', cascade='all, delete')


class Forløb(Base):
    __tablename__ = 'Forløb'
    ForløbID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    startdate = Column(DateTime, nullable=True)
    enddate = Column(DateTime, nullable=True)
    varighed = Column(Integer, nullable=True)
    admin = Column(String, nullable=False)
    usermail = Column(String, nullable=False)
    userdq = Column(String, nullable=False)
    opgave_grupper = relationship('OpgaveGruppe', back_populates='forløb', cascade='all, delete')
    opgave = relationship('Opgave', back_populates='forløb', cascade='all, delete')
    mails = relationship('Mail', back_populates='forløb', cascade='all, delete')
    isPreparation = Column(Boolean, default=True)

    # External (public) access via one-time emailed magic link.
    # Store only a hash (never the raw key) + an expiry timestamp.
    external_access_key_hash = Column(String, nullable=True)
    external_access_expires_at = Column(DateTime, nullable=True)


class Opgaveskabelon(Base):
    __tablename__ = 'Opgaveskabelon'
    OpgaveskabelonID = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    beskrivelse = Column(String, nullable=False)
    note = Column(String, nullable=True)
    ressource = relationship('Ressource', back_populates='opgaveskabelon', cascade='all, delete')
    relativ_slutdag = Column(Integer, nullable=False)


class Opgave(Base):
    __tablename__ = 'Opgave'
    OpgaveID = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    beskrivelse = Column(String, nullable=False)
    ansvarlig = Column(String, nullable=False)
    ansvarligEmail = Column(String, nullable=False)
    startdato = Column(DateTime)
    slutdato = Column(DateTime)
    relativ_startdag = Column(Integer)
    relativ_slutdag = Column(Integer)
    result = Column(Boolean, nullable=False)
    booking = Column(DateTime)
    timestamp = Column(DateTime, nullable=False)
    ForløbsskabelonID = Column(Integer, ForeignKey('Forløbsskabelon.ForløbsskabelonID', ondelete='CASCADE'))
    forløbsskabelon = relationship('Forløbsskabelon', back_populates='opgave')
    ForløbID = Column(Integer, ForeignKey('Forløb.ForløbID', ondelete='CASCADE'))
    forløb = relationship('Forløb', back_populates='opgave')
    ressource = relationship('Ressource', back_populates='opgave', cascade='all, delete')
    OpgaveGruppeID = Column(Integer, ForeignKey('OpgaveGruppe.OpgaveGruppeID', ondelete='CASCADE'))
    opgavegruppe = relationship('OpgaveGruppe', back_populates='opgave')
    note = Column(String, nullable=True)
    mails = relationship('Mail', back_populates='opgave', cascade='all, delete')


class Ressource(Base):
    __tablename__ = 'Ressource'
    RessourceID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    # When true, this resource is backed by an uploaded file (see RessourceFile).
    # Keep `url` as a non-nullable column for backwards compatibility with the
    # current lightweight DB migration approach (add-missing-columns only).
    isFile = Column(Boolean, default=False)
    OpgaveID = Column(Integer, ForeignKey('Opgave.OpgaveID', ondelete='CASCADE'))
    opgave = relationship('Opgave', back_populates='ressource')
    OpgaveskabelonID = Column(Integer, ForeignKey('Opgaveskabelon.OpgaveskabelonID', ondelete='CASCADE'))
    opgaveskabelon = relationship('Opgaveskabelon', back_populates='ressource')
    file = relationship(
        'RessourceFile',
        back_populates='ressource',
        uselist=False,
        cascade='all, delete-orphan',
    )


class RessourceFile(Base):
    __tablename__ = 'RessourceFile'
    # One-to-one with Ressource; use RessourceID as both PK and FK.
    RessourceID = Column(
        Integer,
        ForeignKey('Ressource.RessourceID', ondelete='CASCADE'),
        primary_key=True,
    )
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    ressource = relationship('Ressource', back_populates='file')


class OpgaveGruppe(Base):
    __tablename__ = 'OpgaveGruppe'
    OpgaveGruppeID = Column(Integer, primary_key=True, autoincrement=True)
    ForløbID = Column(Integer, ForeignKey('Forløb.ForløbID', ondelete='CASCADE'))
    forløb = relationship('Forløb', back_populates='opgave_grupper')
    ForløbsskabelonID = Column(Integer, ForeignKey('Forløbsskabelon.ForløbsskabelonID', ondelete='CASCADE'))
    forløbsskabelon = relationship('Forløbsskabelon', back_populates='opgave_grupper')
    name = Column(String, nullable=False)
    letter = Column(String, nullable=False)
    opgave = relationship("Opgave", back_populates="opgavegruppe", cascade='all, delete')


class Mail(Base):
    __tablename__ = 'Mail'
    MailID = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    isSent = Column(Boolean, default=False)
    sent = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    OpgaveID = Column(Integer, ForeignKey('Opgave.OpgaveID', ondelete='CASCADE'), nullable=True)
    opgave = relationship('Opgave', back_populates='mails')
    ForløbID = Column(Integer, ForeignKey('Forløb.ForløbID', ondelete='CASCADE'), nullable=True)
    forløb = relationship('Forløb', back_populates='mails')
    attachments = relationship(
        'MailAttachment',
        back_populates='mail',
        cascade='all, delete-orphan',
    )


class MailAttachment(Base):
    __tablename__ = 'MailAttachment'
    AttachmentID = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    file_data = Column(String, nullable=False)  # Store file data as base64 encoded string
    MailID = Column(Integer, ForeignKey('Mail.MailID', ondelete='CASCADE'), nullable=False)
    mail = relationship('Mail', back_populates='attachments')
