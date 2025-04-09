from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from analogapi.database import SessionLocal
from analogapi.models.film import Film
from analogapi.models.tag import Tag
from analogapi.schemas.film import FilmCreate, FilmOut

router = APIRouter(prefix="/films", tags=["films"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATES FILM
@router.post("/", response_model=FilmOut)
def create_film(film: FilmCreate, db: Session = Depends(get_db)):
    db_film = Film(**film.model_dump(exclude={"tag_ids"}))
    
    if film.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(film.tag_ids)).all()
        if len(tags) != len(film.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")
        db_film.tags = tags
    
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film

# GET ALL FILM STOCK
@router.get("/", response_model=list[FilmOut])
def get_all_films(db: Session = Depends(get_db)):
    films = db.query(Film).all()
    return films

# GET FILM BY ID
@router.get("/{film_id}", response_model=FilmOut)
def get_film_by_id(film_id: int, db: Session = Depends(get_db)):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        raise HTTPException(status_code=404, detail="Film stock not found")
    return db_film

# EDIT FILM
@router.put("/{film_id}", response_model=FilmOut)
def edit_film(film_id: int, film: FilmCreate, db: Session = Depends(get_db)):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        raise HTTPException(status_code=404, detail="Film stock not found")
    
    for key, value in film.model_dump(exclude={"tag_ids"}).items():
        setattr(db_film, key, value)
    
    if film.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(film.tag_ids)).all()
        if len(tags) != len(film.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")
        db_film.tags = tags
    
    db.commit()
    db.refresh(db_film)
    return db_film

# DELETES FILM STOCK
@router.delete("/{film_id}", response_model=dict)
def delete_film(film_id: int, db: Session = Depends(get_db)):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        raise HTTPException(status_code=404, detail="Film stock not found")
    
    db.delete(db_film)
    db.commit()
    return {"message": f"Film stock with id {film_id} deleted successfully"}