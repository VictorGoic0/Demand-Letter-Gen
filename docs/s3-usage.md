# S3 Client Usage Guide

This document provides examples of how to use the S3 client for document management in the Demand Letter Generator.

## Import

```python
from shared.s3_client import get_s3_client, S3Client
from shared.config import get_config
```

## Configuration

The S3 client reads configuration from environment variables:

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_DOCUMENTS=demand-letters-documents-dev
S3_BUCKET_EXPORTS=demand-letters-exports-dev
```

## Basic Usage

### Get S3 Client Instance

```python
# Using the singleton pattern (recommended)
s3_client = get_s3_client()

# Or create a new instance
s3_client = S3Client()

# With custom credentials
s3_client = S3Client(
    aws_access_key_id="custom_key",
    aws_secret_access_key="custom_secret",
    region_name="us-west-2"
)
```

### Upload a File

```python
from shared.config import get_config

config = get_config()
s3_client = get_s3_client()

# Upload from local file path
result = s3_client.upload_file(
    file_path="/path/to/local/document.pdf",
    bucket_name=config.aws.s3_bucket_documents,
    s3_key="firm-123/documents/document-456.pdf",
    metadata={"firm_id": "123", "document_id": "456"},
    content_type="application/pdf"
)

print(f"Uploaded to: {result['url']}")
```

### Upload a File Object (In-Memory)

```python
from io import BytesIO

# Example: Upload file from FastAPI request
async def upload_document(file: UploadFile):
    config = get_config()
    s3_client = get_s3_client()
    
    # Read file content
    content = await file.read()
    file_obj = BytesIO(content)
    
    # Upload to S3
    result = s3_client.upload_fileobj(
        file_obj=file_obj,
        bucket_name=config.aws.s3_bucket_documents,
        s3_key=f"firm-{firm_id}/documents/{file.filename}",
        content_type=file.content_type,
        metadata={
            "original_filename": file.filename,
            "uploaded_by": user_id
        }
    )
    
    return result
```

### Download a File

```python
# Download to local file
s3_client.download_file(
    bucket_name=config.aws.s3_bucket_documents,
    s3_key="firm-123/documents/document-456.pdf",
    destination_path="/tmp/downloaded-document.pdf"
)

# Download to file object (in-memory)
from io import BytesIO

file_obj = BytesIO()
s3_client.download_fileobj(
    bucket_name=config.aws.s3_bucket_documents,
    s3_key="firm-123/documents/document-456.pdf",
    file_obj=file_obj
)

# Reset file pointer to beginning
file_obj.seek(0)
content = file_obj.read()
```

### Delete a File

```python
result = s3_client.delete_file(
    bucket_name=config.aws.s3_bucket_documents,
    s3_key="firm-123/documents/document-456.pdf"
)

print(f"Status: {result['status']}")  # 'deleted'
```

### Generate Presigned URL

Presigned URLs allow temporary access to S3 objects without AWS credentials.

```python
# Generate URL for downloading (GET)
url = s3_client.generate_presigned_url(
    bucket_name=config.aws.s3_bucket_documents,
    s3_key="firm-123/documents/document-456.pdf",
    expiration=3600,  # 1 hour
    http_method="GET"
)

# User can now download the file using this URL
print(f"Download URL (valid for 1 hour): {url}")

# Generate URL for uploading (PUT)
upload_url = s3_client.generate_presigned_url(
    bucket_name=config.aws.s3_bucket_documents,
    s3_key="firm-123/documents/new-document.pdf",
    expiration=300,  # 5 minutes
    http_method="PUT"
)

# Client can upload directly to S3 using this URL
```

### Check if Bucket Exists

```python
if s3_client.check_bucket_exists(config.aws.s3_bucket_documents):
    print("Bucket exists and is accessible")
else:
    print("Bucket does not exist or is not accessible")
```

### List Files in Bucket

```python
# List all files with a specific prefix
objects = s3_client.list_files(
    bucket_name=config.aws.s3_bucket_documents,
    prefix="firm-123/documents/",
    max_keys=100
)

for obj in objects:
    print(f"Key: {obj['key']}")
    print(f"Size: {obj['size']} bytes")
    print(f"Last Modified: {obj['last_modified']}")
    print(f"ETag: {obj['etag']}")
    print("---")
```

### Get Object Metadata

```python
metadata = s3_client.get_object_metadata(
    bucket_name=config.aws.s3_bucket_documents,
    s3_key="firm-123/documents/document-456.pdf"
)

print(f"Content Length: {metadata['content_length']}")
print(f"Content Type: {metadata['content_type']}")
print(f"Last Modified: {metadata['last_modified']}")
print(f"Custom Metadata: {metadata['metadata']}")
```

## Complete Example: Document Upload Service

```python
from typing import Optional
from fastapi import HTTPException
from shared.s3_client import get_s3_client
from shared.config import get_config
from shared.models.document import Document
from sqlalchemy.orm import Session
import uuid
import os

