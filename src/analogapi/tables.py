from sqlalchemy import Table, Column, Integer, ForeignKey
from ..database import Base

camera_tags = Table(
    "camera_tags",
    Base.metadata,
    Column("camera_id", Integer, ForeignKey("cameras.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

film_tags = Table(
    "film_tags",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

favorite_cameras = Table(
    "favorite_cameras",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("camera_id", Integer, ForeignKey("cameras.id"), primary_key=True)
)

favorite_films = Table(
    "favorite_films",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True)
)