from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)