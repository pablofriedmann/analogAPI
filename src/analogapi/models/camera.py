from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base
from datetime import datetime

favorite_cameras = Table(
    "favorite_cameras",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("camera_id", Integer, ForeignKey("cameras.id"), primary_key=True)
)

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    format = Column(String)
    type = Column(String)
    years = Column(String)
    lens_mount = Column(String)
    source_url = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    tags = relationship("Tag", secondary="camera_tags", back_populates="cameras")
    favorite_users = relationship("User", secondary=favorite_cameras, back_populates="favorite_cameras")