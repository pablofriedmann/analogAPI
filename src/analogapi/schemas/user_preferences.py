from pydantic import BaseModel

class UserPreferencesBase(BaseModel):
    favorite_photography_type: str | None = None
    preferred_format: str | None = None
    color_preference: str | None = None

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesOut(UserPreferencesBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True