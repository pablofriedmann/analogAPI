from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base
from ..tables import film_tags

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    name = Column(String, nullable=False)
    format = Column(String, nullable=False)
    type = Column(String, nullable=False)
    iso = Column(Integer, nullable=False)
    grain = Column(String, nullable=True)

    tags = relationship("Tag", secondary=film_tags, back_populates="films")
    favorited_by = relationship("FavoriteFilm", back_populates="film")