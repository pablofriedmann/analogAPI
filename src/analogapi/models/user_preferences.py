from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..base import Base  
from enum import Enum

class PhotographyType(str, Enum):
    PORTRAIT = "portrait"
    SELF_PORTRAIT = "self_portrait"
    FAMILY = "family"
    DOCUMENTARY = "documentary"
    STREET = "street"
    PHOTOJOURNALISM = "photojournalism"
    EVENT = "event"
    CONCERT = "concert"
    NATURE = "nature"
    LANDSCAPE = "landscape"
    ANIMALS = "animals"
    FINE_ART = "fine_art"
    CONCEPTUAL = "conceptual"
    FASHION = "fashion"
    COMMERCIAL = "commercial"
    ARCHITECTURE = "architecture"
    SPORTS = "sports"
    ASTROPHOTOGRAPHY = "astrophotography"

class AnalogFormat(str, Enum):
    FORMAT_35MM = "35mm"
    FORMAT_120 = "120"
    LARGE_FORMAT = "large_format"
    INSTANT = "instant"
    PINHOLE = "pinhole"
    HALF_FRAME = "half_frame"
    DISC_FILM = "disc_film"
    APS = "aps"

class ColorPreference(str, Enum):
    COLOR = "color"
    BLACK_AND_WHITE = "black_and_white"
    BOTH = "both"

class CameraType(str, Enum):
    SLR = "slr"
    RANGEFINDER = "rangefinder"
    TLR = "tlr"
    POINT_AND_SHOOT = "point_and_shoot"
    PINHOLE = "pinhole"
    VIEW_CAMERA = "view_camera"
    INSTANT = "instant"

class PreferredFocalLength(str, Enum):
    WIDE = "wide"
    STANDARD = "standard"
    SHORT_TELE = "short_tele"
    TELE = "tele"
    OTHER = "other"

class FavouriteLook(str, Enum):
    NATURAL = "natural"
    CONTRASTY = "contrasty"
    SOFT = "soft"
    GRAINY = "grainy"
    VINTAGE = "vintage"
    FADED = "faded"
    WARM = "warm"
    COOL = "cool"
    CINEMATIC = "cinematic"

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    favorite_photography_type = Column(JSON, nullable=True)  
    preferred_format = Column(String, nullable=True) 
    color_preference = Column(String, nullable=True) 
    preferred_camera_type = Column(String, nullable=True)
    preferred_focal_length = Column(String, nullable=True) 
    favourite_look = Column(String, nullable=True) 

    user = relationship("User", back_populates="preferences")

    @staticmethod
    def validate_favorite_photography_type(value):
        if value is None:
            return value
        if not isinstance(value, list):
            raise ValueError("favorite_photography_type must be a list")
        valid_types = [item.value for item in PhotographyType]
        for item in value:
            if item not in valid_types:
                raise ValueError(f"Invalid photography type: {item}. Must be one of {valid_types}")
        return value

    @staticmethod
    def validate_preferred_format(value):
        if value is None:
            return value
        valid_formats = [item.value for item in AnalogFormat]
        if value not in valid_formats:
            raise ValueError(f"Invalid format: {value}. Must be one of {valid_formats}")
        return value

    @staticmethod
    def validate_color_preference(value):
        if value is None:
            return value
        valid_preferences = [item.value for item in ColorPreference]
        if value not in valid_preferences:
            raise ValueError(f"Invalid color preference: {value}. Must be one of {valid_preferences}")
        return value

    @staticmethod
    def validate_preferred_camera_type(value):
        if value is None:
            return value
        valid_types = [item.value for item in CameraType]
        if value not in valid_types:
            raise ValueError(f"Invalid camera type: {value}. Must be one of {valid_types}")
        return value

    @staticmethod
    def validate_preferred_focal_length(value):
        if value is None:
            return value
        valid_lengths = [item.value for item in PreferredFocalLength]
        if value not in valid_lengths:
            raise ValueError(f"Invalid focal length: {value}. Must be one of {valid_lengths}")
        return value

    @staticmethod
    def validate_favourite_look(value):
        if value is None:
            return value
        valid_looks = [item.value for item in FavouriteLook]
        if value not in valid_looks:
            raise ValueError(f"Invalid look: {value}. Must be one of {valid_looks}")
        return value

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "favorite_photography_type" in kwargs:
            self.favorite_photography_type = self.validate_favorite_photography_type(kwargs["favorite_photography_type"])
        if "preferred_format" in kwargs:
            self.preferred_format = self.validate_preferred_format(kwargs["preferred_format"])
        if "color_preference" in kwargs:
            self.color_preference = self.validate_color_preference(kwargs["color_preference"])
        if "preferred_camera_type" in kwargs:
            self.preferred_camera_type = self.validate_preferred_camera_type(kwargs["preferred_camera_type"])
        if "preferred_focal_length" in kwargs:
            self.preferred_focal_length = self.validate_preferred_focal_length(kwargs["preferred_focal_length"])
        if "favourite_look" in kwargs:
            self.favourite_look = self.validate_favourite_look(kwargs["favourite_look"])