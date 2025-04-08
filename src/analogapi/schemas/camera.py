from pydantic import BaseModel, ConfigDict
from typing import Optional

class CameraCreate(BaseModel):
    brand: str
    model: str
    format: Optional[str] = None
    type: Optional[str] = None
    years: Optional[str] = None
    lens_mount: Optional[str] = None
    notes: Optional[str] = None

class CameraOut(CameraCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)