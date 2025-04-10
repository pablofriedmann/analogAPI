from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import get_engine, initialize_engine_and_session, Base  # Agregar Base
from .routers import camera, film, tag, user, recommendations
# Importar explícitamente los modelos para asegurar que se registren
from .models.camera import Camera
from .models.film import Film
from .models.tag import Tag
from .models.user import User
from .models.user_preferences import UserPreferences

# Inicializar el engine y la sesión al cargar el módulo
initialize_engine_and_session()

# Definir la función lifespan antes de usarla
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise Exception(f"Error al crear las tablas en la base de datos: {e}")
    yield

# Crear la instancia de FastAPI después de definir lifespan
app = FastAPI(title="AnalogAPI", lifespan=lifespan)

app.include_router(camera.router)
app.include_router(film.router)
app.include_router(tag.router)
app.include_router(user.router)
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AnalogAPI"}