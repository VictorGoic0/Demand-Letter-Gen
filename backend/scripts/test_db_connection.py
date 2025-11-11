#!/usr/bin/env python3
"""
Test script to verify database connection and table creation.
Run this script to test the database setup after starting Docker Compose.
"""
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path (parent of scripts directory)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load environment variables from .env (source of truth)
load_dotenv(os.path.join(backend_dir, '.env.local'))

from shared.db_utils import check_database_connection, create_all_tables
from shared.database import engine, SessionLocal
from shared.models import Firm, User, Document, LetterTemplate, GeneratedLetter, LetterSourceDocument
from sqlalchemy import inspect, text


def test_database_connection():
    """Test if database connection works."""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    if engine is None:
        print("❌ ERROR: Database engine is not initialized.")
        print("   Make sure psycopg2-binary is installed and database is running.")
        return False
    
    if check_database_connection():
        print("✅ Database connection successful!")
        return True
    else:
        print("❌ Database connection failed!")
        print("   Check your database configuration and ensure PostgreSQL is running.")
        return False


def test_tables_exist():
    """Test if all required tables exist."""
    print("\n" + "=" * 60)
    print("Testing Table Existence")
    print("=" * 60)
    
    if engine is None:
        print("❌ ERROR: Database engine is not initialized.")
        return False
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    required_tables = [
        'firms',
        'users',
        'documents',
        'letter_templates',
        'generated_letters',
        'letter_source_documents',
    ]
    
    print(f"\nExisting tables in database: {len(existing_tables)}")
    print(f"Required tables: {len(required_tables)}")
    print()
    
    all_exist = True
    for table in required_tables:
        if table in existing_tables:
            print(f"✅ Table '{table}' exists")
        else:
            print(f"❌ Table '{table}' is missing")
            all_exist = False
    
    return all_exist


def test_table_columns():
    """Test if tables have correct columns."""
    print("\n" + "=" * 60)
    print("Testing Table Columns")
    print("=" * 60)
    
    if engine is None:
        print("❌ ERROR: Database engine is not initialized.")
        return False
    
    inspector = inspect(engine)
    
    # Test firms table
    print("\n📋 Testing 'firms' table columns:")
    if 'firms' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('firms')]
        expected = ['id', 'name', 'created_at', 'updated_at']
        for col in expected:
            if col in columns:
                print(f"  ✅ Column '{col}' exists")
            else:
                print(f"  ❌ Column '{col}' is missing")
    
    # Test users table
    print("\n📋 Testing 'users' table columns:")
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        expected = ['id', 'firm_id', 'email', 'name', 'role', 'created_at', 'updated_at']
        for col in expected:
            if col in columns:
                print(f"  ✅ Column '{col}' exists")
            else:
                print(f"  ❌ Column '{col}' is missing")
    
    # Test documents table
    print("\n📋 Testing 'documents' table columns:")
    if 'documents' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('documents')]
        expected = ['id', 'firm_id', 'uploaded_by', 'filename', 'file_size', 's3_key', 'mime_type', 'uploaded_at']
        for col in expected:
            if col in columns:
                print(f"  ✅ Column '{col}' exists")
            else:
                print(f"  ❌ Column '{col}' is missing")
    
    return True


def test_indexes():
    """Test if required indexes exist."""
    print("\n" + "=" * 60)
    print("Testing Indexes")
    print("=" * 60)
    
    if engine is None:
        print("❌ ERROR: Database engine is not initialized.")
        return False
    
    inspector = inspect(engine)
    
    # Get all indexes
    all_indexes = {}
    for table_name in inspector.get_table_names():
        indexes = inspector.get_indexes(table_name)
        all_indexes[table_name] = [idx['name'] for idx in indexes]
    
    required_indexes = {
        'documents': ['idx_documents_firm_id', 'idx_documents_uploaded_at'],
        'generated_letters': ['idx_letters_firm_id', 'idx_letters_created_at', 'idx_letters_status'],
    }
    
    all_exist = True
    for table, indexes in required_indexes.items():
        print(f"\n📋 Testing indexes for '{table}' table:")
        if table in all_indexes:
            for idx in indexes:
                if idx in all_indexes[table]:
                    print(f"  ✅ Index '{idx}' exists")
                else:
                    print(f"  ❌ Index '{idx}' is missing")
                    all_exist = False
        else:
            print(f"  ❌ Table '{table}' does not exist")
            all_exist = False
    
    return all_exist


