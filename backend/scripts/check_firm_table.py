#!/usr/bin/env python3
"""
Query script to check firms in the database.

Usage:
    cd backend
    python scripts/check_firm_table.py

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
from shared.models import Firm


def check_firms():
    """Query and display all firms."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("Firms Table Query")
        print("=" * 60)
        
        firms = db.query(Firm).all()
        
        if not firms:
            print("No firms found in database.")
            return
        
        print(f"\nFound {len(firms)} firm(s):\n")
        
        for firm in firms:
            print(f"ID: {firm.id}")
            print(f"Name: {firm.name}")
            print(f"Created At: {firm.created_at}")
            print(f"Updated At: {firm.updated_at}")
            print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error querying firms: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        check_firms()
        print("\n✅ Query complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

