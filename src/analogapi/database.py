from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import os
from dotenv import load_dotenv
from analogapi.base import Base

load_dotenv()

def get_engine(db_url=None):
    load_dotenv()  
    url = db_url if db_url else os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL"))
    if not url:
        raise ValueError("No database URL provided and DATABASE_URL/TEST_DATABASE_URL not set")
    return create_engine(url)

def get_session(db_url=None):
    engine = get_engine(db_url)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine = None
SessionLocal = None

def initialize_engine_and_session(db_url=None):
    global engine, SessionLocal
    engine = get_engine(db_url)
    SessionLocal = get_session(db_url)

initialize_engine_and_session()

def clear_database(db_url=None):
    from analogapi.models.camera import Camera
    from analogapi.models.film import Film
    from analogapi.models.tag import Tag, camera_tags, film_tags

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

        print("Tables to clear:", [table.name for table in Base.metadata.sorted_tables])


        for table in reversed(Base.metadata.sorted_tables):
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