def test_foreign_keys():
    """Test if foreign key constraints exist."""
    print("\n" + "=" * 60)
    print("Testing Foreign Key Constraints")
    print("=" * 60)
    
    if engine is None:
        print("❌ ERROR: Database engine is not initialized.")
        return False
    
    inspector = inspect(engine)
    
    # Test foreign keys for users table
    print("\n📋 Testing foreign keys for 'users' table:")
    if 'users' in inspector.get_table_names():
        fks = inspector.get_foreign_keys('users')
        fk_columns = [fk['constrained_columns'][0] for fk in fks]
        if 'firm_id' in fk_columns:
            print("  ✅ Foreign key 'firm_id' exists")
        else:
            print("  ❌ Foreign key 'firm_id' is missing")
    
    # Test foreign keys for documents table
    print("\n📋 Testing foreign keys for 'documents' table:")
    if 'documents' in inspector.get_table_names():
        fks = inspector.get_foreign_keys('documents')
        fk_columns = [fk['constrained_columns'][0] for fk in fks]
        expected_fks = ['firm_id', 'uploaded_by']
        for fk in expected_fks:
            if fk in fk_columns:
                print(f"  ✅ Foreign key '{fk}' exists")
            else:
                print(f"  ❌ Foreign key '{fk}' is missing")
    
    return True


def test_basic_operations():
    """Test basic database operations (insert, select)."""
    print("\n" + "=" * 60)
    print("Testing Basic Database Operations")
    print("=" * 60)
    
    if SessionLocal is None:
        print("❌ ERROR: SessionLocal is not initialized.")
        return False
    
    db = SessionLocal()
    try:
        # Test insert
        print("\n📝 Testing INSERT operation:")
        test_firm = Firm(
            name="Test Law Firm",
        )
        db.add(test_firm)
        db.commit()
        print(f"  ✅ Successfully inserted firm: {test_firm.id}")
        
        # Test select
        print("\n📖 Testing SELECT operation:")
        firms = db.query(Firm).all()
        print(f"  ✅ Successfully queried {len(firms)} firm(s)")
        
        # Test delete
        print("\n🗑️  Testing DELETE operation:")
        db.delete(test_firm)
        db.commit()
        print(f"  ✅ Successfully deleted test firm")
        
        return True
    except Exception as e:
        print(f"  ❌ Error during operations: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Database Connection and Schema Test")
    print("=" * 60)
    print("\nThis script tests:")
    print("  1. Database connection")
    print("  2. Table existence")
    print("  3. Table columns")
    print("  4. Indexes")
    print("  5. Foreign keys")
    print("  6. Basic CRUD operations")
    print("\nMake sure Docker Compose is running and database is accessible.")
    print("=" * 60)
    
    results = []
    
    # Test 1: Connection
    results.append(("Database Connection", test_database_connection()))
    
    # Test 2: Tables exist
    results.append(("Table Existence", test_tables_exist()))
    
    # Test 3: Table columns
    results.append(("Table Columns", test_table_columns()))
    
    # Test 4: Indexes
    results.append(("Indexes", test_indexes()))
    
    # Test 5: Foreign keys
    results.append(("Foreign Keys", test_foreign_keys()))
    
    # Test 6: Basic operations (only if connection works)
    if results[0][1]:
        results.append(("Basic Operations", test_basic_operations()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Database is properly configured.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

