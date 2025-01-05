from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    timestamp: Optional[datetime] = None
    activity_type: Optional[str] = None  # WALKING, RUNNING, CYCLING, DRIVING, etc. 