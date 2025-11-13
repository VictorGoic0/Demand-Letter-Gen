#!/usr/bin/env python3
"""
Seed script to create a test firm in the database.

Usage:
    cd backend
    python scripts/seed_test_firm.py

Make sure:
    1. Docker Compose is running (database)
    2. Virtual environment is activated (if using venv)
"""
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load environment variables
# Try .env.production first (for production), then fall back to .env (for development)
# prod_env = os.path.join(backend_dir, '.env.production')
# dev_env = os.path.join(backend_dir, '.env')
# if os.path.exists(prod_env):
#     load_dotenv(prod_env)
#     print("📝 Loading from .env.production")
# else:
#     load_dotenv(dev_env)
#     print("📝 Loading from .env")
load_dotenv(os.path.join(backend_dir, '.env'))

from shared.database import SessionLocal
from shared.models import Firm


def seed_firm():
    """Create a test firm."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("Seeding Test Firm")
        print("=" * 60)
        
        # Check if firm already exists
        existing_firm = db.query(Firm).filter(Firm.name == "Test Law Firm").first()
        if existing_firm:
            print(f"✅ Firm already exists: {existing_firm.name} (ID: {existing_firm.id})")
            return existing_firm
        
        # Create firm
        firm = Firm(
            name="Test Law Firm",
        )
        db.add(firm)
        db.commit()
        db.refresh(firm)
        
        print(f"✅ Created firm: {firm.name} (ID: {firm.id})")
        return firm
        
    except Exception as e:
        print(f"❌ Error creating firm: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        firm = seed_firm()
        print(f"\n✅ Success! Firm ID: {firm.id}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

