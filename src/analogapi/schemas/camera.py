from pydantic import BaseModel, ConfigDict
from typing import Optional

class CameraCreate(BaseModel):
    brand: str
    model: str
    format: str
    type: str
    years: Optional[str] = None
    lens_mount: str
    

class CameraOut(CameraCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)