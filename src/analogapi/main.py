from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import camera, film, tag
from .database import engine
from .base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise Exception(f"Error al crear las tablas en la base de datos: {e}")
    yield

app = FastAPI(title="AnalogAPI", lifespan=lifespan)

app.include_router(camera.router)
app.include_router(film.router)
app.include_router(tag.router)

@app.get("/")
def root():
    return {"message": "Welcome to AnalogAPI"}