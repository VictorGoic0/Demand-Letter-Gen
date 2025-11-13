#!/usr/bin/env python3
"""
Seed script to create test users for a firm.

Usage:
    cd backend
    python scripts/seed_test_users.py

Make sure:
    1. Docker Compose is running (database)
    2. A firm exists (run seed_test_firm.py first)
    3. Virtual environment is activated (if using venv)
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
from shared.models import Firm, User


# Hardcoded test users
TEST_USERS = [
    {"name": "John Smith", "email": "john.smith@testfirm.com", "role": "attorney"},
    {"name": "Jane Doe", "email": "jane.doe@testfirm.com", "role": "attorney"},
    {"name": "Bob Johnson", "email": "bob.johnson@testfirm.com", "role": "paralegal"},
    {"name": "Alice Williams", "email": "alice.williams@testfirm.com", "role": "paralegal"},
    {"name": "Charlie Brown", "email": "charlie.brown@testfirm.com", "role": "paralegal"},
    {"name": "Victor Goico", "email": "victormgoico@gmail.com", "role": "attorney"},
]


def seed_users():
    """Create test users for the test firm."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("Seeding Test Users")
        print("=" * 60)
        
        # Get or create test firm
        firm = db.query(Firm).filter(Firm.name == "Test Law Firm").first()
        if not firm:
            print("❌ Test firm not found. Please run seed_test_firm.py first.")
            return None
        
        print(f"Using firm: {firm.name} (ID: {firm.id})")
        
        # Create users
        created_users = []
        skipped_users = []
        
        for user_data in TEST_USERS:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"⏭️  User already exists: {user_data['name']} ({user_data['email']})")
                skipped_users.append(existing_user)
                continue
            
            user = User(
                firm_id=firm.id,
                name=user_data["name"],
                email=user_data["email"],
                role=user_data["role"],
            )
            db.add(user)
            created_users.append(user)
        
        db.commit()
        
        # Refresh to get IDs
        for user in created_users:
            db.refresh(user)
        
        print(f"\n✅ Created {len(created_users)} new users:")
        for user in created_users:
            print(f"   - {user.name} ({user.email}) - {user.role}")
        
        if skipped_users:
            print(f"\n⏭️  Skipped {len(skipped_users)} existing users")
        
        return created_users + skipped_users
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        users = seed_users()
        if users:
            print(f"\n✅ Success! Total users: {len(users)}")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

