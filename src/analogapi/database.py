import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import logging
import time
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

from .base import Base

from .models.tag import Tag
from .models.camera import Camera
from .models.film import Film
from .models.user import User
from .models.user_preferences import UserPreferences

load_dotenv(dotenv_path="/workspaces/analogAPI/.env")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/analogapi_dev")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://user:password@localhost:5432/analogapi_test")

print(f"DEBUG: DATABASE_URL={DATABASE_URL}")
print(f"DEBUG: TEST_DATABASE_URL={TEST_DATABASE_URL}")

class Database:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def get_engine(self, db_url=None, retries=3, delay=2):
        if self.engine is None:
            if db_url is None:
                db_url = os.getenv("DATABASE_URL", os.getenv("TEST_DATABASE_URL"))
                if db_url is None:
                    raise ValueError("DATABASE_URL or TEST_DATABASE_URL must be set")
            print(f"DEBUG: Initializing engine with db_url={db_url}")
            for attempt in range(retries):
                try:
                    self.engine = create_engine(db_url)
                    with self.engine.connect() as connection:
                        connection.execute(text("SELECT 1"))
                    print("DEBUG: Engine initialized successfully")
                    break
                except OperationalError as e:
                    print(f"ERROR: Failed to initialize engine (attempt {attempt + 1}/{retries}): {e}")
                    if attempt < retries - 1:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        raise Exception(f"Failed to initialize engine after {retries} attempts: {e}")
                except Exception as e:
                    print(f"ERROR: Unexpected error while initializing engine: {e}")
                    raise
        return self.engine

    def get_session(self, db_url=None):
        if self.SessionLocal is None:
            engine = self.get_engine(db_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return self.SessionLocal

    def initialize(self, db_url=None):
        print("DEBUG: Calling initialize_engine_and_session")
        self.get_engine(db_url)
        self.get_session(db_url)
        print(f"DEBUG: Engine after initialization: {self.engine}")

db = Database()

SessionLocal = db.get_session()

def get_engine(db_url=None):
    return db.get_engine(db_url)

def get_session(db_url=None):
    return db.get_session(db_url)

def initialize_engine_and_session(db_url=None):
    db.initialize(db_url)

def clear_database(db_url=None):
    from .models.tables import camera_tags, film_tags, favorite_cameras, favorite_films

    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        raise RuntimeError("Cannot clear database in production environment")

    temp_engine = get_engine(db_url)
    temp_session = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)
    db = temp_session()
    try:
        print(f"Clearing database with URL: {db_url}")
        count_before = db.execute(text("SELECT COUNT(*) FROM tags")).scalar()
        print(f"Tags before clearing: {count_before}")

        tables = [
            camera_tags,
            film_tags,
            favorite_cameras,
            favorite_films,
            "user_preferences",
            "tags",
            "films",
            "cameras",
            "users",
        ]

        print(f"Tables to clear: {[table.name if hasattr(table, 'name') else table for table in tables]}")
        for table in tables:
            if isinstance(table, str):
                print(f"Deleting from table: {table}")
                db.execute(text(f"DELETE FROM {table}"))
            else:
                print(f"Deleting from table: {table.name}")
                db.execute(table.delete())

        db.commit()
        print("Database cleared successfully")

        count_after = db.execute(text("SELECT COUNT(*) FROM tags")).scalar()
        print(f"Tags after clearing: {count_after}")
        if count_after != 0:
            raise Exception("Failed to clear tags table")
    except Exception as e:
        db.rollback()
        raise Exception(f"Error clearing database: {e}")
    finally:
        db.close()
        temp_engine.dispose()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()