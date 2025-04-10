from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_session 
from ..models.film import Film
from ..models.camera import Camera
from ..schemas.film import FilmCreate, FilmOut
from ..schemas.camera import CameraOut

router = APIRouter(
    prefix="/films",
    tags=["films"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = get_session()() 
    try:
        yield db
    finally:
        db.close()

# CREATES FILM
@router.post("/", response_model=FilmOut)
def create_film(film: FilmCreate, db: Session = Depends(get_db)):
    if film.tag_ids:
        existing_tags = db.query(Tag).filter(Tag.id.in_(film.tag_ids)).count()
        if existing_tags != len(film.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")

    db_film = Film(**film.model_dump(exclude={"tag_ids"}))
    if film.tag_ids:
        db_film.tags = db.query(Tag).filter(Tag.id.in_(film.tag_ids)).all()
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film

# GET ALL FILM STOCK
@router.get("/", response_model=List[FilmOut])
def get_all_films(db: Session = Depends(get_db)):
    return db.query(Film).all()

# GET FILM BY ID
@router.get("/{film_id}", response_model=FilmOut)
def get_film_by_id(film_id: int, db: Session = Depends(get_db)):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        raise HTTPException(status_code=404, detail="Film stock not found")
    return db_film

# EDIT FILMS
@router.put("/{film_id}", response_model=FilmOut)
def update_film(film_id: int, film: FilmCreate, db: Session = Depends(get_db)):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        raise HTTPException(status_code=404, detail="Film stock not found")

    if film.tag_ids:
        existing_tags = db.query(Tag).filter(Tag.id.in_(film.tag_ids)).count()
        if existing_tags != len(film.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")

    for key, value in film.model_dump(exclude={"tag_ids"}).items():
        setattr(db_film, key, value)
    if film.tag_ids:
        db_film.tags = db.query(Tag).filter(Tag.id.in_(film.tag_ids)).all()
    db.commit()
    db.refresh(db_film)
    return db_film

# DELETE FILM
@router.delete("/{film_id}")
def delete_film(film_id: int, db: Session = Depends(get_db)):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        raise HTTPException(status_code=404, detail="Film stock not found")
    db.delete(db_film)
    db.commit()
    return {"message": f"Film stock with id {film_id} deleted successfully"}

# GET COMPATIBLE CAMERA/FILM
@router.get("/{film_id}/compatible-cameras", response_model=List[CameraOut])
def get_compatible_cameras(film_id: int, db: Session = Depends(get_db)):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        raise HTTPException(status_code=404, detail="Film stock not found")

    compatible_cameras = db.query(Camera).filter(Camera.format == db_film.format).all()
    return compatible_cameras

# IMPORT TAGS
from ..models.tag import Tag