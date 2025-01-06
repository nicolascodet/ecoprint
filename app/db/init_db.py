from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
from .session import SQLALCHEMY_DATABASE_URL, connect_args

def init_db():
    """Initialize the database with the correct schema."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal() 