from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .tag import TagOut

class CameraCreate(BaseModel):
    brand: str
    model: str
    format: str
    type: str
    years: Optional[str] = None
    lens_mount: str
    tag_ids: Optional[List[int]] = None

class CameraOut(CameraCreate):
    id: int
    tags: List[TagOut] = []

    model_config = ConfigDict(from_attributes=True)