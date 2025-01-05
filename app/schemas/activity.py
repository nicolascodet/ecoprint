from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ActivityBase(BaseModel):
    activity_type: str
    description: str
    carbon_impact: float

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
