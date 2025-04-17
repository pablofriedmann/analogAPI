 # src/analogapi/routers/scrape.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..scrapers.scrape_cameras import scrape_cameras, save_scraped_cameras
from ..scrapers.scrape_films import scrape_films, save_scraped_films 

router = APIRouter(
    prefix="/scrape",
    tags=["scrape"],
    responses={404: {"description": "Not found"}},
)

@router.post("/cameras")
def scrape_and_save_cameras(
    max_cameras_per_category: int = 10,
    max_categories: int = 10,
    db: Session = Depends(get_db)
):
    if max_cameras_per_category <= 0:
        raise HTTPException(status_code=400, detail="max_cameras_per_category must be a positive integer")
    if max_categories <= 0:
        raise HTTPException(status_code=400, detail="max_categories must be a positive integer")

    try:
        cameras = scrape_cameras(max_cameras_per_category, max_categories)
        save_scraped_cameras(db, cameras)
        return {"message": f"Scraped and saved {len(cameras)} cameras"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during scraping: {str(e)}")

@router.post("/films")
def scrape_and_save_films(
    max_films_per_category: int = 10,
    max_categories: int = 10,
    db: Session = Depends(get_db)
):
    if max_films_per_category <= 0:
        raise HTTPException(status_code=400, detail="max_films_per_category must be a positive integer")
    if max_categories <= 0:
        raise HTTPException(status_code=400, detail="max_categories must be a positive integer")

    try:
        films = scrape_films(max_films_per_category, max_categories)
        save_scraped_films(db, films)
        return {"message": f"Scraped and saved {len(films)} films"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during scraping: {str(e)}")