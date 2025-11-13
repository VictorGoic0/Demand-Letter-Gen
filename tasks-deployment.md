# Demand Letter Generator - Production Deployment
# AWS Lambda + RDS Deployment Tasks (MVP Optimized)

## 🎯 MVP Deployment Overview

**Goal**: Deploy to AWS Lambda + RDS + Netlify for ~$15-30/month

**Cost Optimizations**:
- ✅ No VPC configuration = Lambda has default internet access (-$32/month NAT Gateway)
- ✅ No Secrets Manager (-$1/month)
- ✅ Single-AZ RDS db.t3.micro (-$15/month vs larger instances)
- ✅ Direct AWS credentials in env vars (faster setup)
- ✅ Basic CloudWatch only (no third-party monitoring)

**Network Architecture**:
- Lambda: No VPC config = runs in AWS managed VPC with internet access
- Can call OpenAI API directly (no NAT Gateway needed)
- Can connect to RDS (RDS has public access enabled, secured by security groups)
- API Gateway provides public HTTPS endpoint for frontend
- RDS security group restricts database access (strong password + IP filtering)

**Tech Stack**:
- Backend: AWS Lambda (Python 3.11) + API Gateway → HTTPS URL
- Database: RDS PostgreSQL (db.t3.micro, single-AZ)
- Storage: S3 (documents + exports)
- Frontend: Netlify (free tier)
- Monitoring: CloudWatch (basic logs only)

**PRs**:
1. S3 Bucket Setup
2. RDS PostgreSQL Setup
3. Environment Config - Simplified, no IAM/Secrets Manager
4. Lambda Function Definitions
5. Basic Monitoring - Simplified
6. Testing
7. Deployment
8. Frontend/Netlify

---

## PR #1: Production S3 Bucket Setup

### S3 Bucket Creation
- [ ] 1. Set AWS region for production (confirm: us-east-2?)
- [ ] 2. Create production documents bucket:
  - [ ] Bucket name: `goico-demand-letters-documents-prod`
  - [ ] Region: us-east-2 (or confirm preferred region)
  - [ ] Enable versioning
  - [ ] Enable encryption (AES256)
  - [ ] Block all public access
- [ ] 3. Create production exports bucket:
  - [ ] Bucket name: `goico-demand-letters-exports-prod`
  - [ ] Region: us-east-2 (or confirm preferred region)
  - [ ] Enable versioning
  - [ ] Enable encryption (AES256)
  - [ ] DO NOT block public access (needed for presigned URLs)

### S3 Configuration Script
- [ ] 4. Create `backend/scripts/create_prod_s3_buckets.sh`:
  - [ ] Add shebang and error handling
  - [ ] Set AWS_REGION variable
  - [ ] Set ENV="prod" variable
  - [ ] Add bucket creation commands with proper configuration
  - [ ] Add versioning enablement commands
  - [ ] Add encryption configuration commands
  - [ ] Add public access block for documents bucket
  - [ ] Add verification commands to check bucket creation
- [ ] 5. Make script executable: `chmod +x backend/scripts/create_prod_s3_buckets.sh`
- [ ] 6. Run script to create production S3 buckets
- [ ] 7. Verify buckets created successfully in AWS Console
- [ ] 8. Delete script after successful creation (cleanup)

### S3 Bucket Policies
- [ ] 9. Configure bucket policies for production:
  - [ ] Documents bucket: Restrict access to Lambda execution role
  - [ ] Exports bucket: Allow presigned URL access
- [ ] 10. Configure lifecycle rules (optional but recommended):
  - [ ] Documents bucket: Archive old files to Glacier after X days
  - [ ] Exports bucket: Delete files after X days (e.g., 7 days)

### Documentation Update
- [ ] 11. Update `docs/s3-bucket-setup.md` with production bucket names
- [ ] 12. Document bucket naming convention confirmation
- [ ] 13. Add troubleshooting section for production-specific issues

---

## PR #2: Production RDS PostgreSQL Setup

