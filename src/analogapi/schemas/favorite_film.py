from pydantic import BaseModel

class FavoriteFilmBase(BaseModel):
    pass

class FavoriteFilmCreate(FavoriteFilmBase):
    film_id: int

class FavoriteFilmOut(FavoriteFilmBase):
    id: int
    user_id: int
    film_id: int

    class Config:
        from_attributes = True