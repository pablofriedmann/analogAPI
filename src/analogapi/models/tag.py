from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base 
from ..tables import camera_tags, film_tags

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    cameras = relationship("Camera", secondary=camera_tags, back_populates="tags")
    films = relationship("Film", secondary=film_tags, back_populates="tags")