### ⚠️ Network Configuration: No VPC for Lambda
**Important**: Lambda will run WITHOUT VPC configuration (Option 1):
- Lambda has default internet access (can call OpenAI API)
- RDS must have **Public accessibility: Yes**
- Security through RDS security groups + strong password
- Saves $32/month on NAT Gateway

### RDS Instance Creation
- [ ] 1. Create RDS PostgreSQL instance via AWS Console:
  - [ ] Go to RDS → Create database
  - [ ] Engine: PostgreSQL 15
  - [ ] Template: Free tier (or Production based on budget)
  - [ ] DB instance identifier: `demand-letter-gen-prod`
  - [ ] Master username: `postgres`
  - [ ] Master password: Generate strong password (save securely!)
  - [ ] DB name: `postgres` (or `demand_letters_prod`)
  - [ ] Instance class: **db.t3.micro** (1 vCPU, 1GB RAM)
  - [ ] Storage: 20 GB (enable autoscaling recommended)
  - [ ] Storage autoscaling: Enable (max 100GB)
  - [ ] Single-AZ deployment (not Multi-AZ to save cost)
  - [ ] VPC: Default VPC
  - [ ] **Public accessibility: YES** (required for Lambda without VPC)
  - [ ] VPC security group: Create new `demand-letter-gen-rds-sg`
  - [ ] Backup retention: 7 days
  - [ ] Enable encryption at rest
  - [ ] Enable automated backups
  - [ ] Maintenance window: Choose off-peak time
- [ ] 2. Wait for RDS instance to be available (5-10 minutes)
- [ ] 3. Note RDS endpoint hostname from AWS Console
- [ ] 4. Note RDS port (default: 5432)

### Security Group Configuration
- [ ] 5. Configure RDS security group `demand-letter-gen-rds-sg`:
  - [ ] **Option A** (More secure): Allow PostgreSQL (5432) from your IP only (for testing)
    - Add your current IP: `[your-ip]/32`
    - Lambda will connect using this same security group
  - [ ] **Option B** (Less secure but easier): Allow PostgreSQL (5432) from 0.0.0.0/0
    - Still secure with strong password
    - Easier for MVP
  - [ ] **Recommended for MVP**: Start with Option A, can change to B if connection issues
- [ ] 6. Test connection from your local machine:
  ```bash
  psql -h [rds-endpoint] -U postgres -d postgres
  ```

### Database Initialization
- [ ] 7. Run Alembic migrations on production database:
  - [ ] Set production DB environment variables locally (create .env.prod)
  - [ ] Run: `alembic upgrade head`
  - [ ] Verify all tables created successfully
  - [ ] Check tables: `\dt` in psql
- [ ] 8. Verify database setup:
  - [ ] Run database check scripts from `backend/scripts/`
  - [ ] Verify all tables exist (firms, users, documents, templates, letters, letter_source_documents)

### Important Notes
- [ ] 9. Save RDS credentials securely (password manager or secure notes)
- [ ] 10. Document RDS endpoint for serverless.yml configuration
- [ ] 11. **Do NOT** commit RDS credentials to git

---

## PR #3: Environment Configuration (MVP Simplified)

### ⚠️ MVP Approach: Direct Credentials in Environment Variables
**Note**: For MVP speed, we're using AWS credentials directly in Lambda env vars instead of IAM roles/Secrets Manager. This is less secure but much faster to set up. Can migrate to IAM/Secrets Manager post-MVP.

