from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class FavoriteFilm(Base):
    __tablename__ = "favorite_films"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    film_id = Column(Integer, ForeignKey("films.id"), nullable=False)

    user = relationship("User", back_populates="favorite_films")
    film = relationship("Film", back_populates="favorited_by")