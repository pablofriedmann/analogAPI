from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    favorite_cameras = relationship("FavoriteCamera", back_populates="user")
    favorite_films = relationship("FavoriteFilm", back_populates="user")