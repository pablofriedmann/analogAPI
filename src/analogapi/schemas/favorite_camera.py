from pydantic import BaseModel

class FavoriteCameraBase(BaseModel):
    pass

class FavoriteCameraCreate(FavoriteCameraBase):
    camera_id: int

class FavoriteCameraOut(FavoriteCameraBase):
    id: int
    user_id: int
    camera_id: int

    class Config:
        from_attributes = True