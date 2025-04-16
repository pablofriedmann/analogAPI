from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    favorite_cameras = relationship("Camera", secondary="favorite_cameras", back_populates="favorite_users")
    favorite_films = relationship("Film", secondary="favorite_films", back_populates="favorite_users")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)