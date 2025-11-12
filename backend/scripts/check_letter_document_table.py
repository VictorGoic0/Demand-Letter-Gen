#!/usr/bin/env python3
"""
Query script to check letter-source document associations in the database.
Returns first 5 results.

Usage:
    cd backend
    python scripts/check_letter_document_table.py

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
from shared.models import LetterSourceDocument, GeneratedLetter, Document


def check_letter_documents():
    """Query and display first 5 letter-document associations."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("Letter Source Documents Table Query (First 5)")
        print("=" * 60)
        
        associations = db.query(LetterSourceDocument).limit(5).all()
        
        if not associations:
            print("No letter-document associations found in database.")
            return
        
        print(f"\nFound {len(associations)} association(s) (showing first 5):\n")
        
        for assoc in associations:
            # Get letter title
            letter = db.query(GeneratedLetter).filter(GeneratedLetter.id == assoc.letter_id).first()
            letter_title = letter.title if letter else "Unknown"
            
            # Get document filename
            document = db.query(Document).filter(Document.id == assoc.document_id).first()
            doc_filename = document.filename if document else "Unknown"
            
            print(f"Letter ID: {assoc.letter_id}")
            print(f"Letter Title: {letter_title}")
            print(f"Document ID: {assoc.document_id}")
            print(f"Document Filename: {doc_filename}")
            print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error querying letter-document associations: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        check_letter_documents()
        print("\n✅ Query complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

