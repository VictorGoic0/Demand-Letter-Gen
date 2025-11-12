#!/usr/bin/env python3
"""
Query script to check generated letters in the database.
Returns first 5 results.

Usage:
    cd backend
    python scripts/check_letter_table.py

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
from shared.models import GeneratedLetter, Firm, User, LetterTemplate


def check_letters():
    """Query and display first 5 letters."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("Generated Letters Table Query (First 5)")
        print("=" * 60)
        
        letters = db.query(GeneratedLetter).limit(5).all()
        
        if not letters:
            print("No letters found in database.")
            return
        
        print(f"\nFound {len(letters)} letter(s) (showing first 5):\n")
        
        for letter in letters:
            # Get firm name
            firm = db.query(Firm).filter(Firm.id == letter.firm_id).first()
            firm_name = firm.name if firm else "Unknown"
            
            # Get creator name if exists
            creator_name = None
            if letter.created_by:
                creator = db.query(User).filter(User.id == letter.created_by).first()
                creator_name = creator.name if creator else "Unknown"
            
            # Get template name if exists
            template_name = None
            if letter.template_id:
                template = db.query(LetterTemplate).filter(LetterTemplate.id == letter.template_id).first()
                template_name = template.name if template else "Unknown"
            
            print(f"ID: {letter.id}")
            print(f"Title: {letter.title}")
            print(f"Status: {letter.status}")
            print(f"Firm: {firm_name} ({letter.firm_id})")
            print(f"Created By: {creator_name if creator_name else 'N/A'}")
            print(f"Template: {template_name if template_name else 'N/A'}")
            if letter.docx_s3_key:
                print(f"DOCX S3 Key: {letter.docx_s3_key}")
            if letter.content:
                print(f"Content Preview: {letter.content[:100]}{'...' if len(letter.content) > 100 else ''}")
            print(f"Created At: {letter.created_at}")
            print(f"Updated At: {letter.updated_at}")
            print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error querying letters: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        check_letters()
        print("\n✅ Query complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

