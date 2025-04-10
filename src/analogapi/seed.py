import os
from sqlalchemy.orm import Session
from .database import get_engine, get_session, SessionLocal
from .models.camera import Camera
from .models.film import Film
from .models.tag import Tag
from .tables import camera_tags, film_tags
from sqlalchemy.sql import text
from .base import Base  #

def seed_database(db_url=None, clear=True):
    
    engine = get_engine(db_url)
    SessionLocal = get_session(db_url)
    db = SessionLocal()

    try:
        print("Seeding database...")

        print("Creating tables if they don't exist...")
        Base.metadata.create_all(bind=engine)

        if clear:
            print("Clearing database before seeding...")
            for table in reversed(Camera.__table__.metadata.sorted_tables):
                db.execute(table.delete())
            db.commit()

        tag_names = ["SLR", "Medium Format", "Color", "B&W", "Portrait"]
        for name in tag_names:
            if not db.query(Tag).filter(Tag.name == name).first():
                db.add(Tag(name=name))
        db.commit()

        # SEEDS CAMERAS
        cameras_data = [
            {"brand": "Canon", "model": "AE-1", "format": "35mm", "type": "SLR", "years": "1976-1984", "lens_mount": "Canon FD"},
            {"brand": "Nikon", "model": "F3", "format": "35mm", "type": "SLR", "years": "1980-2000", "lens_mount": "Nikon F"},
            {"brand": "Hasselblad", "model": "500C/M", "format": "120", "type": "Medium Format", "years": "1970-1994", "lens_mount": "Hasselblad V"},
            {"brand": "Pentax", "model": "K1000", "format": "35mm", "type": "SLR", "years": "1976-1997", "lens_mount": "Pentax K"},
            {"brand": "Mamiya", "model": "RB67", "format": "120", "type": "Medium Format", "years": "1970-1990", "lens_mount": "Mamiya RB"},
        ]
        for camera_data in cameras_data:
            if not db.query(Camera).filter(Camera.model == camera_data["model"]).first():
                db.add(Camera(**camera_data))
        db.commit()

        # ASSOCIATE TAGS/CAMERAS
        tag_slr = db.query(Tag).filter(Tag.name == "SLR").first()
        tag_medium_format = db.query(Tag).filter(Tag.name == "Medium Format").first()

        canon_ae1 = db.query(Camera).filter(Camera.model == "AE-1").first()
        nikon_f3 = db.query(Camera).filter(Camera.model == "F3").first()
        hasselblad_500cm = db.query(Camera).filter(Camera.model == "500C/M").first()
        pentax_k1000 = db.query(Camera).filter(Camera.model == "K1000").first()
        mamiya_rb67 = db.query(Camera).filter(Camera.model == "RB67").first()

        if not canon_ae1.tags:
            canon_ae1.tags.append(tag_slr)
        if not nikon_f3.tags:
            nikon_f3.tags.append(tag_slr)
        if not pentax_k1000.tags:
            pentax_k1000.tags.append(tag_slr)
        if not hasselblad_500cm.tags:
            hasselblad_500cm.tags.append(tag_medium_format)
        if not mamiya_rb67.tags:
            mamiya_rb67.tags.append(tag_medium_format)
        db.commit()

        # SEEDS FILM
        films_data = [
            {"brand": "Kodak", "name": "Portra 400", "format": "35mm", "type": "Color", "iso": 400, "grain": "Fine"},
            {"brand": "Ilford", "name": "HP5 Plus", "format": "35mm", "type": "B&W", "iso": 400, "grain": "Medium"},
            {"brand": "Fujifilm", "name": "Superia 400", "format": "35mm", "type": "Color", "iso": 400, "grain": "Fine"},
            {"brand": "Kodak", "name": "Ektar 100", "format": "120", "type": "Color", "iso": 100, "grain": "Fine"},
            {"brand": "Ilford", "name": "Delta 3200", "format": "120", "type": "B&W", "iso": 3200, "grain": "Coarse"},
        ]
        for film_data in films_data:
            if not db.query(Film).filter(Film.name == film_data["name"]).first():
                db.add(Film(**film_data))
        db.commit()

        # TAG ASSOCIATION
        tag_color = db.query(Tag).filter(Tag.name == "Color").first()
        tag_bw = db.query(Tag).filter(Tag.name == "B&W").first()
        tag_portrait = db.query(Tag).filter(Tag.name == "Portrait").first()

        portra_400 = db.query(Film).filter(Film.name == "Portra 400").first()
        hp5_plus = db.query(Film).filter(Film.name == "HP5 Plus").first()
        superia_400 = db.query(Film).filter(Film.name == "Superia 400").first()
        ektar_100 = db.query(Film).filter(Film.name == "Ektar 100").first()
        delta_3200 = db.query(Film).filter(Film.name == "Delta 3200").first()

        if not portra_400.tags:
            portra_400.tags.append(tag_color)
            portra_400.tags.append(tag_portrait)
        if not hp5_plus.tags:
            hp5_plus.tags.append(tag_bw)
        if not superia_400.tags:
            superia_400.tags.append(tag_color)
        if not ektar_100.tags:
            ektar_100.tags.append(tag_color)
            ektar_100.tags.append(tag_portrait)
        if not delta_3200.tags:
            delta_3200.tags.append(tag_bw)
        db.commit()

        print("Database seeded successfully with 5 cameras, 5 films, and 5 tags.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/analogapi_dev")
    seed_database(db_url, clear=True)