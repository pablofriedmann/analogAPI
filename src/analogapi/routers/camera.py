from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from analogapi.database import SessionLocal
from analogapi.models.camera import Camera
from analogapi.schemas.camera import CameraCreate, CameraOut

router = APIRouter(prefix="/cameras", tags=["cameras"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CameraOut)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = Camera(**camera.dict())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.get("/{camera_id}", response_model=CameraOut)
def read_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera