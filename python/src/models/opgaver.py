from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


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
