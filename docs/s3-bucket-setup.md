# S3 Bucket Setup Guide

Simple guide for creating and configuring S3 buckets for the Demand Letter Generator.

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured (`aws configure`)

## Create S3 Buckets

### Using AWS CLI

**1. Set your environment variables:**
```bash
AWS_REGION="us-east-2"  # or your preferred region
ENV="dev"  # or staging, prod
```

**2. Create documents bucket:**
```bash
aws s3api create-bucket \
  --bucket goico-demand-letters-documents-${ENV} \
  --region ${AWS_REGION} \
  --create-bucket-configuration LocationConstraint=${AWS_REGION}
```

**3. Create exports bucket:**
```bash
aws s3api create-bucket \
  --bucket goico-demand-letters-exports-${ENV} \
  --region ${AWS_REGION} \
  --create-bucket-configuration LocationConstraint=${AWS_REGION}
```

### Using AWS Console

1. Go to [S3 Console](https://console.aws.amazon.com/s3/)
2. Click "Create bucket"
3. Bucket name: `goico-demand-letters-documents-dev` (or your environment)
4. Select your AWS region
5. **Enable "Block all public access"** (recommended for documents)
6. Enable versioning (optional but recommended)
7. Click "Create bucket"
8. Repeat for `goico-demand-letters-exports-dev` (but **do NOT block public access** for exports - needed for presigned URLs)

## Configure Buckets

### Enable Versioning

```bash
# Documents bucket
aws s3api put-bucket-versioning \
  --bucket goico-demand-letters-documents-${ENV} \
  --versioning-configuration Status=Enabled

# Exports bucket
aws s3api put-bucket-versioning \
  --bucket goico-demand-letters-exports-${ENV} \
  --versioning-configuration Status=Enabled
```

### Enable Encryption

```bash
# Documents bucket
aws s3api put-bucket-encryption \
  --bucket goico-demand-letters-documents-${ENV} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Exports bucket
aws s3api put-bucket-encryption \
  --bucket goico-demand-letters-exports-${ENV} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### Block Public Access

**Important:** Only block public access for the documents bucket. The exports bucket needs to allow presigned URLs for frontend access.

```bash
# Documents bucket - BLOCK public access (recommended for security)
aws s3api put-public-access-block \
  --bucket goico-demand-letters-documents-${ENV} \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Exports bucket - DO NOT block public access (needed for presigned URLs)
# Skip this step for exports bucket to allow presigned URL access
```

## Environment Variables

Add these to your `backend/.env` file:

```env
AWS_REGION=us-east-2
S3_BUCKET_DOCUMENTS=goico-demand-letters-documents-dev
S3_BUCKET_EXPORTS=goico-demand-letters-exports-dev
```

If using AWS credentials (not IAM roles), also add:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## Verify Setup

Test that your buckets are accessible:

```python
from shared.s3_client import get_s3_client
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

s3_client = get_s3_client()

# Check buckets exist
documents_bucket = os.getenv("S3_BUCKET_DOCUMENTS")
exports_bucket = os.getenv("S3_BUCKET_EXPORTS")

if s3_client.check_bucket_exists(documents_bucket):
    print(f"✅ Documents bucket accessible: {documents_bucket}")
else:
    print(f"❌ Documents bucket not accessible: {documents_bucket}")

if s3_client.check_bucket_exists(exports_bucket):
    print(f"✅ Exports bucket accessible: {exports_bucket}")
else:
    print(f"❌ Exports bucket not accessible: {exports_bucket}")
```

## Bucket Naming Convention

- **Documents bucket:** `goico-demand-letters-documents-{env}`
- **Exports bucket:** `goico-demand-letters-exports-{env}`

Where `{env}` is:
- `dev` for development
- `staging` for staging
- `prod` for production

### Production Buckets (Confirmed)

**Production bucket names:**
- Documents: `goico-demand-letters-documents-prod`
- Exports: `goico-demand-letters-exports-prod`
- Region: `us-east-2`

## Troubleshooting

### Bucket Already Exists
If you get "BucketAlreadyExists" error, the bucket name is already taken. Try:
- Adding a unique suffix (e.g., `-yourname`)
- Using a different environment name
- Checking if you already created it

### Access Denied
- Verify your AWS credentials have S3 permissions
- Check IAM user/role has `s3:CreateBucket` permission
- Ensure you're using the correct AWS account
- For production, verify Lambda execution role has proper S3 permissions

### Region Mismatch
- Ensure all buckets are in the same region
- Set `AWS_REGION` environment variable correctly
- Verify region in AWS Console
- Production buckets are in `us-east-2`

### Presigned URLs Not Working
- Verify exports bucket does NOT have public access blocked
- Check bucket policy allows presigned URL access
- Ensure Lambda execution role has `s3:GetObject` permission
- Verify presigned URL expiration time is reasonable (default: 1 hour)

### Production-Specific Issues

**Lambda Cannot Access Buckets:**
- Verify bucket policies include Lambda execution role ARN
- Check IAM role has S3 permissions
- For MVP, ensure AWS credentials are properly configured in Lambda environment variables

## Next Steps

Once buckets are created:
1. Update `backend/.env` with bucket names
2. Test S3 client with the verification script above
3. Start using S3 client in your application code

For S3 client usage examples, see [S3 Usage Guide](s3-usage.md).

