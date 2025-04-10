from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import SessionLocal
from ..models.camera import Camera
from ..models.film import Film
from ..schemas.camera import CameraCreate, CameraOut
from ..schemas.film import FilmOut

router = APIRouter(
    prefix="/cameras",
    tags=["cameras"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATES CAMERA
@router.post("/", response_model=CameraOut)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    if camera.tag_ids:
        existing_tags = db.query(Tag).filter(Tag.id.in_(camera.tag_ids)).count()
        if existing_tags != len(camera.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")

    db_camera = Camera(**camera.model_dump(exclude={"tag_ids"}))
    if camera.tag_ids:
        db_camera.tags = db.query(Tag).filter(Tag.id.in_(camera.tag_ids)).all()
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

# GET ALL CAMERAS
@router.get("/", response_model=List[CameraOut])
def get_all_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()

# GET CAMERA BY ID
@router.get("/{camera_id}", response_model=CameraOut)
def get_camera_by_id(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

# EDIT CAMERA
@router.put("/{camera_id}", response_model=CameraOut)
def update_camera(camera_id: int, camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    if camera.tag_ids:
        existing_tags = db.query(Tag).filter(Tag.id.in_(camera.tag_ids)).count()
        if existing_tags != len(camera.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")

    for key, value in camera.model_dump(exclude={"tag_ids"}).items():
        setattr(db_camera, key, value)
    if camera.tag_ids:
        db_camera.tags = db.query(Tag).filter(Tag.id.in_(camera.tag_ids)).all()
    db.commit()
    db.refresh(db_camera)
    return db_camera

# DELETE CAMERA
@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    db.delete(db_camera)
    db.commit()
    return {"message": f"Camera with id {camera_id} deleted successfully"}

# GET COMPATIBLE FILMS/CAMERAS
@router.get("/{camera_id}/compatible-films", response_model=List[FilmOut])
def get_compatible_films(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")


    compatible_films = db.query(Film).filter(Film.format == db_camera.format).all()
    return compatible_films

# IMPORT TAGS
from ..models.tag import Tag