#!/usr/bin/env python3
"""
Query script to check users in the database.

Usage:
    cd backend
    python scripts/check_users_table.py

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
load_dotenv(os.path.join(backend_dir, '.env'))

from shared.database import SessionLocal
from shared.models import User, Firm


def check_users():
    """Query and display all users."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("Users Table Query")
        print("=" * 60)
        
        users = db.query(User).all()
        
        if not users:
            print("No users found in database.")
            return
        
        print(f"\nFound {len(users)} user(s):\n")
        
        for user in users:
            # Get firm name
            firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
            firm_name = firm.name if firm else "Unknown"
            
            print(f"ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Firm: {firm_name} ({user.firm_id})")
            print(f"Created At: {user.created_at}")
            print(f"Updated At: {user.updated_at}")
            print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error querying users: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        check_users()
        print("\n✅ Query complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

