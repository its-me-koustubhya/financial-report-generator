"""
Database initialization script.
Run this once to create all tables.
"""
from database.models import Base
from database.connection import engine
from config import get_settings

def init_database():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Verify connection
    settings = get_settings()
    print(f"✅ Connected to database: {settings.DATABASE_URL.split('@')[1]}")

if __name__ == "__main__":
    init_database()