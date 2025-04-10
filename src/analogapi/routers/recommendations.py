from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..auth import get_current_user, get_db 
from ..models.user import User
from ..models.camera import Camera as CameraModel
from ..models.film import Film as FilmModel
from ..schemas.camera import CameraOut
from ..schemas.film import FilmOut

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Not found"}},
)
# CAMERA RECOMMENDATIONS
@router.get("/cameras", response_model=List[CameraOut])
def recommend_cameras(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")
    query = db.query(CameraModel)
    if preferences.preferred_format:
        query = query.filter(CameraModel.format == preferences.preferred_format)
    if preferences.favorite_photography_type:
        query = query.join(CameraModel.tags).filter(Tag.name.ilike(f"%{preferences.favorite_photography_type}%"))
    cameras = query.all()
    if not cameras:
        raise HTTPException(status_code=404, detail="No cameras found matching your preferences")
    return cameras

# FILM RECOMMENDATIONS
@router.get("/films", response_model=List[FilmOut])
def recommend_films(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")
    query = db.query(FilmModel)
    if preferences.preferred_format:
        query = query.filter(FilmModel.format == preferences.preferred_format)
    if preferences.color_preference:
        if preferences.color_preference.lower() == "color":
            query = query.filter(FilmModel.type == "Color")
        elif preferences.color_preference.lower() == "b&w":
            query = query.filter(FilmModel.type == "B&W")
    if preferences.favorite_photography_type:
        query = query.join(FilmModel.tags).filter(Tag.name.ilike(f"%{preferences.favorite_photography_type}%"))
    films = query.all()
    if not films:
        raise HTTPException(status_code=404, detail="No films found matching your preferences")
    return films

# IMPORTS
from ..models.user_preferences import UserPreferences
from ..models.tag import Tag