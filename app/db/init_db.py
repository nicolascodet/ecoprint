from sqlalchemy.orm import Session
from .base import Base
from .session import engine

def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine) 