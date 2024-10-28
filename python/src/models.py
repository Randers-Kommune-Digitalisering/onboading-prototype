from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Forløbsskabelon(Base):
    __tablename__ = 'Forløbsskabelon'
    ForløbsskabelonID = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    varighed = Column(DateTime, nullable=False)
    opgave = relationship('Opgave', back_populates='forløbsskabelon')


class Forløb(Base):
    __tablename__ = 'Forløb'
    ForløbID = Column(Integer, primary_key=True, autoincrement=True)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    admin = Column(String)
    usermail = Column(String)
    userdq = Column(String)
    opgave = relationship('Opgave', back_populates='forløb')


class Opgaveskabelon(Base):
    __tablename__ = 'Opgaveskabelon'
    OpgaveskabelonID = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    beskrivelse = Column(String, nullable=False)
    ressource = relationship('Ressource', back_populates='opgaveskabelon')
    startdato = Column(DateTime, nullable=False)
    slutdato = Column(DateTime, nullable=False)


class Opgave(Base):
    __tablename__ = 'Opgave'
    OpgaveID = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    beskrivelse = Column(String, nullable=False)
    ansvarlig = Column(String, nullable=False)
    startdato = Column(DateTime, nullable=False)
    slutdato = Column(DateTime, nullable=False)
    result = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    ForløbsskabelonID = Column(Integer, ForeignKey('Forløbsskabelon.ForløbsskabelonID'))
    forløbsskabelon = relationship('Forløbsskabelon', back_populates='opgave')
    ForløbID = Column(Integer, ForeignKey('Forløb.ForløbID'))
    forløb = relationship('Forløb', back_populates='opgave')
    ressource = relationship('Ressource', back_populates='opgave')


class Ressource(Base):
    __tablename__ = 'Ressource'
    RessourceID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    OpgaveID = Column(Integer, ForeignKey('Opgave.OpgaveID'))
    opgave = relationship('Opgave', back_populates='ressource')
    OpgaveskabelonID = Column(Integer, ForeignKey('Opgaveskabelon.OpgaveskabelonID'))
    opgaveskabelon = relationship('Opgaveskabelon', back_populates='ressource')
