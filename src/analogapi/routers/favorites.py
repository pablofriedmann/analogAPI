from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..auth import get_current_user, get_db
from ..models.user import User
from ..models.favorite_camera import FavoriteCamera
from ..models.favorite_film import FavoriteFilm
from ..schemas.favorite_camera import FavoriteCameraCreate, FavoriteCameraOut
from ..schemas.favorite_film import FavoriteFilmCreate, FavoriteFilmOut

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"],
    responses={404: {"description": "Not found"}},
)

# PICKS FAVORITE CAMERA
@router.post("/cameras/{camera_id}", response_model=FavoriteCameraOut, status_code=status.HTTP_201_CREATED)
def add_favorite_camera(camera_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_favorite = db.query(FavoriteCamera).filter(
        FavoriteCamera.user_id == current_user.id,
        FavoriteCamera.camera_id == camera_id
    ).first()
    if existing_favorite:
        raise HTTPException(status_code=400, detail="Camera already in favorites")

    favorite = FavoriteCamera(user_id=current_user.id, camera_id=camera_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

# DELETES FAVORITE CAMERA
@router.delete("/cameras/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite_camera(camera_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorite = db.query(FavoriteCamera).filter(
        FavoriteCamera.user_id == current_user.id,
        FavoriteCamera.camera_id == camera_id
    ).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Camera not in favorites")

    db.delete(favorite)
    db.commit()
    return

# GET FAVORITE CAMERA
@router.get("/cameras", response_model=List[FavoriteCameraOut])
def get_favorite_cameras(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorites = db.query(FavoriteCamera).filter(FavoriteCamera.user_id == current_user.id).all()
    return favorites

# PICK FAVORITE FILM
@router.post("/films/{film_id}", response_model=FavoriteFilmOut, status_code=status.HTTP_201_CREATED)
def add_favorite_film(film_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_favorite = db.query(FavoriteFilm).filter(
        FavoriteFilm.user_id == current_user.id,
        FavoriteFilm.film_id == film_id
    ).first()
    if existing_favorite:
        raise HTTPException(status_code=400, detail="Film already in favorites")

    favorite = FavoriteFilm(user_id=current_user.id, film_id=film_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

# DELETE FAVORITE FILM
@router.delete("/films/{film_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite_film(film_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorite = db.query(FavoriteFilm).filter(
        FavoriteFilm.user_id == current_user.id,
        FavoriteFilm.film_id == film_id
    ).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Film not in favorites")

    db.delete(favorite)
    db.commit()
    return

# GET FAVORITE FILM
@router.get("/films", response_model=List[FavoriteFilmOut])
def get_favorite_films(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorites = db.query(FavoriteFilm).filter(FavoriteFilm.user_id == current_user.id).all()
    return favorites