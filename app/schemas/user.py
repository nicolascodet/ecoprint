from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    total_distance: float
    total_co2_saved: float
    points: int
    strava_connected: bool

    class Config:
        from_attributes = True
