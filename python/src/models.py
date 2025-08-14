from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Forløbsskabelon(Base):
    __tablename__ = 'Forløbsskabelon'
    ForløbsskabelonID = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    varighed = Column(Integer, nullable=False)
    opgave = relationship('Opgave', back_populates='forløbsskabelon')


class Forløb(Base):
    __tablename__ = 'Forløb'
    ForløbID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    startdate = Column(DateTime, nullable=False)
    enddate = Column(DateTime, nullable=False)
    admin = Column(String, nullable=False)
    usermail = Column(String, nullable=False)
    userdq = Column(String, nullable=False)
    opgave = relationship('Opgave', back_populates='forløb')


class Opgaveskabelon(Base):
    __tablename__ = 'Opgaveskabelon'
    OpgaveskabelonID = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    beskrivelse = Column(String, nullable=False)
    note = Column(String, nullable=True)
    ressource = relationship('Ressource', back_populates='opgaveskabelon')
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
    ForløbsskabelonID = Column(Integer, ForeignKey('Forløbsskabelon.ForløbsskabelonID'))
    forløbsskabelon = relationship('Forløbsskabelon', back_populates='opgave')
    ForløbID = Column(Integer, ForeignKey('Forløb.ForløbID'))
    forløb = relationship('Forløb', back_populates='opgave')
    ressource = relationship('Ressource', back_populates='opgave')
    OpgaveGruppeID = Column(Integer, ForeignKey('OpgaveGruppe.OpgaveGruppeID'))
    opgavegruppe = relationship('OpgaveGruppe', back_populates='opgaver')
    note = Column(String, nullable=True)


class Ressource(Base):
    __tablename__ = 'Ressource'
    RessourceID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    OpgaveID = Column(Integer, ForeignKey('Opgave.OpgaveID'))
    opgave = relationship('Opgave', back_populates='ressource')
    OpgaveskabelonID = Column(Integer, ForeignKey('Opgaveskabelon.OpgaveskabelonID'))
    opgaveskabelon = relationship('Opgaveskabelon', back_populates='ressource')


class OpgaveGruppe(Base):
    __tablename__ = 'OpgaveGruppe'
    OpgaveGruppeID = Column(Integer, primary_key=True, autoincrement=True)
    ForløbID = Column(Integer, ForeignKey('Forløb.ForløbID'))
    ForløbsskabelonID = Column(Integer, ForeignKey('Forløbsskabelon.ForløbsskabelonID'))
    name = Column(String, nullable=False)
    letter = Column(String, nullable=False)
    opgaver = relationship("Opgave", back_populates="opgavegruppe")
