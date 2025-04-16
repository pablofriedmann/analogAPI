# src/analogapi/models/film.py
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base
from datetime import datetime

favorite_films = Table(
    "favorite_films",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True)
)

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    name = Column(String, nullable=False)
    iso = Column(Integer)
    format = Column(String)
    color = Column(String)
    grain = Column(String)
    source_url = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    tags = relationship("Tag", secondary="film_tags", back_populates="films")
    favorite_users = relationship("User", secondary=favorite_films, back_populates="favorite_films")