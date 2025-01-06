from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    total_distance = Column(Float, default=0.0)
    total_co2_saved = Column(Float, default=0.0)
    current_streak = Column(Integer, default=0)
    points = Column(Integer, default=0)
    achievements = Column(JSON, default=list)
    synced_activities = Column(JSON, default=list)
    
    # Strava integration
    strava_connected = Column(Boolean, default=False)
    strava_access_token = Column(String, nullable=True)
    strava_refresh_token = Column(String, nullable=True)
    strava_token_expires_at = Column(Integer, nullable=True)
    strava_athlete_id = Column(String, nullable=True)
    
    # Relationships
    activities = relationship("Activity", back_populates="user")
