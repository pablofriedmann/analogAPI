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

# CREATES CAMERA
@router.post("/", response_model=CameraOut)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

# GET ALL CAMERAS
@router.get("/", response_model=list[CameraOut])
def get_all_cameras(db: Session = Depends(get_db)):
    cameras = db.query(Camera).all()
    return cameras

# GET CAMERA BY ID
@router.get("/{camera_id}", response_model=CameraOut)
def get_camera_by_id(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

# EDIT CAMERA
@router.put("/{camera_id}", response_model=CameraOut)
def edit_camera(camera_id: int, camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    for key, value in camera.model_dump().items():
        setattr(db_camera, key, value)
    
    db.commit()
    db.refresh(db_camera)
    return db_camera

# DELETES CAMERA
@router.delete("/{camera_id}", response_model=dict)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db.delete(db_camera)
    db.commit()
    return {"message": f"Camera with id {camera_id} deleted successfully"}