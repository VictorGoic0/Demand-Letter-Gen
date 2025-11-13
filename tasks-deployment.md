# Demand Letter Generator - Production Deployment
# AWS Lambda + RDS Deployment Tasks (MVP Optimized)

## 🎯 MVP Deployment Overview

**Goal**: Deploy to AWS Lambda + RDS + Netlify for ~$15-30/month


**Tech Stack**:
- Backend: AWS Lambda (Python 3.11) + API Gateway → HTTPS URL
- Database: RDS PostgreSQL (db.t3.micro, single-AZ)
- Storage: S3 (documents + exports)
- Frontend: Netlify (free tier)
- Monitoring: CloudWatch (basic logs only)

**PRs**:
1. S3 Bucket Setup
2. RDS PostgreSQL Setup
3. Environment Config
4. Lambda Function Definitions
5. Basic Monitoring - Simplified
6. Testing
7. Deployment
8. Frontend/Netlify

---

## PR #1: Production S3 Bucket Setup ✅

### S3 Bucket Creation
- [x] 1. Set AWS region for production (confirm: us-east-2?)
- [x] 2. Create production documents bucket:
  - [x] Bucket name: `goico-demand-letters-documents-prod`
  - [x] Region: us-east-2 (or confirm preferred region)
  - [x] Enable versioning
  - [x] Enable encryption (AES256)
  - [x] Block all public access
- [x] 3. Create production exports bucket:
  - [x] Bucket name: `goico-demand-letters-exports-prod`
  - [x] Region: us-east-2 (or confirm preferred region)
  - [x] Enable versioning
  - [x] Enable encryption (AES256)
  - [x] DO NOT block public access (needed for presigned URLs)

### S3 Configuration Script
- [x] 4. Create `backend/scripts/create_prod_s3_buckets.sh`:
  - [x] Add shebang and error handling
  - [x] Set AWS_REGION variable
  - [x] Set ENV="prod" variable
  - [x] Add bucket creation commands with proper configuration
  - [x] Add versioning enablement commands
  - [x] Add encryption configuration commands
  - [x] Add public access block for documents bucket
  - [x] Add verification commands to check bucket creation
- [x] 5. Make script executable: `chmod +x backend/scripts/create_prod_s3_buckets.sh`
- [x] 6. Run script to create production S3 buckets
- [x] 7. Verify buckets created successfully in AWS Console
- [x] 8. Delete script after successful creation (cleanup)

### S3 Bucket Policies
- [x] 9. Configure bucket policies for production:
  - [x] Documents bucket: Restrict access to Lambda execution role
  - [x] Exports bucket: Allow presigned URL access
- [x] 10. Configure lifecycle rules (optional but recommended):
  - [x] Documents bucket: Archive old files to Glacier after X days
  - [x] Exports bucket: Delete files after X days (e.g., 7 days)

### Documentation Update
- [x] 11. Update `docs/s3-bucket-setup.md` with production bucket names
- [x] 12. Document bucket naming convention confirmation
- [x] 13. Add troubleshooting section for production-specific issues

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

### Database Initialization
- [x] 7. Run Alembic migrations on production database:
  - [x] Ensure `backend/.env.production` exists with production DB credentials
  - [x] Run: `cd backend && alembic upgrade head`
  - [x] Verify all tables created successfully
  - [x] Check tables: `\dt` in psql
- [x] 8. Verify database setup:
  - [x] Run database check scripts from `backend/scripts/`
  - [x] Verify all tables exist (firms, users, documents, templates, letters, letter_source_documents)
- [x] 9. Seed production database:
  - [x] Run seed scripts: `seed_test_firm.py` and `seed_test_users.py` (using `.env.production`)

### Important Notes
- [x] 10. Save RDS credentials securely (password manager or secure notes)
- [ ] 11. Document RDS endpoint for serverless.yml configuration
- [x] 12. **Do NOT** commit RDS credentials to git

---

## PR #3: Environment Configuration (MVP Simplified) ✅

