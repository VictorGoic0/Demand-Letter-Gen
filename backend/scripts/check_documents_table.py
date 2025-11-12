#!/usr/bin/env python3
"""
Query script to check documents in the database.

Usage:
    cd backend
    python scripts/check_documents_table.py

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
from shared.models import Document, Firm, User
from shared.utils import format_file_size


def check_documents():
    """Query and display all documents."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("Documents Table Query")
        print("=" * 60)
        
        documents = db.query(Document).all()
        
        if not documents:
            print("No documents found in database.")
            return
        
        print(f"\nFound {len(documents)} document(s):\n")
        
        for document in documents:
            # Get firm name
            firm = db.query(Firm).filter(Firm.id == document.firm_id).first()
            firm_name = firm.name if firm else "Unknown"
            
            # Get uploader name if exists
            uploader_name = None
            if document.uploaded_by:
                uploader = db.query(User).filter(User.id == document.uploaded_by).first()
                uploader_name = uploader.name if uploader else "Unknown"
            
            print(f"ID: {document.id}")
            print(f"Filename: {document.filename}")
            print(f"Firm: {firm_name} ({document.firm_id})")
            print(f"Uploaded By: {uploader_name if uploader_name else 'N/A'}")
            print(f"File Size: {format_file_size(document.file_size)} ({document.file_size} bytes)")
            print(f"MIME Type: {document.mime_type}")
            print(f"S3 Key: {document.s3_key}")
            print(f"Uploaded At: {document.uploaded_at}")
            print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error querying documents: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        check_documents()
        print("\n✅ Query complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

