from datetime import datetime
from pydantic import BaseModel, ConfigDict


# --- Request schemas ---

class LocationCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    image_url: str | None = None
    camera_url: str | None = None


class LocationUpdate(BaseModel):
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_url: str | None = None
    camera_url: str | None = None  


# --- Response schemas ---

class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    latitude: float
    longitude: float
    image_url: str | None
    camera_url: str | None         
    created_at: datetime