### Create Production Environment Variables File
- [ ] 1. Create `backend/.env.prod` (DO NOT commit):
  - [ ] DB_HOST=[RDS endpoint from PR #2]
  - [ ] DB_PORT=5432
  - [ ] DB_NAME=demand_letters_prod
  - [ ] DB_USER=[RDS master username]
  - [ ] DB_PASSWORD=[RDS master password]
  - [ ] AWS_REGION=us-east-2
  - [ ] AWS_ACCESS_KEY_ID=[your AWS access key]
  - [ ] AWS_SECRET_ACCESS_KEY=[your AWS secret key]
  - [ ] S3_BUCKET_DOCUMENTS=goico-demand-letters-documents-prod
  - [ ] S3_BUCKET_EXPORTS=goico-demand-letters-exports-prod
  - [ ] OPENAI_API_KEY=[your OpenAI API key]
  - [ ] ENVIRONMENT=production
  - [ ] DEBUG=false
  - [ ] LOG_LEVEL=INFO
- [ ] 2. Ensure `.env.prod` is in `.gitignore`
- [ ] 3. Update `backend/.env.example` with production placeholders

### Update Serverless Configuration for MVP
- [ ] 4. Update `backend/serverless.yml` for simplified production:
  - [ ] Remove IAM role configuration (use default Lambda role)
  - [ ] Remove VPC configuration (Lambda in default/public subnet)
  - [ ] Update environment variables to read from .env.prod
  - [ ] Set appropriate memory and timeout for production
  - [ ] Configure basic API Gateway CORS
- [ ] 5. Verify serverless.yml has basic S3 permissions:
  - [ ] Serverless Framework will create basic execution role automatically
  - [ ] Add iamRoleStatements for S3 access only (simplified)

### AWS Credentials Setup
- [ ] 6. Verify AWS credentials are configured locally:
  - [ ] Run `aws configure` if not already done
  - [ ] Or use AWS access keys from AWS Console
- [ ] 7. Test AWS credentials work:
  - [ ] Run `aws s3 ls` to verify S3 access
  - [ ] Run `aws rds describe-db-instances --region us-east-2` to verify RDS access

---

## PR #4: Lambda Function Definitions and Deployment Configuration

### Define Lambda Functions in serverless.yml
- [ ] 1. Add functions section to `backend/serverless.yml`
- [ ] 2. Define health check function:
  ```yaml
  functions:
    healthCheck:
      handler: main.health_handler
      events:
        - http:
            path: /health
            method: get
            cors: true
      timeout: 10
      memorySize: 256
  ```
- [ ] 3. Define document service functions:
  - [ ] documentUpload (POST /{firm_id}/documents)
  - [ ] documentList (GET /{firm_id}/documents)
  - [ ] documentGet (GET /{firm_id}/documents/{document_id})
  - [ ] documentDelete (DELETE /{firm_id}/documents/{document_id})
  - [ ] documentDownloadUrl (GET /{firm_id}/documents/{document_id}/download-url)
- [ ] 4. Define template service functions:
  - [ ] templateCreate (POST /{firm_id}/templates)
  - [ ] templateList (GET /{firm_id}/templates)
  - [ ] templateGet (GET /{firm_id}/templates/{template_id})
  - [ ] templateUpdate (PUT /{firm_id}/templates/{template_id})
  - [ ] templateDelete (DELETE /{firm_id}/templates/{template_id})
- [ ] 5. Define letter service functions:
  - [ ] letterGenerate (POST /{firm_id}/letters/generate)
  - [ ] letterList (GET /{firm_id}/letters)
  - [ ] letterGet (GET /{firm_id}/letters/{letter_id})
  - [ ] letterUpdate (PUT /{firm_id}/letters/{letter_id})
  - [ ] letterDelete (DELETE /{firm_id}/letters/{letter_id})
  - [ ] letterFinalize (POST /{firm_id}/letters/{letter_id}/finalize)
- [ ] 6. Define parser service functions:
  - [ ] parseDocument (POST /{firm_id}/documents/{document_id}/parse)
- [ ] 7. Define AI service functions:
  - [ ] aiGenerate (POST /{firm_id}/ai/generate)
- [ ] 8. Configure memory and timeout per function:
  - [ ] Health check: 256MB, 10s
  - [ ] Document upload: 1024MB, 60s
  - [ ] Document list/get: 512MB, 30s
  - [ ] Template operations: 512MB, 30s
  - [ ] Letter generate: 2048MB, 300s (5 min for AI)
  - [ ] Letter finalize: 1024MB, 60s
  - [ ] Parser: 1024MB, 60s
  - [ ] AI generate: 2048MB, 300s
- [ ] 9. Configure CORS for all HTTP events
- [ ] 10. Add layers reference to all functions:
  ```yaml
  layers:
    - { Ref: PythonRequirementsLambdaLayer }
  ```

### Create Lambda Handlers
- [ ] 11. Verify all handlers exist in `backend/handlers/`:
  - [ ] document_handler.py
  - [ ] template_handler.py
  - [ ] letter_handler.py
- [ ] 12. Create main.py health handler (if not exists):
  ```python
  def health_handler(event, context):
      return {
          "statusCode": 200,
          "body": json.dumps({
              "status": "healthy",
              "service": "demand-letter-generator",
              "environment": os.getenv("ENVIRONMENT", "unknown")
          })
      }
  ```
- [ ] 13. Verify Mangum adapter configured in all handlers
- [ ] 14. Test handlers locally with `serverless offline`

### API Gateway Configuration
- [ ] 15. Configure API Gateway in `backend/serverless.yml`:
  - [ ] Enable request validation
  - [ ] Configure request throttling (rate and burst limits)
  - [ ] Configure binary media types (for file uploads)
  - [ ] Enable CloudWatch logging
  - [ ] Configure access logging
- [ ] 16. Add API Gateway configuration:
  ```yaml
  provider:
    apiGateway:
      binaryMediaTypes:
        - 'multipart/form-data'
        - 'application/pdf'
        - 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      minimumCompressionSize: 1024
      shouldStartNameWithService: true
  ```
- [ ] 17. Configure API Gateway request/response models (optional)
- [ ] 18. Configure API Gateway authorizer (if using custom auth)

### Deployment Scripts
- [ ] 19. Update `backend/package.json` scripts:
  - [ ] Verify deploy:prod script exists
  - [ ] Add script: `"deploy:prod:verbose": "serverless deploy --stage prod --verbose"`
  - [ ] Add script: `"info:prod": "serverless info --stage prod"`
  - [ ] Add script: `"logs:prod": "serverless logs --stage prod"`
- [ ] 20. Create deployment checklist document:
  - [ ] Pre-deployment verification steps
  - [ ] Deployment commands
  - [ ] Post-deployment verification steps
  - [ ] Rollback procedures

---

## PR #5: Basic CloudWatch Monitoring (MVP Simplified)

### Basic CloudWatch Log Configuration
- [ ] 1. Configure log retention in `backend/serverless.yml`:
  ```yaml
  provider:
    logRetentionInDays: 7  # Keep costs low for MVP
  ```
- [ ] 2. Verify CloudWatch logs are automatically created:
  - [ ] Serverless Framework creates log groups automatically
  - [ ] No additional configuration needed

### Basic Monitoring (No Alarms for MVP)
- [ ] 3. Document how to view logs in AWS Console:
  - [ ] CloudWatch > Log groups > /aws/lambda/[function-name]
  - [ ] Can filter and search logs
- [ ] 4. Document how to view logs via CLI:
  ```bash
  serverless logs -f functionName --tail --stage prod
  ```
- [ ] 5. Bookmark CloudWatch dashboard links for:
  - [ ] Lambda metrics (invocations, errors, duration)
  - [ ] API Gateway metrics (requests, latency, errors)
  - [ ] RDS metrics (CPU, connections, storage)

### Cost Monitoring (Optional but Recommended)
- [ ] 6. Set up basic AWS Cost Budget:
  - [ ] Create monthly budget: $50 (2x expected cost)
  - [ ] Set alert at 80% ($40)
  - [ ] Add your email for notifications
- [ ] 7. Check AWS Billing Dashboard weekly

**Note**: Advanced monitoring (alarms, X-Ray, dashboards) can be added post-MVP if needed.

---

## PR #6: Pre-Deployment Testing and Validation

### Local Testing with Production-like Configuration
- [ ] 1. Create test environment with production settings:
  - [ ] Use production-like database (local or staging)
  - [ ] Use production bucket names in test account (or staging buckets)
  - [ ] Test with production-like data volume
- [ ] 2. Run full integration tests:
  - [ ] Test document upload (large files)
  - [ ] Test document parsing
  - [ ] Test template CRUD operations
  - [ ] Test letter generation with real OpenAI API
  - [ ] Test letter finalization and export
- [ ] 3. Test error scenarios:
  - [ ] Invalid file types
  - [ ] Oversized files
  - [ ] Missing documents
  - [ ] Database connection failures
  - [ ] S3 access errors
  - [ ] OpenAI API errors/timeouts
- [ ] 4. Load testing (optional but recommended):
  - [ ] Test concurrent document uploads
  - [ ] Test concurrent letter generation
  - [ ] Verify database connection pooling

### Dependency Verification
- [ ] 5. Verify all Python dependencies are Lambda-compatible:
  - [ ] Check for compiled dependencies (psycopg2-binary, etc.)
  - [ ] Ensure all dependencies work on Amazon Linux 2
- [ ] 6. Test Lambda layer building:
  - [ ] Run `serverless package --stage prod`
  - [ ] Verify layer size (must be < 250MB unzipped)
  - [ ] Verify no missing dependencies
- [ ] 7. Test cold start performance:
  - [ ] Measure Lambda cold start times
  - [ ] Optimize if > 5 seconds

### Configuration Validation
- [ ] 8. Validate `backend/serverless.yml`:
  - [ ] Run `serverless print --stage prod`
  - [ ] Verify all environment variables resolve
  - [ ] Verify IAM permissions are correct
  - [ ] Verify VPC configuration is correct
- [ ] 9. Validate secrets in AWS Secrets Manager:
  - [ ] Confirm all required secrets exist
  - [ ] Test secret retrieval with IAM role
- [ ] 10. Dry-run deployment:
  - [ ] Run `serverless package --stage prod`
  - [ ] Review generated CloudFormation template
  - [ ] Check for any warnings or errors

### Documentation Review
- [ ] 11. Review and update all deployment documentation:
  - [ ] README.md
  - [ ] backend/README.md
  - [ ] backend/docs/lambda-deployment.md
  - [ ] docs/s3-bucket-setup.md
  - [ ] New docs created in previous PRs
- [ ] 12. Create deployment runbook:
  - [ ] Step-by-step deployment instructions
  - [ ] Rollback procedures
  - [ ] Troubleshooting guide
  - [ ] Emergency contacts

---

## PR #7: Production Deployment and Verification

### Initial Production Deployment
- [ ] 1. Set AWS credentials for production account:
  - [ ] Verify AWS CLI profile configured
  - [ ] Run `aws sts get-caller-identity` to verify account
- [ ] 2. Deploy Lambda layer first:
  ```bash
  cd backend
  serverless deploy --stage prod --verbose
  ```
- [ ] 3. Monitor deployment output:
  - [ ] Verify CloudFormation stack creation
  - [ ] Verify Lambda functions created
  - [ ] Verify API Gateway endpoints created
  - [ ] Note API Gateway base URL
- [ ] 4. Handle any deployment errors:
  - [ ] Check CloudFormation events
  - [ ] Check IAM permissions
  - [ ] Check VPC configuration
  - [ ] Check security group rules

### Post-Deployment Verification
- [ ] 5. Test health check endpoint:
  ```bash
  curl https://[api-gateway-url]/prod/health
  ```
- [ ] 6. Test each Lambda function manually:
  - [ ] Invoke via AWS Console
  - [ ] Check CloudWatch logs for errors
  - [ ] Verify function completes successfully
- [ ] 7. Test API Gateway endpoints:
  - [ ] Health check
  - [ ] Document upload (with test file)
  - [ ] Template creation
  - [ ] Letter generation (end-to-end)
- [ ] 8. Verify database connectivity:
  - [ ] Check Lambda can connect to RDS
  - [ ] Verify CRUD operations work
  - [ ] Check database logs for errors
- [ ] 9. Verify S3 access:
  - [ ] Upload test document
  - [ ] Download test document
  - [ ] Verify presigned URLs work
  - [ ] Delete test document
- [ ] 10. Test OpenAI API integration:
  - [ ] Generate test letter
  - [ ] Verify API key works
  - [ ] Check OpenAI usage dashboard

### Production Data Seeding
- [ ] 11. Seed initial production data (if needed):
  - [ ] Create initial firm record
  - [ ] Create admin user
  - [ ] Create default template
- [ ] 12. Run database verification script:
  - [ ] Check all tables exist
  - [ ] Check indexes created
  - [ ] Verify foreign key constraints

### Monitoring Setup Verification
- [ ] 13. Verify CloudWatch logs are appearing:
  - [ ] Check Lambda function logs
  - [ ] Check API Gateway access logs
  - [ ] Check RDS logs
- [ ] 14. Verify CloudWatch metrics are reporting:
  - [ ] Lambda invocations
  - [ ] API Gateway requests
  - [ ] RDS connections
- [ ] 15. Test CloudWatch alarms:
  - [ ] Trigger a test alarm (if possible)
  - [ ] Verify SNS notification received
- [ ] 16. Verify X-Ray traces appearing (if enabled)

### Performance Verification
- [ ] 17. Measure baseline performance metrics:
  - [ ] API response times
  - [ ] Lambda execution duration
  - [ ] Database query performance
  - [ ] Letter generation time
- [ ] 18. Document baseline metrics for future comparison

### Security Verification
- [ ] 19. Verify security configurations:
  - [ ] S3 buckets have correct access policies
  - [ ] RDS is not publicly accessible
  - [ ] Lambda functions are in VPC
  - [ ] Secrets are stored in Secrets Manager (not code)
  - [ ] CloudWatch logs don't contain sensitive data
- [ ] 20. Run security audit:
  - [ ] AWS Trusted Advisor checks
  - [ ] AWS Config compliance checks (if enabled)
  - [ ] Review IAM policies for least privilege

### Documentation Update
- [ ] 21. Document production environment:
  - [ ] API Gateway URLs
  - [ ] CloudWatch dashboard links
  - [ ] RDS endpoint (without credentials)
  - [ ] S3 bucket names
  - [ ] AWS region
- [ ] 22. Create production runbook:
  - [ ] Common operations
  - [ ] Troubleshooting procedures
  - [ ] Emergency procedures
  - [ ] On-call guide
- [ ] 23. Update README with production deployment status

### Rollback Plan Verification
- [ ] 24. Document rollback procedures:
  - [ ] How to rollback to previous version
  - [ ] Database rollback procedures
  - [ ] How to restore from backup
- [ ] 25. Test rollback capability (if possible):
  - [ ] Deploy a test version
  - [ ] Rollback to previous version
  - [ ] Verify application works after rollback

---

## PR #8: Frontend Production Configuration

### Frontend Environment Configuration
- [ ] 1. Create `frontend/.env.production`:
  - [ ] VITE_API_URL=[production-api-gateway-url]
  - [ ] VITE_ENVIRONMENT=production
  - [ ] Any other production-specific variables
- [ ] 2. Verify production API URL in frontend code
- [ ] 3. Update CORS configuration in backend if needed:
  - [ ] Add production frontend domain to allowed origins
  - [ ] Update `backend/serverless.yml` CORS settings

### Frontend Build for Production
- [ ] 4. Build frontend for production:
  ```bash
  cd frontend
  npm run build
  ```
- [ ] 5. Verify production build:
  - [ ] Check dist/ directory created
  - [ ] Verify assets are minified
  - [ ] Check for build warnings/errors
- [ ] 6. Test production build locally:
  ```bash
  npm run preview
  ```

### Frontend Deployment (Choose One)

#### Option A: Deploy to Vercel
- [ ] 7a. Install Vercel CLI:
  ```bash
  npm install -g vercel
  ```
- [ ] 8a. Configure Vercel project:
  - [ ] Run `vercel` in frontend directory
  - [ ] Link to Vercel account
  - [ ] Configure project settings
- [ ] 9a. Set environment variables in Vercel:
  - [ ] Add VITE_API_URL
  - [ ] Add any other production variables
- [ ] 10a. Deploy to production:
  ```bash
  vercel --prod
  ```
- [ ] 11a. Verify deployment URL
- [ ] 12a. Configure custom domain (if applicable)

#### Option B: Deploy to AWS S3 + CloudFront
- [ ] 7b. Create S3 bucket for frontend:
  - [ ] Bucket name: `demand-letter-gen-frontend-prod`
  - [ ] Enable static website hosting
  - [ ] Configure bucket policy for public read
- [ ] 8b. Upload build to S3:
  ```bash
  aws s3 sync dist/ s3://demand-letter-gen-frontend-prod --delete
  ```
- [ ] 9b. Create CloudFront distribution:
  - [ ] Origin: S3 bucket
  - [ ] Default root object: index.html
  - [ ] Error pages: Redirect to index.html (for SPA routing)
  - [ ] SSL certificate: Use ACM certificate or CloudFront default
- [ ] 10b. Configure CloudFront error pages:
  - [ ] 403 -> /index.html (for SPA routing)
  - [ ] 404 -> /index.html (for SPA routing)
- [ ] 11b. Wait for CloudFront deployment (15-20 minutes)
- [ ] 12b. Test CloudFront URL
- [ ] 13b. Configure custom domain with Route53 (if applicable):
  - [ ] Create A record pointing to CloudFront
  - [ ] Verify DNS propagation

#### Option C: Deploy to Netlify
- [ ] 7c. Install Netlify CLI:
  ```bash
  npm install -g netlify-cli
  ```
- [ ] 8c. Login to Netlify:
  ```bash
  netlify login
  ```
- [ ] 9c. Initialize Netlify site:
  ```bash
  netlify init
  ```
- [ ] 10c. Configure build settings:
  - [ ] Build command: `npm run build`
  - [ ] Publish directory: `dist`
- [ ] 11c. Set environment variables in Netlify:
  - [ ] Add VITE_API_URL
  - [ ] Add any other production variables
- [ ] 12c. Deploy to production:
  ```bash
  netlify deploy --prod
  ```
- [ ] 13c. Verify deployment URL
- [ ] 14c. Configure custom domain (if applicable)

### Frontend Post-Deployment
- [ ] 13. Test production frontend:
  - [ ] Verify all pages load
  - [ ] Test user registration/login
  - [ ] Test document upload
  - [ ] Test template management
  - [ ] Test letter generation
- [ ] 14. Verify API integration:
  - [ ] Check browser console for errors
  - [ ] Verify API calls to production backend
  - [ ] Test error handling
- [ ] 15. Performance testing:
  - [ ] Run Lighthouse audit
  - [ ] Check page load times
  - [ ] Verify asset compression
- [ ] 16. Mobile responsiveness testing:
  - [ ] Test on mobile devices
  - [ ] Verify touch interactions
  - [ ] Check viewport settings

---

## Notes


### Cost Estimates (Monthly, MVP Production)
- RDS db.t3.micro (single-AZ): ~$12-15
- Lambda (estimated 100K requests): ~$0-2
- API Gateway (100K requests): ~$0.35
- S3 (10GB storage, moderate access): ~$0.50-2
- CloudWatch Logs (basic): ~$1-5
- Data Transfer: ~$1-5

**Estimated Total: $15-30/month for MVP** 🎉

### Cost Savings vs Full Production Setup:
- No NAT Gateway: -$32/month
- No VPC Endpoints: -$7/month  
- No Secrets Manager: -$1/month
- Single-AZ RDS: -$15/month
- **Total Savings: ~$55/month**

### Pre-Deployment Decisions (CONFIRMED)

1. **AWS Region**: ✅ us-east-2
2. **RDS Instance Size**: ✅ db.t3.micro (~$12-15/month, 1GB RAM, sufficient for MVP)
3. **RDS Multi-AZ**: ✅ NO (single-AZ to save cost)
4. **VPC/NAT Gateway**: ✅ SKIP VPC for MVP (use default/public Lambda, saves ~$32/month)
5. **Custom Domain**: ⏭️ After deployment
6. **Authentication**: ⏭️ After deployment (not implemented yet)
7. **Frontend Hosting**: ✅ Netlify
8. **Cost Strategy**: ✅ Cheapest possible for MVP
9. **RDS Backup Retention**: ✅ 7 days
10. **CI/CD**: ✅ NO (removed from deployment plan)
11. **Monitoring**: ✅ CloudWatch only (no third-party for MVP)
12. **Node Version**: ✅ Node 18+ (local only, for Serverless Framework)
13. **IAM/Secrets Manager**: ✅ SKIP for MVP (use direct AWS credentials in env vars)

### Cleanup Tasks
- [ ] Remove temporary S3 bucket creation script after use
- [ ] Remove any test data from production
- [ ] Remove any debugging code or verbose logging
- [ ] Archive development/staging resources if no longer needed

---

## 🚀 Quick Start: Begin Deployment

Ready to deploy? Start with PR #1:

### 1. Create Production S3 Buckets

```bash
# Ensure AWS CLI is configured
aws sts get-caller-identity

# Run the bucket creation script
cd backend/scripts
./create_prod_s3_buckets.sh

# Verify buckets created
aws s3 ls | grep goico-demand-letters

# Clean up script
rm create_prod_s3_buckets.sh
```

### 2. Create RDS Instance

Use AWS Console:
1. Go to RDS → Create database
2. Engine: PostgreSQL 15
3. Template: Free tier (or Production)
4. DB instance identifier: `demand-letter-gen-prod`
5. Master username: `postgres`
6. Master password: (generate strong password)
7. Instance class: db.t3.micro
8. Storage: 20 GB (enable autoscaling)
9. Public access: Yes (for now, can restrict later)
10. Create database

Wait for RDS to be available, then:

```bash
# Get RDS endpoint
aws rds describe-db-instances \
  --db-instance-identifier demand-letter-gen-prod \
  --region us-east-2 \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text

# Test connection (replace with your endpoint)
psql -h [rds-endpoint] -U postgres -d postgres
```

### 3. Run Database Migrations

```bash
cd backend

# Create .env.prod with RDS endpoint
cat > .env.prod << EOF
DB_HOST=[your-rds-endpoint]
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=[your-rds-password]
AWS_REGION=us-east-2
S3_BUCKET_DOCUMENTS=goico-demand-letters-documents-prod
S3_BUCKET_EXPORTS=goico-demand-letters-exports-prod
OPENAI_API_KEY=[your-openai-key]
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
EOF

# Load env and run migrations
export $(cat .env.prod | xargs)
alembic upgrade head
```

### 4. Deploy to Lambda

```bash
cd backend

# Install dependencies
npm install

# Deploy
serverless deploy --stage prod

# Note the API Gateway URL from output
```

### 5. Deploy Frontend to Netlify

```bash
cd frontend

# Create .env.production with API Gateway URL
echo "VITE_API_URL=https://[your-api-gateway-url]/prod" > .env.production

# Build
npm run build

# Deploy to Netlify (first time)
npx netlify-cli deploy --prod --dir=dist
```

### 6. Test Production

```bash
# Test backend health
curl https://[api-gateway-url]/prod/health

# Test frontend
open https://[netlify-url]
```

**Done! Your application is live! 🎉**

Monitor costs at: https://console.aws.amazon.com/billing/

