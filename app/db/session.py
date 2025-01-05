from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# For Vercel serverless environment, use /tmp directory
if os.environ.get("VERCEL"):
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/ecoprint.db"
else:
    # Local development
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecoprint.db")

# Create engine with SQLite configuration
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
