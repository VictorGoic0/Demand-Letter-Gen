#!/usr/bin/env python3
"""
Test script for document service upload endpoint.

Usage:
    cd backend
    python scripts/test_document_api.py

Make sure:
    1. Docker Compose is running (database)
    2. Firm and users are seeded (run seed_test_firm.py and seed_test_users.py first)
    3. AWS credentials are configured in .env file
    4. Virtual environment is activated (if using venv)
"""
import os
import sys
import io
from dotenv import load_dotenv

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv(os.path.join(backend_dir, '.env'))

from shared.database import SessionLocal
from shared.models import Firm, User
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.document_service.router import router as document_router
from shared.exceptions import register_exception_handlers


def create_test_app():
    """Create a FastAPI test app with document router."""
    app = FastAPI(
        title="Document Service Test API",
        description="Test API for document service",
        version="1.0.0",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include document router
    app.include_router(document_router)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    return app


def create_test_pdf():
    """Create a simple test PDF file in memory."""
    # Create a minimal PDF content (valid PDF structure)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF"""
    return pdf_content


def test_upload_document(client, firm_id, user_id=None):
    """Test document upload endpoint."""
    print("\n" + "=" * 60)
    print("Testing Document Upload")
    print("=" * 60)
    
    pdf_content = create_test_pdf()
    
    files = {
        "file": ("test_document.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    
    params = {}
    if user_id:
        params["uploaded_by"] = str(user_id)
    
    response = client.post(
        f"/{firm_id}/documents/",
        files=files,
        params=params,
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Document uploaded successfully!")
        print(f"   Document ID: {data['document']['id']}")
        print(f"   Filename: {data['document']['filename']}")
        print(f"   File Size: {data['document']['file_size']} bytes")
        print(f"   MIME Type: {data['document']['mime_type']}")
        print(f"   Uploaded At: {data['document']['uploaded_at']}")
        return data['document']['id']
    else:
        print(f"❌ Upload failed:")
        print(f"   Response: {response.text}")
        return None


def main():
    """Run upload test."""
    print("\n" + "=" * 60)
    print("Document Upload Test")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Get test firm and user from database")
    print("  2. Test document upload endpoint")
    print("\nMake sure:")
    print("  - Docker Compose is running (database)")
    print("  - Firm and users are seeded (run seed_test_firm.py and seed_test_users.py)")
    print("  - AWS credentials are configured in .env file")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get test firm
        firm = db.query(Firm).filter(Firm.name == "Test Law Firm").first()
        if not firm:
            print("\n❌ Test firm not found. Please run seed_test_firm.py first.")
            return 1
        
        # Get first user
        user = db.query(User).filter(User.firm_id == firm.id).first()
        if not user:
            print("\n❌ No users found for test firm. Please run seed_test_users.py first.")
            return 1
        
        print(f"\nUsing firm: {firm.name} (ID: {firm.id})")
        print(f"Using user: {user.name} (ID: {user.id})")
        
        # Create test app and client
        app = create_test_app()
        client = TestClient(app)
        
        # Test upload
        document_id = test_upload_document(client, firm.id, user.id)
        
        if document_id:
            print("\n✅ Upload test passed!")
            return 0
        else:
            print("\n❌ Upload test failed!")
            return 1
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
