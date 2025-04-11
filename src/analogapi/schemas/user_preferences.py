from pydantic import BaseModel
from enum import Enum
from typing import List, Optional

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

class UserPreferencesBase(BaseModel):
    favorite_photography_type: Optional[List[PhotographyType]] = None
    preferred_format: Optional[AnalogFormat] = None
    color_preference: Optional[ColorPreference] = None
    preferred_camera_type: Optional[CameraType] = None
    preferred_focal_length: Optional[PreferredFocalLength] = None
    favourite_look: Optional[FavouriteLook] = None

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesOut(UserPreferencesBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True