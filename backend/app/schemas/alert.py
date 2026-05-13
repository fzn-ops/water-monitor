from datetime import datetime
from pydantic import BaseModel, ConfigDict


# --- Response schemas ---

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reading_id: int
    message: str
    is_sent: bool
    sent_at: datetime | None
    created_at: datetime
