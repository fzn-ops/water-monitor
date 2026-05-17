from datetime import datetime
from pydantic import BaseModel, ConfigDict, computed_field
from app.core.config import settings


# --- Request schemas ---

class ReadingCreate(BaseModel):
    location_id: int
    water_level_cm: float
    pixel_distance: float | None = None


# --- Response schemas ---

class ReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location_id: int
    water_level_cm: float
    status: str
    pixel_distance: float | None
    recorded_at: datetime

    @computed_field
    @property
    def danger_threshold(self) -> float:
        # Mengirimkan angka batas bahaya ke React
        return float(settings.THRESHOLD_BAHAYA)

