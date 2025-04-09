from fastapi import FastAPI
from analogapi.routers import camera, film
from analogapi.database import Base, engine

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    raise Exception(f"Error al crear las tablas en la base de datos: {e}")

app = FastAPI(title="AnalogAPI")

app.include_router(camera.router)
app.include_router(film.router)

@app.get("/")
def root():
    return {"message": "Welcome to AnalogAPI"}