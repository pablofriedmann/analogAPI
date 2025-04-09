from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .tag import TagOut

class FilmCreate(BaseModel):
    brand: str
    name: str
    format: str
    type: str
    iso: int
    grain: Optional[str] = None
    tag_ids: Optional[List[int]] = None
    

class FilmOut(FilmCreate):
    id: int
    tags: List[TagOut] = []

    model_config = ConfigDict(from_attributes=True)