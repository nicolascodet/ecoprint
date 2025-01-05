from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String)  # WALKING, RUNNING, CYCLING, etc.
    distance = Column(Float)  # in meters
    duration = Column(Integer)  # in seconds
    carbon_impact = Column(Float)  # in kg CO2
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="activities")
