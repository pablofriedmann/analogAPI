from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class FavoriteCamera(Base):
    __tablename__ = "favorite_cameras"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)

    user = relationship("User", back_populates="favorite_cameras")
    camera = relationship("Camera", back_populates="favorited_by")