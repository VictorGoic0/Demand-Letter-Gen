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

## PR #5: Production Deployment Fixes & Troubleshooting

This PR documents all the fixes required to get the application working in production after initial deployment.

### Issues Encountered & Fixes

#### 1. Email Validator Dependency Issue
**Problem**: Lambda failing with `Runtime.ImportModuleError: No package metadata was found for email-validator`
- Pydantic 2.x's `EmailStr` type requires `email-validator` package metadata at runtime
- `serverless-python-requirements` with `slim: true` was stripping metadata

**Fixes**:
- [x] Removed `EmailStr` from `backend/services/auth_service/schemas.py` (changed to plain `str`)
- [x] Removed `email-validator>=2.0.0` from `backend/requirements.txt`
- [x] Changed `slim: true` to `slim: false` in `backend/serverless.yml` (preserves package metadata)

#### 2. Environment Variable Validation Issues
**Problem**: Lambda crashing with Pydantic validation errors for environment variables

**Issue A - Environment name mismatch**:
- serverless.yml set `ENVIRONMENT: ${self:provider.stage}` which resolves to `prod`
- config.py only accepts `development`, `staging`, `production`

**Fix**:
- [x] Changed `backend/serverless.yml` line 27 to hardcode: `ENVIRONMENT: production`

**Issue B - AWS Lambda environment variables rejected**:
- AWS Lambda automatically sets many `AWS_*` environment variables (e.g., `AWS_LAMBDA_FUNCTION_NAME`)
- `AWSConfig` class in config.py used `env_prefix="AWS_"` with strict validation
- Pydantic rejected Lambda's extra environment variables with `extra_forbidden` errors

**Fix**:
- [x] Added `extra="ignore"` to `AWSConfig.model_config` in `backend/shared/config.py` (line 54)

#### 3. CORS Configuration Issues
**Problem**: Browser blocking requests with CORS error - `Access-Control-Allow-Origin` cannot be wildcard `*` when credentials mode is `include`

**Root Cause**:
- Frontend `axios` client had `withCredentials: true` (not needed - we use localStorage, not cookies)
- Backend had `cors: true` in serverless.yml which defaults to wildcard `*`
- Wildcard CORS breaks when credentials are included

**Fixes**:
- [x] Removed `withCredentials: true` from `frontend/src/lib/api.ts`
- [x] Replaced all `cors: true` in `backend/serverless.yml` with explicit CORS configuration:
  ```yaml
  cors:
    origin: https://demand-letter-generator.netlify.app
    headers:
      - Content-Type
      - Authorization
      - X-Firm-Id
      - X-User-Id
    allowCredentials: false
  ```
- [x] Updated `backend/handlers/base.py` to hardcode Netlify domain in CORS origins (lines 40-45)
- [x] Updated `backend/main.py` health handler to use Netlify domain (line 210)

#### 4. Missing Auth Service Endpoint
**Problem**: `/login` endpoint returning 403/404 - endpoint not deployed

**Root Cause**: Auth service had router but no Lambda handler and wasn't configured in serverless.yml

**Fixes**:
- [x] Created `backend/handlers/auth_handler.py` (following pattern from other handlers)
- [x] Added `authService` function to `backend/serverless.yml` with `/login` POST endpoint

#### 5. RDS Connection Timeout
**Problem**: Lambda timing out when trying to connect to RDS PostgreSQL

**Root Cause**: RDS security group only allowed connections from specific IP (local machine), not from Lambda

**Fix**:
- [x] Updated RDS security group to allow inbound connections from `0.0.0.0/0` on port 5432
- Note: For MVP this is acceptable; for production, should use Lambda in VPC with RDS

#### 6. Template List Empty Page Size Validation Error
**Problem**: GET `/templates` returning 500 when no templates exist

**Root Cause**: `TemplateListResponse` has Pydantic validation `page_size >= 1`, but code was setting `page_size=len(templates)` which is 0 when empty

