"""
Database configuration and session management.
"""
import os
from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from shared.base import Base

# Database URL from environment variables
# Use .env as the source of truth for all database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "demand_letters")
DB_USER = os.getenv("DB_USER", "dev_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dev_password")

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with connection pooling
# Note: Engine creation may fail if psycopg2 is not installed, but Base can still be imported
try:
    engine: Engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before using
        echo=False,  # Set to True for SQL query logging
    )
    # Create SessionLocal factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception:
    # If engine creation fails (e.g., psycopg2 not installed), set to None
    # This allows Base and models to be imported for migrations
    engine = None
    SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    Yields a database session and ensures it's closed after use.
    """
    if SessionLocal is None:
        raise RuntimeError("Database session factory is not initialized. Check your database configuration.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

