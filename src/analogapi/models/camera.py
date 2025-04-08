from sqlalchemy import Column, Integer, String
from analogapi.database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    format = Column(String)
    type = Column(String)
    years = Column(String)
    lens_mount = Column(String)
    notes = Column(String)