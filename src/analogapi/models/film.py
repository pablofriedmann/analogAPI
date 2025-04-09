from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from analogapi.base import Base

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    name = Column(String, nullable=False)
    format = Column(String, nullable=False)
    type = Column(String, nullable=False)
    iso = Column(Integer, nullable=False)
    grain = Column(String)

    tags = relationship("Tag", secondary="film_tags", back_populates="films")