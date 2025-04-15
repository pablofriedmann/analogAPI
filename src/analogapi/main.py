from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import get_engine, initialize_engine_and_session, Base
from .routers import camera, film, tag, user, recommendations, favorites, scrape
from .models.camera import Camera
from .models.film import Film
from .models.tag import Tag
from .models.user import User
from .models.user_preferences import UserPreferences
from .models.favorite_camera import FavoriteCamera
from .models.favorite_film import FavoriteFilm
from .models.tables import camera_tags, film_tags, favorite_cameras, favorite_films 

initialize_engine_and_session()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise Exception(f"Error al crear las tablas en la base de datos: {e}")
    yield

app = FastAPI(title="AnalogAPI", lifespan=lifespan)

app.include_router(camera.router)
app.include_router(film.router)
app.include_router(tag.router)
app.include_router(user.router)
app.include_router(recommendations.router)
app.include_router(favorites.router)
app.include_router(scrape.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AnalogAPI"}