### ⚠️ MVP Approach: Direct Credentials in Environment Variables
**Note**: For MVP speed, we're using AWS credentials directly in Lambda env vars instead of IAM roles/Secrets Manager. This is less secure but much faster to set up. Can migrate to IAM/Secrets Manager post-MVP.

### Create Production Environment Variables File
- [x] 1. Create `backend/.env.production` (DO NOT commit):
  - [x] DB_HOST=[RDS endpoint from PR #2]
  - [x] DB_PORT=5432
  - [x] DB_NAME=postgres (or demand_letters_prod)
  - [x] DB_USER=[RDS master username]
  - [x] DB_PASSWORD=[RDS master password]
  - [x] AWS_REGION=us-east-2
  - [x] AWS_ACCESS_KEY_ID=[your AWS access key]
  - [x] AWS_SECRET_ACCESS_KEY=[your AWS secret key]
  - [x] S3_BUCKET_DOCUMENTS=goico-demand-letters-documents-prod
  - [x] S3_BUCKET_EXPORTS=goico-demand-letters-exports-prod
  - [x] OPENAI_API_KEY=[your OpenAI API key]
  - [x] ENVIRONMENT=production
  - [x] DEBUG=false
  - [x] LOG_LEVEL=INFO
- [x] 2. Ensure `.env.production` is in `.gitignore`
- [x] 3. Create `backend/.env.example` with production placeholders

### Update Serverless Configuration for MVP
- [x] 4. Update `backend/serverless.yml` for simplified production:
  - [x] No IAM role configuration needed (use default Lambda role)
  - [x] No VPC configuration (Lambda in default/public subnet)
  - [x] Environment variables read from environment (via .env.production)
  - [x] Added AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to environment
  - [x] Basic API Gateway CORS configured
- [x] 5. Verify serverless.yml has basic S3 permissions:
  - [x] Serverless Framework will create basic execution role automatically
  - [x] iamRoleStatements for S3 access configured

### AWS Credentials Setup
- [x] 6. Verify AWS credentials are configured locally:
  - [x] AWS credentials configured in .env.production
  - [x] Helper script created: `load-env-production.sh` for loading env vars
- [x] 7. Test AWS credentials work:
  - [x] Credentials verified during S3 bucket setup (PR #1)
  - [x] Credentials verified during RDS setup (PR #2)

---

## PR #4: Lambda Function Definitions and Deployment Configuration ✅

### Define Lambda Functions in serverless.yml
- [x] 1. Add functions section to `backend/serverless.yml`
- [x] 2. Define health check function
- [x] 3. Define document service function (handles all document routes):
  - [x] documentUpload (POST /{firm_id}/documents)
  - [x] documentList (GET /{firm_id}/documents)
  - [x] documentGet (GET /{firm_id}/documents/{document_id})
  - [x] documentDelete (DELETE /{firm_id}/documents/{document_id})
  - [x] documentDownloadUrl (GET /{firm_id}/documents/{document_id}/download)
- [x] 4. Define template service function (handles all template routes):
  - [x] templateCreate (POST /{firm_id}/templates)
  - [x] templateList (GET /{firm_id}/templates)
  - [x] templateGetDefault (GET /{firm_id}/templates/default)
  - [x] templateGet (GET /{firm_id}/templates/{template_id})
  - [x] templateUpdate (PUT /{firm_id}/templates/{template_id})
  - [x] templateDelete (DELETE /{firm_id}/templates/{template_id})
- [x] 5. Define letter service function (handles all letter routes):
  - [x] letterList (GET /{firm_id}/letters)
  - [x] letterGet (GET /{firm_id}/letters/{letter_id})
  - [x] letterUpdate (PUT /{firm_id}/letters/{letter_id})
  - [x] letterDelete (DELETE /{firm_id}/letters/{letter_id})
  - [x] letterFinalize (POST /{firm_id}/letters/{letter_id}/finalize)
  - [x] letterExport (POST /{firm_id}/letters/{letter_id}/export)
- [x] 6. Define parser service function (handles parsing routes):
  - [x] parseDocument (POST /parse/document/{document_id})
  - [x] parseBatch (POST /parse/batch)
- [x] 7. Define AI service function (handles generation):
  - [x] aiGenerate (POST /generate/letter)
- [x] 8. Configure memory and timeout per function:
  - [x] Health check: 256MB, 10s
  - [x] Document service: 1024MB, 60s
  - [x] Template service: 512MB, 30s
  - [x] Letter service: 1024MB, 60s
  - [x] AI service: 2048MB, 300s (5 min for AI)
  - [x] Parser service: 1024MB, 60s
- [x] 9. Configure CORS for all HTTP events
- [x] 10. Add layers reference to all functions

### Create Lambda Handlers
- [x] 11. Verify all handlers exist in `backend/handlers/`:
  - [x] document_handler.py (updated to use actual router)
  - [x] template_handler.py (updated to use actual router)
  - [x] letter_handler.py (updated to use actual router)
  - [x] ai_handler.py (created)
  - [x] parser_handler.py (created)
- [x] 12. Create main.py health handler
- [x] 13. Verify Mangum adapter configured in all handlers (via LambdaHandler base class)
- [x] 14. Update Mangum base path to be dynamic based on stage

### API Gateway Configuration
- [x] 15. Configure API Gateway in `backend/serverless.yml`:
  - [x] Binary media types configured (for file uploads)
  - [x] Minimum compression size set
  - [x] CloudWatch logging enabled (logRetentionInDays: 7)
- [x] 16. API Gateway configuration already present (from PR #3)
- [x] 17. Request/response models (optional - skipped for MVP)
- [x] 18. API Gateway authorizer (optional - skipped for MVP)

### Deployment Scripts
- [x] 19. Update `backend/package.json` scripts:
  - [x] deploy:prod script exists (from PR #3)
  - [x] Added deploy:prod:verbose script
  - [x] Added info:prod script (from PR #3)
  - [x] Added logs:prod script (from PR #3)
- [x] 20. Deployment documentation:
  - [x] Deployment commands documented in package.json scripts
  - [x] Environment loading script created (load-env-production.sh)

### Deployment Notes
- [x] Successfully deployed to production (AWS Lambda + API Gateway)
- [x] Fixed environment variable naming (AWS_S3_BUCKET_DOCUMENTS, AWS_S3_BUCKET_EXPORTS)
- [x] Removed reserved AWS env vars (AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) - Lambda execution role provides these automatically
- [x] API Gateway URL includes stage prefix: `/prod/` (e.g., `https://[api-id].execute-api.us-east-2.amazonaws.com/prod/health`)
- [x] Mangum configured to strip stage prefix before routing to FastAPI
- [x] All Lambda functions deployed and accessible

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

## PR #8: Frontend Production Configuration (Netlify)

### Netlify Configuration
- [ ] 1. Create `frontend/netlify.toml`:
  - [ ] Build command: `npm run build`
  - [ ] Publish directory: `dist`
  - [ ] SPA redirect rules (redirect all routes to index.html)
- [ ] 2. Update CORS configuration in backend if needed:
  - [ ] Add Netlify domain to allowed origins in `backend/serverless.yml`
  - [ ] Update CORS settings to allow Netlify frontend

### Environment Variables
- [ ] 3. Create `frontend/.env.production`:
  - [ ] VITE_API_URL=[production-api-gateway-url]/prod
  - [ ] VITE_ENVIRONMENT=production
- [ ] 4. Note: Set VITE_API_URL in Netlify dashboard after linking project

### Deployment
- [ ] 5. Link project in Netlify dashboard (user will handle)
- [ ] 6. Set environment variables in Netlify dashboard (user will handle)
- [ ] 7. Verify deployment URL and test production frontend

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

# Ensure .env.production exists with RDS endpoint and credentials
# Then run migrations (alembic will automatically load .env.production)
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

