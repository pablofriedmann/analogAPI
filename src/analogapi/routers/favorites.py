# src/analogapi/routers/favorites.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import select, delete
from ..database import get_db
from ..models.user import User
from ..models.camera import Camera, favorite_cameras
from ..models.film import Film, favorite_films 
from ..schemas.favorite_camera import FavoriteCameraCreate, FavoriteCameraOut
from ..schemas.favorite_film import FavoriteFilmCreate, FavoriteFilmOut

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"],
    responses={404: {"description": "Not found"}},
)

@router.post("/cameras/{camera_id}", response_model=FavoriteCameraOut)
def add_favorite_camera(camera_id: int, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    query = select(favorite_cameras).where(
        favorite_cameras.c.user_id == user_id,
        favorite_cameras.c.camera_id == camera_id
    )
    favorite = db.execute(query).fetchone()
    if favorite:
        raise HTTPException(status_code=400, detail="Camera already in favorites")

    insert_stmt = favorite_cameras.insert().values(user_id=user_id, camera_id=camera_id)
    result = db.execute(insert_stmt)
    db.commit()

    return {"id": result.inserted_primary_key[0] if result.inserted_primary_key else None, "user_id": user_id, "camera_id": camera_id}

@router.post("/films/{film_id}", response_model=FavoriteFilmOut)
def add_favorite_film(film_id: int, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    film = db.query(Film).filter(Film.id == film_id).first()
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")

    query = select(favorite_films).where(
        favorite_films.c.user_id == user_id,
        favorite_films.c.film_id == film_id
    )
    favorite = db.execute(query).fetchone()
    if favorite:
        raise HTTPException(status_code=400, detail="Film already in favorites")

    insert_stmt = favorite_films.insert().values(user_id=user_id, film_id=film_id)
    result = db.execute(insert_stmt)
    db.commit()

    return {"id": result.inserted_primary_key[0] if result.inserted_primary_key else None, "user_id": user_id, "film_id": film_id}

@router.delete("/cameras/{camera_id}")
def remove_favorite_camera(camera_id: int, user_id: int, db: Session = Depends(get_db)):
    query = select(favorite_cameras).where(
        favorite_cameras.c.user_id == user_id,
        favorite_cameras.c.camera_id == camera_id
    )
    favorite = db.execute(query).fetchone()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite camera not found")

    delete_stmt = delete(favorite_cameras).where(
        favorite_cameras.c.user_id == user_id,
        favorite_cameras.c.camera_id == camera_id
    )
    db.execute(delete_stmt)
    db.commit()
    return {"message": "Camera removed from favorites"}

@router.delete("/films/{film_id}")
def remove_favorite_film(film_id: int, user_id: int, db: Session = Depends(get_db)):
    query = select(favorite_films).where(
        favorite_films.c.user_id == user_id,
        favorite_films.c.film_id == film_id
    )
    favorite = db.execute(query).fetchone()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite film not found")

    delete_stmt = delete(favorite_films).where(
        favorite_films.c.user_id == user_id,
        favorite_films.c.film_id == film_id
    )
    db.execute(delete_stmt)
    db.commit()
    return {"message": "Film removed from favorites"}