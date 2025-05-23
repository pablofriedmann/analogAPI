from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

camera_tags = Table(
    "camera_tags",
    Base.metadata,
    Column("camera_id", Integer, ForeignKey("cameras.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

film_tags = Table(
    "film_tags",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    cameras = relationship("Camera", secondary=camera_tags, back_populates="tags")
    films = relationship("Film", secondary=film_tags, back_populates="tags")