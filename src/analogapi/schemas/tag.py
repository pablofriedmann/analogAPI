from pydantic import BaseModel, ConfigDict
from typing import Optional

class TagCreate(BaseModel):
    name: str

class TagOut(TagCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)