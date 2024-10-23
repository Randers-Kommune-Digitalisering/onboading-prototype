from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from models.base import Base


class Forløbsskabelon(Base):
    __tablename__ = 'Forløbsskabelon'
    ForløbsskabelonID = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    varighed = Column(DateTime, nullable=False)
    opgaver = relationship('Opgaver', back_populates='forløbsskabelon')
