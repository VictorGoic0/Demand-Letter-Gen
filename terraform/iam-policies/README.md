# IAM Policy JSON Examples

This directory contains IAM policy JSON files that can be used to create policies for the Demand Letter Generator application.

## Policy Files

### 1. s3-access-policy.json
Grants access to S3 buckets for document storage and exports.

**Create Policy:**
```bash
aws iam create-policy \
  --policy-name DemandLetterS3AccessPolicy \
  --policy-document file://s3-access-policy.json
```

**Attach to Role:**
```bash
aws iam attach-role-policy \
  --role-name your-lambda-role \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/DemandLetterS3AccessPolicy
```

### 2. lambda-execution-policy.json
Grants Lambda functions permissions for execution, VPC access, and Secrets Manager.

**Create Policy:**
```bash
aws iam create-policy \
  --policy-name DemandLetterLambdaExecutionPolicy \
  --policy-document file://lambda-execution-policy.json
```

### 3. rds-access-policy.json
Grants access to RDS instances for database operations.

**Create Policy:**
```bash
aws iam create-policy \
  --policy-name DemandLetterRDSAccessPolicy \
  --policy-document file://rds-access-policy.json
```

### 4. cloudwatch-logs-policy.json
Grants access to CloudWatch Logs for monitoring and debugging.

**Create Policy:**
```bash
aws iam create-policy \
  --policy-name DemandLetterCloudWatchLogsPolicy \
  --policy-document file://cloudwatch-logs-policy.json
```

**Note:** This is already included in the AWS managed policy `AWSLambdaBasicExecutionRole`.

## Creating a Lambda Execution Role

To create a complete Lambda execution role with all necessary policies:

```bash
# Set variables
ENV="dev"  # or staging, prod
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="demand-letter-lambda-role-${ENV}"

# Create the role
aws iam create-role \
  --role-name ${ROLE_NAME} \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach AWS managed policies
aws iam attach-role-policy \
  --role-name ${ROLE_NAME} \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name ${ROLE_NAME} \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole

# Create and attach custom policies
aws iam create-policy \
  --policy-name DemandLetterS3AccessPolicy-${ENV} \
  --policy-document file://s3-access-policy.json

aws iam attach-role-policy \
  --role-name ${ROLE_NAME} \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/DemandLetterS3AccessPolicy-${ENV}

aws iam create-policy \
  --policy-name DemandLetterLambdaExecutionPolicy-${ENV} \
  --policy-document file://lambda-execution-policy.json

aws iam attach-role-policy \
  --role-name ${ROLE_NAME} \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/DemandLetterLambdaExecutionPolicy-${ENV}

aws iam create-policy \
  --policy-name DemandLetterRDSAccessPolicy-${ENV} \
  --policy-document file://rds-access-policy.json

aws iam attach-role-policy \
  --role-name ${ROLE_NAME} \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/DemandLetterRDSAccessPolicy-${ENV}
```

## Customization

Before using these policies, make sure to customize:

1. **Bucket Names:** Replace `demand-letters-documents-*` and `demand-letters-exports-*` with your actual bucket names
2. **Database User:** Replace `demand_letter_user` in the RDS policy with your actual database user
3. **Resource ARNs:** Update any ARNs to match your AWS account and resources
4. **Regions:** Adjust region-specific resources as needed

## Security Best Practices

1. **Principle of Least Privilege:** Only grant permissions that are absolutely necessary
2. **Environment Separation:** Use different policies/roles for dev, staging, and production
3. **Regular Audits:** Review and audit IAM policies regularly
4. **Use Tags:** Tag policies and roles for better organization and cost tracking
5. **Version Control:** Keep policy JSON files in version control
6. **Testing:** Test policies in development before applying to production

## Additional Resources

- [AWS IAM Policy Generator](https://awspolicygen.s3.amazonaws.com/policygen.html)
- [IAM Policy Simulator](https://policysim.aws.amazon.com/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

