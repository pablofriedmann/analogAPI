from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class FilmBase(BaseModel):
    brand: str
    name: str
    format: str
    type: str
    iso: int = Field(..., gt=0) 
    grain: str

class FilmCreate(FilmBase):
    tag_ids: Optional[List[int]] = None

class FilmOut(FilmBase):
    id: int
    tags: List["TagOut"] = []

    model_config = ConfigDict(from_attributes=True)

from .tag import TagOut
FilmOut.model_rebuild()