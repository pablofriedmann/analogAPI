from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base
from .tables import film_tags, favorite_films

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    name = Column(String, nullable=False)
    iso = Column(Integer)
    format = Column(String)
    color = Column(String)
    source_url = Column(String)

    tags = relationship("Tag", secondary=film_tags, back_populates="films")
    favorite_users = relationship("User", secondary=favorite_films, back_populates="favorite_films")