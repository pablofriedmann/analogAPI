from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    favorite_photography_type = Column(String, nullable=True)  # Ejemplo: "retrato", "paisaje", "calle"
    preferred_format = Column(String, nullable=True)  # Ejemplo: "35mm", "120"
    color_preference = Column(String, nullable=True)  # Ejemplo: "color", "b&w"

    user = relationship("User", back_populates="preferences")