"""
Database utility functions for initialization and management.
"""
from sqlalchemy import text
from shared.database import engine
from shared.base import Base


def check_database_connection() -> bool:
    """
    Check if database connection is available.
    
    Returns:
        True if connection is successful, False otherwise.
    """
    if engine is None:
        return False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def create_all_tables():
    """
    Create all tables defined in the models.
    This is useful for development/testing but migrations should be used in production.
    """
    if engine is None:
        raise RuntimeError("Database engine is not initialized. Check your database configuration.")
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Drop all tables defined in the models.
    WARNING: This will delete all data! Use only in development.
    """
    if engine is None:
        raise RuntimeError("Database engine is not initialized. Check your database configuration.")
    Base.metadata.drop_all(bind=engine)


def init_database():
    """
    Initialize the database by creating all tables.
    This is a convenience function for development setup.
    """
    if not check_database_connection():
        raise ConnectionError("Cannot connect to database. Check your connection settings.")
    
    create_all_tables()
    print("Database tables created successfully.")


if __name__ == "__main__":
    # Allow running this script directly for database initialization
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        print("WARNING: This will drop all tables and delete all data!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() == "yes":
            drop_all_tables()
            print("All tables dropped.")
        else:
            print("Cancelled.")
    else:
        init_database()

