from pydantic import BaseModel, ConfigDict
from typing import Optional

class FilmCreate(BaseModel):
    brand: str
    name: str
    format: str
    type: str
    iso: int
    grain: Optional[str] = None
    

class FilmOut(FilmCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)