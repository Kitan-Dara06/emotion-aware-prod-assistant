import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables
load_dotenv()

# Don't create engine immediately - wait until DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL")

# Lazy initialization - only create engine when needed
_engine = None
_SessionLocal = None

def get_engine():
    """Get or create database engine"""
    global _engine
    if _engine is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError(
                "DATABASE_URL environment variable not set. "
                "Please create a .env file with DATABASE_URL or set it in your environment."
            )
        _engine = create_engine(db_url)
    return _engine

def get_session_local():
    """Get or create SessionLocal"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

# For backward compatibility
@property
def engine():
    return get_engine()

# Create SessionLocal as a callable that returns the session maker
class SessionLocalProxy:
    def __call__(self):
        return get_session_local()()
    
    def __getattr__(self, name):
        return getattr(get_session_local(), name)

SessionLocal = SessionLocalProxy()
Base = declarative_base()
