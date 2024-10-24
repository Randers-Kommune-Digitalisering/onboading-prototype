from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Forløbsskabelon(Base):
    __tablename__ = 'Forløbsskabelon'
    ForløbsskabelonID = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    varighed = Column(DateTime, nullable=False)
    opgaver = relationship('Opgaver', back_populates='forløbsskabelon')


class Forløb(Base):
    __tablename__ = 'Forløb'
    ForløbID = Column(Integer, primary_key=True, autoincrement=True)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    admin = Column(String)
    usermail = Column(String)
    userdq = Column(String)
    opgaver = relationship('Opgaver', back_populates='forløb')


class Opgaver(Base):
    __tablename__ = 'Opgaver'
    OpgaverID = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    beskrivelse = Column(String, nullable=False)
    resourcer = Column(String, nullable=False)
    ansvarlig = Column(String, nullable=False)
    startdato = Column(DateTime, nullable=False)
    slutdato = Column(DateTime, nullable=False)
    result = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    ForløbsskabelonID = Column(Integer, ForeignKey('Forløbsskabelon.ForløbsskabelonID'))
    forløbsskabelon = relationship('Forløbsskabelon', back_populates='opgaver')
    ForløbID = Column(Integer, ForeignKey('Forløb.ForløbID'))
    forløb = relationship('Forløb', back_populates='opgaver')