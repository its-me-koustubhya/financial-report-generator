from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# Get database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Fix for Railway PostgreSQL URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()