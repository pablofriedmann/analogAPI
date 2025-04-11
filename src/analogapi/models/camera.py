from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base
from ..tables import camera_tags

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    format = Column(String, nullable=False)
    type = Column(String, nullable=False)
    years = Column(String, nullable=True)
    lens_mount = Column(String, nullable=True)

    tags = relationship("Tag", secondary=camera_tags, back_populates="cameras")
    favorited_by = relationship("FavoriteCamera", back_populates="camera")