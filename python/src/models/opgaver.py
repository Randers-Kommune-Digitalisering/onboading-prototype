from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Opgaver(Base):
    __tablename__ = 'Opgaver'
    OpgaverID = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    beskrivelse = Column(String)
    resourcer = Column(String)
    ansvarlig = Column(String)
    startdato = Column(DateTime)
    slutdato = Column(DateTime)
    result = Column(Boolean)
    timestamp = Column(DateTime)
