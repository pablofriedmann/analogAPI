from sqlalchemy import Table, Column, Integer, ForeignKey
from .database import Base

camera_tags = Table(
    "camera_tags",
    Base.metadata,
    Column("camera_id", Integer, ForeignKey("cameras.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)

film_tags = Table(
    "film_tags",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)