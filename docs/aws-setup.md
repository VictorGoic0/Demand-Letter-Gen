# AWS Infrastructure Setup Guide

This document provides detailed instructions for setting up AWS infrastructure for the Demand Letter Generator application.

## Table of Contents

- [IAM Policies](#iam-policies)
  - [S3 Access Policy](#s3-access-policy)
  - [Lambda Execution Policy](#lambda-execution-policy)
  - [RDS Access Policy](#rds-access-policy)
  - [CloudWatch Logs Policy](#cloudwatch-logs-policy)
- [S3 Configuration](#s3-configuration)
- [RDS Configuration](#rds-configuration)
- [Lambda Configuration](#lambda-configuration)
- [Security Best Practices](#security-best-practices)

---

## IAM Policies

### S3 Access Policy

This policy grants read and write access to the S3 buckets used for document storage and exports.

**Policy Name:** `DemandLetterS3AccessPolicy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBuckets",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::demand-letters-documents-*",
        "arn:aws:s3:::demand-letters-exports-*"
      ]
    },
    {
      "Sid": "ObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:GetObjectMetadata",
        "s3:PutObjectAcl"
      ],
      "Resource": [
        "arn:aws:s3:::demand-letters-documents-*/*",
        "arn:aws:s3:::demand-letters-exports-*/*"
      ]
    },
    {
      "Sid": "GeneratePresignedUrls",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::demand-letters-documents-*/*",
        "arn:aws:s3:::demand-letters-exports-*/*"
      ]
    }
  ]
}
```

**Usage:**
- Replace `demand-letters-documents-*` and `demand-letters-exports-*` with your actual bucket names
- Attach this policy to the IAM role used by Lambda functions
- For development, you can also attach to IAM users

---

### Lambda Execution Policy

This policy grants Lambda functions the necessary permissions to execute and access AWS services.

**Policy Name:** `DemandLetterLambdaExecutionPolicy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/demand-letter-*"
    },
    {
      "Sid": "VPCNetworkInterface",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface",
        "ec2:AssignPrivateIpAddresses",
        "ec2:UnassignPrivateIpAddresses"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:demand-letter/*"
    }
  ]
}
```

**Usage:**
- Attach this policy to the Lambda execution role
- The VPC permissions are needed if your Lambda functions need to access RDS in a VPC
- SecretsManager permissions allow secure retrieval of database credentials

---

### RDS Access Policy

This policy grants access to RDS instances from Lambda functions.

**Policy Name:** `DemandLetterRDSAccessPolicy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RDSConnectAccess",
      "Effect": "Allow",
      "Action": [
        "rds-db:connect"
      ],
      "Resource": "arn:aws:rds-db:*:*:dbuser:*/demand_letter_user"
    },
    {
      "Sid": "RDSDescribeAccess",
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances",
        "rds:DescribeDBClusters"
      ],
      "Resource": "*"
    }
  ]
}
```

**Usage:**
- Attach this policy to the Lambda execution role
- Replace `demand_letter_user` with your actual database user
- This is for IAM database authentication (recommended for production)

---

### CloudWatch Logs Policy

This policy grants access to CloudWatch Logs for monitoring and debugging.

**Policy Name:** `DemandLetterCloudWatchLogsPolicy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CreateLogGroup",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/demand-letter-*"
    },
    {
      "Sid": "WriteToLogStreams",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/demand-letter-*:*"
    },
    {
      "Sid": "DescribeLogs",
      "Effect": "Allow",
      "Action": [
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    }
  ]
}
```

**Usage:**
- Automatically included in AWS managed policy `AWSLambdaBasicExecutionRole`
- Use this custom policy if you need more granular control

---

## S3 Configuration

### Bucket Creation

Create two S3 buckets for the application:

1. **Documents Bucket:** Stores uploaded PDF and DOCX files
2. **Exports Bucket:** Stores generated demand letter exports

**Using AWS CLI:**

```bash
# Set your AWS region
AWS_REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ENV="dev"  # or staging, prod

# Create documents bucket
aws s3api create-bucket \
  --bucket demand-letters-documents-${ENV} \
  --region ${AWS_REGION} \
  --create-bucket-configuration LocationConstraint=${AWS_REGION}

# Create exports bucket
aws s3api create-bucket \
  --bucket demand-letters-exports-${ENV} \
  --region ${AWS_REGION} \
  --create-bucket-configuration LocationConstraint=${AWS_REGION}
```

**Note:** For `us-east-1`, omit the `--create-bucket-configuration` parameter:

```bash
aws s3api create-bucket \
  --bucket demand-letters-documents-${ENV} \
  --region us-east-1
```

### Bucket Configuration

#### Enable Versioning

```bash
aws s3api put-bucket-versioning \
  --bucket demand-letters-documents-${ENV} \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning \
  --bucket demand-letters-exports-${ENV} \
  --versioning-configuration Status=Enabled
```

#### Enable Server-Side Encryption

```bash
aws s3api put-bucket-encryption \
  --bucket demand-letters-documents-${ENV} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

aws s3api put-bucket-encryption \
  --bucket demand-letters-exports-${ENV} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

#### Configure Lifecycle Rules

For the exports bucket, configure automatic deletion of old files:

```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket demand-letters-exports-${ENV} \
  --lifecycle-configuration file://s3-lifecycle-config.json
```

**s3-lifecycle-config.json:**

```json
{
  "Rules": [
    {
      "Id": "DeleteOldExports",
      "Status": "Enabled",
      "Filter": {},
      "Expiration": {
        "Days": 30
      },
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 7
      }
    }
  ]
}
```

#### Block Public Access

```bash
aws s3api put-public-access-block \
  --bucket demand-letters-documents-${ENV} \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

aws s3api put-public-access-block \
  --bucket demand-letters-exports-${ENV} \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

#### Enable CORS (if needed for direct uploads from frontend)

```bash
aws s3api put-bucket-cors \
  --bucket demand-letters-documents-${ENV} \
  --cors-configuration file://s3-cors-config.json
```

**s3-cors-config.json:**

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://yourdomain.com"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

---

## RDS Configuration

### Database Instance Creation

**Recommended Configuration:**

- **Engine:** PostgreSQL 15
- **Instance Class:** 
  - Development: `db.t3.micro` or `db.t4g.micro`
  - Production: `db.t3.small` or larger based on load
- **Storage:** 
  - Development: 20 GB GP2
  - Production: 100+ GB GP3 with autoscaling
- **Multi-AZ:** Enabled for production
- **Backup Retention:** 7 days minimum for production

**Using AWS CLI:**

```bash
# Set variables
DB_INSTANCE_IDENTIFIER="demand-letters-db-${ENV}"
DB_NAME="demand_letters"
DB_USERNAME="demand_admin"
DB_PASSWORD="your-secure-password-here"  # Use AWS Secrets Manager in production
VPC_SECURITY_GROUP_ID="sg-xxxxxxxxx"
DB_SUBNET_GROUP_NAME="demand-letters-db-subnet-group"

# Create DB instance
aws rds create-db-instance \
  --db-instance-identifier ${DB_INSTANCE_IDENTIFIER} \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username ${DB_USERNAME} \
  --master-user-password ${DB_PASSWORD} \
  --allocated-storage 20 \
  --storage-type gp2 \
  --vpc-security-group-ids ${VPC_SECURITY_GROUP_ID} \
  --db-subnet-group-name ${DB_SUBNET_GROUP_NAME} \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "sun:04:00-sun:05:00" \
  --storage-encrypted \
  --enable-cloudwatch-logs-exports '["postgresql"]' \
  --auto-minor-version-upgrade \
  --publicly-accessible false \
  --tags Key=Environment,Value=${ENV} Key=Application,Value=DemandLetterGen
```

### Security Group Configuration

Create a security group for RDS that allows connections from Lambda:

```bash
# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name demand-letters-rds-sg-${ENV} \
  --description "Security group for Demand Letter RDS instance" \
  --vpc-id ${VPC_ID} \
  --output text --query GroupId)

# Add ingress rule for PostgreSQL (port 5432) from Lambda security group
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp \
  --port 5432 \
  --source-group ${LAMBDA_SECURITY_GROUP_ID}

# For development, you might want to allow access from your IP
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp \
  --port 5432 \
  --cidr $(curl -s ifconfig.me)/32
```

### Connection String Format

**Standard Connection:**

```
postgresql://username:password@endpoint:5432/database_name
```

**Example:**

```
postgresql://demand_admin:password@demand-letters-db-dev.xxxxx.us-east-1.rds.amazonaws.com:5432/demand_letters
```

**Environment Variables:**

```bash
DB_HOST=demand-letters-db-dev.xxxxx.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=demand_letters
DB_USER=demand_admin
DB_PASSWORD=your-secure-password
```

### RDS Connection Troubleshooting

#### Issue: Cannot connect to RDS from Lambda

**Solutions:**

1. **Check Security Groups:**
   - Ensure Lambda security group is allowed in RDS security group
   - Verify inbound rules on port 5432

2. **Check VPC Configuration:**
   - Lambda and RDS must be in the same VPC
   - Lambda needs to be in subnets with routes to RDS subnets
   - Check route tables and network ACLs

3. **Check RDS Instance Status:**
   ```bash
   aws rds describe-db-instances \
     --db-instance-identifier ${DB_INSTANCE_IDENTIFIER} \
     --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address]'
   ```

4. **Test Connection:**
   ```bash
   # From a Lambda function or EC2 in the same VPC
   psql -h your-rds-endpoint -U demand_admin -d demand_letters
   ```

#### Issue: Connection timeout

**Solutions:**

1. **Check NAT Gateway:** If Lambda is in private subnet, ensure NAT Gateway exists for internet access
2. **Check Subnet Routes:** Verify route tables have correct routes
3. **Check Network ACLs:** Ensure they allow traffic on port 5432

#### Issue: Authentication failed

**Solutions:**

1. **Verify Credentials:** Double-check username and password
2. **Check IAM Authentication:** If using IAM auth, ensure proper permissions
3. **Check Password Special Characters:** URL-encode special characters in connection string

### Backup Configuration Recommendations

**Automated Backups:**

- **Retention Period:** 7-30 days (7 minimum for production)
- **Backup Window:** During low-traffic hours (e.g., 3:00-4:00 AM)
- **Maintenance Window:** Different from backup window

**Manual Snapshots:**

Create manual snapshots before major deployments:

```bash
aws rds create-db-snapshot \
  --db-instance-identifier ${DB_INSTANCE_IDENTIFIER} \
  --db-snapshot-identifier ${DB_INSTANCE_IDENTIFIER}-manual-$(date +%Y%m%d-%H%M%S)
```

**Point-in-Time Recovery:**

- Automatically enabled with automated backups
- Can restore to any point within retention period

**Cross-Region Backups (Production):**

```bash
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:us-east-1:account:snapshot:source-snapshot \
  --target-db-snapshot-identifier target-snapshot \
  --source-region us-east-1 \
  --region us-west-2
```

---

## Lambda Configuration

### Execution Role

Create an IAM role for Lambda execution that combines all necessary policies:

```bash
# Create role
aws iam create-role \
  --role-name demand-letter-lambda-role-${ENV} \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name demand-letter-lambda-role-${ENV} \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name demand-letter-lambda-role-${ENV} \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole

# Attach custom policies (created from JSON above)
aws iam attach-role-policy \
  --role-name demand-letter-lambda-role-${ENV} \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/DemandLetterS3AccessPolicy
```

### Environment Variables

Lambda functions should have these environment variables:

```
# Database
DB_HOST=your-rds-endpoint
DB_PORT=5432
DB_NAME=demand_letters
DB_USER=demand_admin
DB_PASSWORD=stored-in-secrets-manager

# AWS
AWS_REGION=us-east-1
S3_BUCKET_DOCUMENTS=demand-letters-documents-dev
S3_BUCKET_EXPORTS=demand-letters-exports-dev

# OpenAI
OPENAI_API_KEY=stored-in-secrets-manager
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=false
```

---

## Security Best Practices

### 1. Use AWS Secrets Manager

Store sensitive credentials in AWS Secrets Manager instead of environment variables:

```bash
# Create secret for database password
aws secretsmanager create-secret \
  --name demand-letter/${ENV}/db-password \
  --secret-string "${DB_PASSWORD}"

# Create secret for OpenAI API key
aws secretsmanager create-secret \
  --name demand-letter/${ENV}/openai-api-key \
  --secret-string "${OPENAI_API_KEY}"
```

### 2. Enable Encryption

- **S3:** Enable server-side encryption (SSE-S3 or SSE-KMS)
- **RDS:** Enable encryption at rest
- **Lambda:** Encrypt environment variables with KMS
- **Secrets Manager:** Automatically encrypted with KMS

### 3. Implement Least Privilege

- Grant only necessary permissions to IAM roles
- Use resource-level permissions where possible
- Regularly audit and review IAM policies

### 4. Enable Logging and Monitoring

- **CloudWatch Logs:** Capture all Lambda logs
- **RDS Enhanced Monitoring:** Monitor database performance
- **S3 Access Logging:** Track bucket access
- **CloudTrail:** Audit AWS API calls

### 5. Network Security

- **Private Subnets:** Place RDS in private subnets (no public access)
- **VPC Endpoints:** Use VPC endpoints for AWS services to avoid internet routing
- **Security Groups:** Implement strict ingress/egress rules
- **NACLs:** Add network ACLs for additional subnet-level security

### 6. Regular Updates

- Enable automatic minor version upgrades for RDS
- Keep Lambda runtime updated
- Regularly update dependencies and packages

### 7. Backup and Disaster Recovery

- Enable automated RDS backups
- Create manual snapshots before deployments
- Test restore procedures regularly
- Consider cross-region replication for critical data

---

## Additional Resources

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)
- [Amazon RDS User Guide](https://docs.aws.amazon.com/rds/latest/userguide/)
- [Amazon S3 User Guide](https://docs.aws.amazon.com/s3/latest/userguide/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Secrets Manager User Guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/)

