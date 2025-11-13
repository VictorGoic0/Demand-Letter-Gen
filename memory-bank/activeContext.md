# Active Context: Demand Letter Generator

## Current Status

**Phase:** Production Deployment (Phase 6)
**Last Updated:** November 13, 2025

The project has completed all 23 PRs from the development phase (foundation through authentication). Backend is deployed to AWS Lambda + API Gateway, frontend is deployed to Netlify. Most endpoints working, but document uploads failing.

## Current Work Focus

### Production Deployment Status

**Backend Deployment:**
- ✅ All Lambda functions deployed to AWS
- ✅ API Gateway configured with HTTPS endpoints
- ✅ RDS PostgreSQL database running and accessible
- ✅ S3 buckets created (documents + exports)
- ✅ CORS fixed for Netlify origin
- ✅ Auth service deployed (/login endpoint)
- ✅ Environment variables configured
- ✅ Document uploads fixed (S3 client now uses IAM role in Lambda)

**Frontend Deployment:**
- ✅ Deployed to Netlify (https://demand-letter-generator.netlify.app)
- ✅ CORS issues resolved
- ✅ Login endpoint working
- ✅ Templates endpoint working (empty state)
- ✅ Letters endpoint working (empty state)
- ✅ Documents endpoint working (list + upload)

### Recent Changes

**Files Modified in Deployment Session:**

1. **backend/serverless.yml**
   - Changed `ENVIRONMENT: ${self:provider.stage}` → `ENVIRONMENT: production` (line 27)
   - Changed `slim: true` → `slim: false` (line 416) to preserve package metadata
   - Replaced all `cors: true` with explicit CORS configuration:
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
   - Added `authService` function for /login endpoint

2. **backend/shared/config.py**
   - Added `extra="ignore"` to `AWSConfig.model_config` (line 54) to allow Lambda's built-in AWS_* environment variables

3. **backend/services/auth_service/schemas.py**
   - Changed `email: EmailStr` → `email: str` to avoid email-validator dependency

4. **backend/requirements.txt**
   - Removed `email-validator>=2.0.0` (causing metadata import errors)

5. **backend/handlers/base.py**
   - Hardcoded Netlify domain in default CORS origins (lines 40-45)
   - Updated error response headers to use Netlify domain instead of `*`

6. **backend/main.py**
   - Added Netlify domain to local dev CORS origins
   - Updated health handler to return Netlify domain in CORS header

7. **backend/handlers/auth_handler.py** (NEW)
   - Created Lambda handler for authentication service

8. **frontend/src/lib/api.ts**
   - Removed `withCredentials: true` (not needed for localStorage-based auth)

9. **backend/services/template_service/router.py**
   - Fixed page_size validation: `page_size=len(templates) if len(templates) > 0 else 1` (line 120)

10. **backend/package.json**
    - Updated all deployment scripts to use `npx serverless` with proper env loading
    - Added `logs:prod`, `logs:function`, `info:prod`, `remove:prod` scripts

11. **backend/shared/s3_client.py**
    - Updated `__init__` method to detect Lambda environment using `AWS_EXECUTION_ENV`
    - Lambda: Initialize boto3 client with only `region_name` (uses IAM role automatically)
    - Local dev: Use explicit credentials from environment variables or parameters
    - Lambda no longer reads or checks `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY`

12. **tasks-deployment.md**
    - Removed PRs 5, 6, 7
    - Added new PR #5 documenting all production deployment fixes
    - Updated PR #5 section 7 to document S3 upload fix

### Issues Fixed During Deployment

1. **Email Validator Dependency Issue**
   - Problem: `Runtime.ImportModuleError: No package metadata was found for email-validator`
   - Root cause: Pydantic's EmailStr requires metadata, serverless-python-requirements with `slim: true` strips it
   - Fix: Removed EmailStr, removed email-validator from requirements, changed slim to false

2. **Environment Variable Validation**
   - Problem A: `ENVIRONMENT: prod` not accepted (expects `production`)
   - Fix: Hardcoded `ENVIRONMENT: production` in serverless.yml
   - Problem B: Lambda's AWS_* env vars rejected by AWSConfig
   - Fix: Added `extra="ignore"` to AWSConfig model

3. **CORS Issues**
   - Problem: Wildcard `*` CORS breaks when credentials included
   - Fix: Removed `withCredentials` from frontend, added explicit Netlify origin in backend

4. **Missing Auth Endpoint**
   - Problem: /login endpoint not deployed
   - Fix: Created auth_handler.py, added authService to serverless.yml

5. **RDS Connection Timeout**
   - Problem: Lambda couldn't connect to RDS
   - Fix: Updated RDS security group to allow connections from 0.0.0.0/0 on port 5432

6. **Template List Empty State**
   - Problem: GET /templates returns 500 when no templates exist
   - Fix: Set page_size to 1 minimum (was 0 for empty results)

7. **S3 Upload Failures** ✅ FIXED
   - Problem: Document uploads failing with `InvalidAccessKeyId` error
   - Root Cause: S3 client was checking for AWS credentials from environment variables even when running in Lambda. Lambda execution role provides S3 access automatically via IAM, but the code was still trying to read `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from environment.
   - Fix: Updated `backend/shared/s3_client.py` to detect Lambda environment using `AWS_EXECUTION_ENV` environment variable. When in Lambda, initialize boto3 client with only `region_name` (no credentials) - uses IAM role automatically. When in local dev, use explicit credentials from environment variables.
   - Status: ✅ Fixed - S3 uploads now work in Lambda using IAM role

## Deployment Architecture

### Backend (AWS)
- **Compute:** AWS Lambda (Python 3.11)
- **API:** API Gateway (HTTPS)
- **Database:** RDS PostgreSQL (db.t3.micro, single-AZ)
- **Storage:** S3 (2 buckets: documents + exports)
- **Region:** us-east-2

**Lambda Functions:**
- `healthCheck` - GET /health
- `authService` - POST /login
- `documentService` - All /documents endpoints
- `templateService` - All /templates endpoints
- `letterService` - All /letters endpoints
- `parserService` - All /parse endpoints
- `aiService` - POST /generate/letter

**Environment Variables (Production):**
- `ENVIRONMENT=production`
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `AWS_S3_BUCKET_DOCUMENTS`, `AWS_S3_BUCKET_EXPORTS`
- `OPENAI_API_KEY`
- Note: S3 access uses Lambda execution role (IAM) - no explicit credentials needed

### Frontend (Netlify)
- **URL:** https://demand-letter-generator.netlify.app
- **Build:** Vite + React
- **Auth:** localStorage-based (email, userId, firmId, role)
- **API:** Axios client with firmId/userId headers

## Deployment Commands

**Backend:**
```bash
cd backend
npm run deploy:prod         # Deploy all functions
npm run logs:prod           # View all logs
npm run logs:function       # View specific function logs
npm run remove:prod         # Remove deployment
npm run info:prod           # Get deployment info
```

**Frontend:**
- Auto-deployed via Netlify on git push to main

## Key Learnings from Deployment

1. **Pydantic Validation:** Too strict for MVP - caused crashes on edge cases (EmailStr, page_size >= 1, extra="forbid")

2. **CORS with Credentials:** Wildcard `*` doesn't work with `withCredentials: true` - always use explicit origins

3. **Dev/Prod Parity:** Environment name mismatches and Lambda-specific env vars caused issues that didn't appear locally

4. **Serverless Framework:**
   - `cors: true` defaults to wildcard `*`
   - Must use `npx serverless` for consistent versions
   - Environment variables must be loaded before deployment commands

5. **AWS Lambda:** Should use execution role for AWS service access, not explicit credentials in environment
   - S3 client must detect Lambda environment and skip credential checks
   - Use `AWS_EXECUTION_ENV` environment variable to detect Lambda
   - Initialize boto3 client with only `region_name` in Lambda - IAM role provides credentials automatically

## Next Steps

1. ✅ **Fix S3 upload issue** - Fixed: S3 client now uses IAM role in Lambda
2. **Test end-to-end flow** - upload documents, create template, generate letter
3. **Document production setup** - create runbook for operations
4. **Monitor costs** - verify staying within budget (~$15-30/month)

## Questions to Resolve

1. ~~Authentication system details~~ - Deferred to post-MVP
2. ~~OpenAI API key management~~ - Using environment variables for MVP
3. ~~Frontend deployment strategy~~ - Using Netlify ✅
4. ~~Database migration strategy~~ - Using Alembic ✅
5. ~~Local S3 testing~~ - Using actual S3 buckets ✅
6. ~~S3 uploads failing with InvalidAccessKeyId~~ - Fixed: S3 client now uses IAM role in Lambda ✅

## Workflow Notes

- Use task lists and tasks-deployment.md as implementation guide
- Each PR should be focused and complete
- Test locally before deployment
- Update documentation as features are built
- Keep memory bank updated with new patterns and decisions
- For deployment issues: check Lambda logs first (CloudWatch)
- Use `npx serverless logs --function <functionName> --stage prod` to view logs

