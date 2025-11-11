"""
Base declarative base for SQLAlchemy models.
This is separated to allow imports without requiring database connection.
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

