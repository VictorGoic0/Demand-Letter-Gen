#!/usr/bin/env python3
"""
Query script to check templates in the database.

Usage:
    cd backend
    python scripts/check_template_table.py

Make sure:
    1. Docker Compose is running (database)
    2. Virtual environment is activated (if using venv)
"""
import os
import sys
import json
from dotenv import load_dotenv

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv(os.path.join(backend_dir, '.env'))

from shared.database import SessionLocal
from shared.models import LetterTemplate, Firm, User


def check_templates():
    """Query and display all templates."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 60)
        print("Templates Table Query")
        print("=" * 60)
        
        templates = db.query(LetterTemplate).all()
        
        if not templates:
            print("No templates found in database.")
            return
        
        print(f"\nFound {len(templates)} template(s):\n")
        
        for template in templates:
            # Get firm name
            firm = db.query(Firm).filter(Firm.id == template.firm_id).first()
            firm_name = firm.name if firm else "Unknown"
            
            # Get creator name if exists
            creator_name = None
            if template.created_by:
                creator = db.query(User).filter(User.id == template.created_by).first()
                creator_name = creator.name if creator else "Unknown"
            
            print(f"ID: {template.id}")
            print(f"Name: {template.name}")
            print(f"Firm: {firm_name} ({template.firm_id})")
            print(f"Is Default: {template.is_default}")
            print(f"Created By: {creator_name if creator_name else 'N/A'}")
            if template.letterhead_text:
                print(f"Letterhead: {template.letterhead_text[:100]}{'...' if len(template.letterhead_text) > 100 else ''}")
            if template.opening_paragraph:
                print(f"Opening Paragraph: {template.opening_paragraph[:100]}{'...' if len(template.opening_paragraph) > 100 else ''}")
            if template.closing_paragraph:
                print(f"Closing Paragraph: {template.closing_paragraph[:100]}{'...' if len(template.closing_paragraph) > 100 else ''}")
            if template.sections:
                sections_str = json.dumps(template.sections) if isinstance(template.sections, list) else str(template.sections)
                print(f"Sections: {sections_str[:100]}{'...' if len(sections_str) > 100 else ''}")
            print(f"Created At: {template.created_at}")
            print(f"Updated At: {template.updated_at}")
            print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error querying templates: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        check_templates()
        print("\n✅ Query complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