**Fix**:
- [x] Changed `backend/services/template_service/router.py` line 120 to: `page_size=len(templates) if len(templates) > 0 else 1`

#### 7. S3 Upload Failures (ONGOING)
**Problem**: Document uploads failing with `InvalidAccessKeyId` error

**Root Cause**: TBD - needs investigation
- S3 client trying to use AWS credentials from environment variables
- Lambda execution role should provide S3 access automatically
- Credentials in .env.production may be invalid or not being used correctly

**Attempted Fix (reverted)**:
- Tried making S3 client use IAM role when credentials not provided
- Reverted - need different approach

**Current Status**: File uploads not working - requires AWS credentials to be configured properly

### Deployment Scripts
- [x] Updated `backend/package.json` scripts to use `npx serverless` and proper env var loading:
  - `npm run deploy:prod` - Deploy to production
  - `npm run logs:prod` - View all prod logs  
  - `npm run logs:function` - View specific function logs
  - `npm run remove:prod` - Remove prod deployment
  - `npm run info:prod` - Get prod deployment info

### Lessons Learned

1. **Pydantic validation is too strict for MVP** - Overly strict validation (EmailStr, page_size >= 1, extra="forbid") causes production crashes on edge cases

2. **CORS wildcards break with credentials** - Always use explicit origins, never `*` when credentials might be involved

3. **Dev/Prod parity is critical** - Environment name mismatches and Lambda-specific env vars caused issues that didn't appear locally

4. **Serverless Framework quirks**:
   - `cors: true` defaults to wildcard
   - Must use `npx serverless` to ensure consistent version
   - Environment variables need to be loaded before deployment commands

5. **AWS Lambda execution roles** - Lambda should use execution role for AWS service access, not explicit credentials in environment



## PR #8: Frontend Production Configuration (Netlify)

### Netlify Configuration
- [x] 1. Create `frontend/netlify.toml`:
  - [x] Build command: `npm run build`
  - [x] Publish directory: `dist`
  - [x] SPA redirect rules (redirect all routes to index.html)
- [x] 2. Update CORS configuration in backend if needed:
  - [x] CORS already configured to allow all origins (`["*"]` in base handler and API Gateway)
  - [x] No changes needed - Netlify will work with current CORS settings

### Auth Service Deployment
- [x] 3. Add auth service Lambda function to `backend/serverless.yml`:
  - [x] Create `backend/handlers/auth_handler.py` (following pattern from other handlers)
  - [x] Add `authService` function definition with `/login` POST endpoint
  - [x] Configure CORS for auth endpoints
  - [x] Set appropriate timeout and memory size
- [ ] 4. Deploy auth service:
  - [ ] Run `serverless deploy --stage prod` to deploy auth service
  - [ ] Verify `/login` endpoint is accessible via API Gateway
  - [ ] Test login endpoint from Netlify frontend

### CORS Configuration for Production
- [x] 5. Update CORS to explicitly allow Netlify origin:
  - [x] Hardcode `https://demand-letter-generator.netlify.app` in `backend/handlers/base.py` default CORS origins
  - [x] Update `backend/main.py` to include Netlify domain in local dev CORS origins
  - [x] Update error response headers to use Netlify domain
  - [ ] Verify CORS headers are present in API Gateway responses after deployment
  - [ ] Test preflight (OPTIONS) requests work correctly from Netlify frontend

### Deployment
- [ ] 6. Link project in Netlify dashboard (user will handle)
- [ ] 7. Set environment variables in Netlify dashboard (user will handle)
- [ ] 8. Verify deployment URL and test production frontend

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

# Create netlify.toml (see PR #8)
# Create .env.production with API Gateway URL
echo "VITE_API_URL=https://[your-api-gateway-url]/prod" > .env.production

# Link project in Netlify dashboard and set environment variables
# Netlify will auto-deploy on git push
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

