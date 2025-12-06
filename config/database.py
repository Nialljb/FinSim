"""
Database configuration and connection management
Supports both SQLite (local) and PostgreSQL (production)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# Database Configuration
# ============================================================================

# Get database URL from environment (Render sets this automatically)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///finsim.db")

# Fix for Render PostgreSQL URL (uses postgres:// instead of postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ============================================================================
# SQLAlchemy Setup
# ============================================================================

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debug logging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=300,    # Recycle connections after 5 minutes
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ============================================================================
# Helper Functions
# ============================================================================

def get_db():
    """
    Get database session (dependency injection pattern)
    
    Usage:
        db = get_db()
        try:
            # use db
        finally:
            db.close()
    
    Or with context manager:
        with get_db() as db:
            # use db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database - create all tables
    Should be called on application startup
    """
    # Import all models to ensure they're registered
    from data.database import Base as ModelsBase
    
    # Create all tables
    ModelsBase.metadata.create_all(bind=engine)

def get_database_type():
    """Return 'sqlite' or 'postgresql'"""
    if DATABASE_URL.startswith("sqlite"):
        return "sqlite"
    elif DATABASE_URL.startswith("postgresql"):
        return "postgresql"
    else:
        return "unknown"

# ============================================================================
# Export
# ============================================================================

__all__ = [
    'engine',
    'SessionLocal',
    'Base',
    'get_db',
    'init_db',
    'get_database_type',
    'DATABASE_URL'
]
