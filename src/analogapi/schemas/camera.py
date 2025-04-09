from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class CameraBase(BaseModel):
    brand: str
    model: str
    format: str
    type: str
    years: str
    lens_mount: str

class CameraCreate(CameraBase):
    tag_ids: Optional[List[int]] = None

class CameraOut(CameraBase):
    id: int
    tags: List["TagOut"] = []

    model_config = ConfigDict(from_attributes=True)

from .tag import TagOut
CameraOut.model_rebuild()