async def upload_document_to_s3(
    db: Session,
    firm_id: str,
    user_id: str,
    file: UploadFile,
) -> Document:
    """
    Upload a document to S3 and create a database record.
    
    Args:
        db: Database session
        firm_id: Firm ID
        user_id: User ID who is uploading
        file: FastAPI UploadFile object
        
    Returns:
        Document model instance
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Get configuration
        config = get_config()
        s3_client = get_s3_client()
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Create S3 key with proper structure
        file_extension = os.path.splitext(file.filename)[1]
        s3_key = f"firm-{firm_id}/documents/{doc_id}{file_extension}"
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Upload to S3
        from io import BytesIO
        file_obj = BytesIO(content)
        
        result = s3_client.upload_fileobj(
            file_obj=file_obj,
            bucket_name=config.aws.s3_bucket_documents,
            s3_key=s3_key,
            content_type=file.content_type or "application/octet-stream",
            metadata={
                "firm_id": firm_id,
                "document_id": doc_id,
                "original_filename": file.filename,
                "uploaded_by": user_id
            }
        )
        
        # Create database record
        document = Document(
            id=uuid.UUID(doc_id),
            firm_id=uuid.UUID(firm_id),
            uploaded_by=uuid.UUID(user_id),
            filename=file.filename,
            file_size=file_size,
            s3_key=s3_key,
            mime_type=file.content_type or "application/octet-stream"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
        
    except Exception as e:
        db.rollback()
        # Try to cleanup S3 if database failed
        try:
            s3_client.delete_file(
                bucket_name=config.aws.s3_bucket_documents,
                s3_key=s3_key
            )
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )


async def get_document_download_url(
    db: Session,
    document_id: str,
    expiration: int = 3600
) -> str:
    """
    Get a presigned URL to download a document.
    
    Args:
        db: Database session
        document_id: Document ID
        expiration: URL expiration in seconds (default: 1 hour)
        
    Returns:
        Presigned URL string
        
    Raises:
        HTTPException: If document not found or URL generation fails
    """
    # Get document from database
    document = db.query(Document).filter(
        Document.id == uuid.UUID(document_id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        config = get_config()
        s3_client = get_s3_client()
        
        url = s3_client.generate_presigned_url(
            bucket_name=config.aws.s3_bucket_documents,
            s3_key=document.s3_key,
            expiration=expiration,
            http_method="GET"
        )
        
        return url
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate download URL: {str(e)}"
        )


async def delete_document_from_s3(
    db: Session,
    document_id: str,
) -> None:
    """
    Delete a document from S3 and database.
    
    Args:
        db: Database session
        document_id: Document ID
        
    Raises:
        HTTPException: If document not found or deletion fails
    """
    # Get document from database
    document = db.query(Document).filter(
        Document.id == uuid.UUID(document_id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        config = get_config()
        s3_client = get_s3_client()
        
        # Delete from S3
        s3_client.delete_file(
            bucket_name=config.aws.s3_bucket_documents,
            s3_key=document.s3_key
        )
        
        # Delete from database
        db.delete(document)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )
```

## Error Handling

The S3 client raises exceptions for various error conditions:

```python
from botocore.exceptions import ClientError

try:
    result = s3_client.upload_file(
        file_path="document.pdf",
        bucket_name="my-bucket",
        s3_key="documents/doc.pdf"
    )
except FileNotFoundError as e:
    print(f"Local file not found: {e}")
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'NoSuchBucket':
        print("Bucket does not exist")
    elif error_code == 'AccessDenied':
        print("Access denied - check IAM permissions")
    else:
        print(f"AWS error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Use Consistent Key Naming

Organize S3 keys with a consistent structure:

```
firm-{firm_id}/documents/{document_id}.{extension}
firm-{firm_id}/exports/{letter_id}.docx
```

### 2. Set Appropriate Metadata

Add metadata to help track and organize files:

```python
metadata = {
    "firm_id": "123",
    "document_id": "456",
    "uploaded_by": "user-789",
    "content_category": "medical_records"
}
```

### 3. Use Content Types

Always specify the correct content type:

```python
content_type_map = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".txt": "text/plain"
}
```

### 4. Handle Large Files

For large files (>5MB), consider using multipart upload:

```python
# For very large files, boto3 automatically uses multipart upload
# Just use the standard upload methods
s3_client.upload_file(
    file_path="large-document.pdf",
    bucket_name=bucket,
    s3_key=key
)
```

### 5. Clean Up Temporary Files

Always clean up local temporary files:

```python
import os

temp_file = "/tmp/document.pdf"
try:
    s3_client.upload_file(temp_file, bucket, key)
finally:
    if os.path.exists(temp_file):
        os.remove(temp_file)
```

### 6. Use Presigned URLs for Direct Upload

For better performance, use presigned URLs for direct client-to-S3 uploads:

```python
# Backend generates presigned URL
upload_url = s3_client.generate_presigned_url(
    bucket_name=bucket,
    s3_key=key,
    expiration=300,  # 5 minutes
    http_method="PUT"
)

# Return URL to frontend
return {"upload_url": upload_url, "s3_key": key}

# Frontend uploads directly to S3
# fetch(upload_url, {
#     method: 'PUT',
#     body: file,
#     headers: {'Content-Type': file.type}
# })
```

### 7. Implement Retry Logic

For production, implement retry logic for transient failures:

```python
from botocore.config import Config
import boto3

config = Config(
    retries = {
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)

s3_client = boto3.client('s3', config=config)
```

## Security Considerations

1. **Never expose S3 keys directly** - Use presigned URLs instead
2. **Set appropriate expiration times** - Keep presigned URL expiration as short as possible
3. **Use HTTPS** - All S3 operations use HTTPS by default
4. **Implement access control** - Verify user permissions before generating URLs
5. **Enable bucket encryption** - Use server-side encryption for all buckets
6. **Regular audits** - Monitor S3 access logs for suspicious activity

## Troubleshooting

### Issue: Access Denied

**Solution:** Check IAM permissions and ensure the S3 access policy is attached to the Lambda execution role.

### Issue: Bucket Not Found

**Solution:** Verify bucket name in environment variables and ensure the bucket exists in the correct region.

### Issue: Connection Timeout

**Solution:** Check network connectivity, VPC configuration, and security groups if using VPC endpoints.

### Issue: File Upload Fails

**Solution:** Check file size limits, available disk space, and memory limits in Lambda.

## Additional Resources

- [boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
- [Presigned URLs Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)

