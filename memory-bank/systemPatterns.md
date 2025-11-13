# System Patterns: Demand Letter Generator

## Architecture Overview

**Pattern:** Service-oriented Lambda functions with shared dependencies

The system uses a hybrid approach:
- **Local Development:** Single FastAPI application with all service routers combined
- **Production:** Each service deployed as separate Lambda function with API Gateway

This provides clean separation of concerns without full microservices complexity.

## Service Architecture

### Service Breakdown

```
backend/
  shared/              # Common code and dependencies
    database.py        # SQLAlchemy models, session management
    auth.py           # Authentication middleware
    s3_client.py      # S3 operations wrapper (upload, download, delete, presigned URLs)
    config.py         # Environment variables, settings (Pydantic BaseSettings)
    exceptions.py     # Custom exception classes and FastAPI handlers
    utils.py          # Utility functions (UUID, datetime, file size, sanitization)
    schemas/          # Common Pydantic schemas
      common.py       # SuccessResponse, ErrorResponse, PaginationParams, PaginatedResponse
  services/
    document_service/  # Document upload/management
    template_service/ # Template CRUD operations
    parser_service/   # PDF text extraction
    ai_service/       # Letter generation orchestration
    letter_service/   # Letter CRUD, finalize, export
  scripts/            # Utility scripts (testing, check scripts)
    check_*.py        # Table check scripts (firm, user, document, template, letter, letter_document)
    seed_*.py         # Seed scripts (test_firm, test_users)
    test_*.py         # Test scripts (db_connection, upload_document_api)
  migration_scripts/ # Alembic migration scripts
    migrate-up.sh     # Upgrade to latest migration
    migrate-down.sh   # Rollback one migration
    migrate-create.sh # Create new migration
  package.json        # npm scripts (start, restart, end, serverless commands)
  main.py             # Local dev: combines all routers with health checks
```

### Service Responsibilities

**Document Service**
- Handles file uploads to S3 (using `shared/s3_client.py`)
- Manages document metadata in database
- Provides document listing, retrieval, deletion
- Generates presigned download URLs (1 hour expiration)
- Uses bucket: `goico-demand-letters-documents-dev`

**Template Service**
- CRUD operations for letter templates
- Manages firm-level template sharing
- Handles default template logic

**Parser Service**
- Extracts text from PDFs on-demand
- Called internally by AI service (not directly by frontend)
- Handles multi-page PDFs, encrypted PDFs

**AI Service**
- Orchestrates letter generation workflow
- Calls parser service for document text extraction
- Fetches template from database
- Sends context to OpenAI API
- Saves generated letter to database

**Letter Service**
- CRUD operations for generated letters (PR #12 Complete)
  - List letters with pagination and sorting (created_at, updated_at, title, status)
  - Get single letter with full metadata and presigned URL
  - Update letter title and/or content
  - Delete letter and associated .docx from S3
- DOCX generation from HTML content (PR #13 Complete)
  - Custom HTML parser (`HTMLToDocxParser`) supporting common tags (p, h1-h3, strong, b, em, i, ul, ol, li)
  - Handles nested formatting with stack-based approach
  - Converts HTML to python-docx Document objects
  - Filename generation with sanitization (50 char limit, format: `Demand_Letter_[Title]_[Date].docx`)
- Finalize and export actions (PR #13 Complete)
  - `finalize_letter()`: Generates DOCX, updates status to 'created', uploads to S3
  - `export_letter()`: Returns existing presigned URL or generates new DOCX
  - Works on letters with status 'draft' OR 'created' (allows re-finalizing)
  - S3 key format: `{firmId}/letters/{filename}.docx`
  - Cleans up old files when filenames change
- Manages letter-document associations (via LetterSourceDocument junction table)
- Uploads .docx exports to S3 (using `shared/s3_client.py`)
- Uses bucket: `goico-demand-letters-exports-dev` (presigned URLs for frontend access)
- Router prefix: `/{firm_id}/letters`
- All operations enforce firm-level isolation

## Data Flow Patterns

### Letter Generation Flow

```
Frontend → API Gateway → AI Service Lambda
  ↓
AI Service:
  1. Validates request (template, documents)
  2. Fetches template from RDS
  3. Fetches document metadata from RDS
  4. Calls Parser Service for each document
     ↓
     Parser Service:
     - Downloads PDF from S3
     - Extracts text using pypdf
     - Returns extracted text
  5. Builds prompt with template + document text
  6. Calls OpenAI API
  7. Receives generated HTML
  8. Saves letter to RDS (status='draft')
  9. Creates letter-document associations
  10. Returns letter ID and content
  ↓
Frontend redirects to Finalize page
```

### Document Upload Flow

```
Frontend → API Gateway → Document Service Lambda
  ↓
Document Service:
  1. Validates file (type, size)
  2. Generates unique S3 key
  3. Uploads file to S3
  4. Creates document record in RDS
  5. Returns document metadata
```

### Finalization Flow

```
Frontend → API Gateway → Letter Service Lambda
  ↓
Letter Service:
  1. Fetches letter from RDS (verifies firm-level access)
  2. Generates filename from title and date (sanitized, 50 char limit)
  3. Converts HTML content to .docx using custom HTML parser:
     - Parses HTML tags (p, h1-h3, strong, b, em, i, ul, ol, li)
     - Handles nested formatting (bold + italic)
     - Creates python-docx Document with proper styling
  4. Uploads .docx to S3 (key: {firmId}/letters/{filename}.docx)
  5. Cleans up old file if filename changed
  6. Updates letter record:
     - status = 'created'
     - docx_s3_key = new S3 key
  7. Generates presigned download URL (1 hour expiration)
  8. Returns letter data with download URL
```

### Export Flow (Re-export)

```
Frontend → API Gateway → Letter Service Lambda
  ↓
Letter Service:
  1. Fetches letter from RDS (verifies firm-level access)
  2. Always regenerates DOCX from current letter.content:
     - Stores old S3 key for cleanup
     - Generates filename from title and updated_at date
     - Cleans content: removes ```html at start, ``` at end, stray backticks
     - Converts cleaned HTML to .docx using custom parser
     - Uploads new .docx to S3 (key: {firmId}/letters/{filename}.docx)
     - Updates docx_s3_key in database
     - Cleans up old file from S3 if filename changed
     - Generates presigned URL (1 hour expiration)
     - Returns new presigned URL
  3. Database always updated with new docx_s3_key
  4. Old files automatically cleaned up when filename changes
```

**Note:** Re-export always regenerates to ensure DOCX reflects latest content changes. Download uses existing presigned URLs from list view (only for finalized letters).

## Design Patterns

### Repository Pattern (Implicit)
- Business logic separated from database access
- Each service has `logic.py` for business rules
- Database models in `shared/models/`

### Dependency Injection
- FastAPI dependency system for database sessions
- Auth dependencies for user verification
- Config singleton pattern via `get_settings()` function
- Settings class with nested BaseSettings models (Database, AWS, OpenAI, CORS)

### Service Layer Pattern
- Each service has clear boundaries
- Services communicate via API calls (in production) or direct imports (in local dev)
- Shared utilities in `shared/` directory

### Lambda Layer Strategy
- **Common Layer:** Heavy, stable dependencies (fastapi, sqlalchemy, boto3, pydantic)
- **Service-Specific:** Each Lambda includes only its service code + service-specific deps
- Benefits: Smaller bundles, faster deployments, shared dependencies

## Database Patterns

### Multi-Tenancy
- Firm-level isolation via `firm_id` foreign keys
- All queries MUST filter by `firm_id` - all users within a firm see the same documents, templates, and letters
- No cross-firm data access
- For MVP: `firm_id` provided via query parameter or header (authentication removed from MVP scope)
- All create operations must include `firm_id` in database records
- All read/update/delete operations must verify `firm_id` matches before proceeding

### Soft Relationships
- Letter-source document relationship via junction table
- Cascade deletes for data integrity
- Indexes on foreign keys and common query fields

### Status Management
- Letters have explicit status: 'draft' or 'created'
- Status transitions: draft → created (via finalize)
- Status used for UI display and business logic

## Frontend Patterns

### Component Hierarchy

```
App
  └── MainLayout
       ├── Navigation
       └── Router
            ├── DocumentLibrary
            │    ├── DocumentUpload
            │    └── DocumentList
            ├── TemplateManagement
            │    ├── TemplateForm
            │    └── TemplateList
            ├── CreateLetter
            │    ├── TemplateSelector
            │    └── DocumentSelector
            ├── FinalizeLetter
            │    ├── LetterViewer
            │    └── LetterEditor
            └── GeneratedLetters
                 └── LetterList
```

### State Management
- React hooks for API calls (`useDocuments`, `useTemplates`, etc.)
- Context API for authentication state
- Local component state for UI interactions
- No global state management library (Redux/Zustand) needed for MVP

### API Integration Pattern
- Centralized axios instance in `lib/api.ts`
- Custom hooks for each resource type
- Consistent error handling via interceptors
- Loading states managed in hooks

## Security Patterns

### Authentication (MVP: Removed)
- JWT authentication removed from MVP scope
- For MVP: `firm_id` provided via query parameter or header
- Future: Will implement JWT-based authentication with user sessions

### Authorization
- Firm-level access control enforced
- All queries filtered by `firm_id` (provided in request)
- No direct database access from frontend
- API validates `firm_id` matches on every request before returning/updating data

### Data Protection
- S3 bucket encryption at rest (AES256) - Both buckets encrypted
- S3 versioning enabled - Both buckets have versioning
- Documents bucket: Public access blocked (security)
- Exports bucket: Public access allowed (for presigned URL downloads)
- HTTPS for all API communication
- Presigned URLs with expiration (1 hour default) for downloads
- No sensitive data in frontend code

## Error Handling Patterns

### Backend
- Custom exception classes in `shared/exceptions.py`:
  - BaseAppException (base class with status_code, message, detail, code)
  - Resource-specific exceptions (DocumentNotFoundException, TemplateNotFoundException, LetterNotFoundException)
  - Service-specific exceptions (S3UploadException, S3DownloadException, OpenAIException)
  - HTTP exceptions (ValidationException, UnauthorizedException, ForbiddenException)
- Global exception handlers in FastAPI:
  - `app_exception_handler` for custom application exceptions
  - `http_exception_handler` for HTTP exceptions
  - `validation_exception_handler` for request validation errors
  - `general_exception_handler` for unhandled exceptions
- `register_exception_handlers(app)` function to register all handlers at once
- Structured error responses using ErrorResponse schema
- Logging to CloudWatch

### Frontend
- Error boundary for React errors
- Toast notifications for API errors
- Retry logic for transient failures
- User-friendly error messages

## Deployment Patterns

### Local Development
- Docker Compose for full stack
- Hot reload for both frontend and backend
- Local PostgreSQL database
- Direct service imports (no API calls between services)
- Docker management via npm scripts: `npm run start`, `npm run end`, `npm run restart`
- Migration scripts: `migration_scripts/migrate-up.sh`, `migrate-down.sh`, `migrate-create.sh`
- Check scripts: `scripts/check_*.py` for all database tables (first 5 results)
- Main application with startup/shutdown events and detailed health checks

### Production (AWS Lambda + Netlify)

**Backend Stack:**
- AWS Lambda (Python 3.11) - Each service as separate function
- API Gateway (HTTP API) - HTTPS endpoints with explicit CORS
- RDS PostgreSQL (db.t3.micro, single-AZ) - Production database
- S3 (2 buckets) - Document storage and exports
- CloudWatch - Logs and monitoring (7-day retention)
- Region: us-east-2
- No VPC (Lambda has default internet access for OpenAI API)

**Frontend Stack:**
- Netlify - Static hosting with auto-deploy from git
- Vite + React - Optimized production builds
- URL: https://demand-letter-generator.netlify.app

### Lambda Deployment (Serverless Framework)

**Configuration (serverless.yml):**
- Monorepo deployment (all functions in one stack)
- Lambda Layers for Python dependencies (via serverless-python-requirements plugin)
- Environment variables loaded from `.env.production` during deployment
- IAM roles for S3 access and CloudWatch logs
- Explicit CORS configuration (no wildcards)

**Critical Settings:**
- `ENVIRONMENT: production` (hardcoded, not `${self:provider.stage}`)
- `slim: false` (preserves package metadata for Pydantic runtime checks)
- `dockerizePip: true` (build dependencies in Docker for Lambda compatibility)
- Explicit CORS origins: `https://demand-letter-generator.netlify.app`

**Deployment Commands:**
```bash
npm run deploy:prod         # Deploy all functions (uses npx serverless)
npm run logs:prod           # View all CloudWatch logs
npm run logs:function       # View specific function logs
npm run remove:prod         # Remove entire stack
npm run info:prod           # Get deployment info
```

**Lambda Functions:**
- `healthCheck` - GET /health
- `authService` - POST /login
- `documentService` - All /documents endpoints
- `templateService` - All /templates endpoints
- `letterService` - All /letters endpoints
- `parserService` - All /parse endpoints
- `aiService` - POST /generate/letter

### Production CORS Configuration

**Problem Solved:** Wildcard `*` CORS doesn't work when credentials mode is `include`

**Solution:**
1. **serverless.yml** - Every HTTP event has explicit CORS:
   ```yaml
   cors:
     origin: https://demand-letter-generator.netlify.app
     headers: [Content-Type, Authorization, X-Firm-Id, X-User-Id]
     allowCredentials: false
   ```
2. **handlers/base.py** - Hardcoded Netlify domain in default CORS origins
3. **main.py** - Health handler returns Netlify domain in CORS header
4. **frontend/api.ts** - No `withCredentials` (uses localStorage, not cookies)

### Environment Variables (Production Lambda)

**Required in .env.production:**
- `ENVIRONMENT=production` (must match config.py validation)
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (RDS credentials)
- `AWS_S3_BUCKET_DOCUMENTS`, `AWS_S3_BUCKET_EXPORTS` (S3 bucket names)
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (for S3 client)
- `OPENAI_API_KEY` (OpenAI API access)

**Note:** Lambda automatically sets many `AWS_*` environment variables. The `AWSConfig` class uses `extra="ignore"` to prevent Pydantic validation errors from these extra variables.

## Key Technical Decisions

1. **HTML Storage:** Letter content stored as HTML in database (source of truth)
2. **On-Demand Parsing:** PDF text extracted when needed, not pre-stored
3. **Status-Based Workflow:** Explicit draft/created status for business logic
4. **Firm-Level Templates:** Templates shared across firm, not per-user
5. **Service Separation:** Clear boundaries but shared codebase for development speed
6. **Environment Configuration:** `.env` files are source of truth for most configuration. OpenAI model and temperature are in `shared/config.py` for easier development iteration.
7. **Scripts Organization:** 
   - Utility scripts in `backend/scripts/` directory (check, seed, test scripts)
   - Migration scripts in `backend/migration_scripts/` directory (alembic commands)
   - Docker management via npm scripts in `package.json` (npm run start, end, restart)
8. **Port Standardization:** Use 5432 for PostgreSQL in all environments (local matches production)
9. **HTML to DOCX Conversion:** Custom HTML parser built using Python's `html.parser` module, converting to python-docx Document objects. Supports common tags with nested formatting support. Filename generation with sanitization (50 char limit).
10. **DOCX Export Strategy:** S3 key format `{firmId}/letters/{filename}.docx` (no letter_id in path). Old files cleaned up when filenames change. Finalize always generates new DOCX (overwrites existing). Re-export always regenerates DOCX from current content (ensures latest changes are reflected). List view returns presigned URLs (docx_url) for finalized letters. Download button only visible for finalized letters with docx_url.
11. **Content Cleaning (Export Only):** Markdown code block markers (```html at start, ``` at end) and stray backticks are removed during DOCX conversion. Cleaning happens in html_to_docx function before HTML parsing. Valid HTML formatting tags (p, h1-h3, strong, em, ul, ol, li) are preserved. Database content remains unchanged - cleaning only affects exports.
12. **Health Checks:** Main application performs detailed health checks on startup (database connection test, S3 bucket accessibility). Enhanced `/health` endpoint returns database and S3 connection status for monitoring.
13. **Startup/Shutdown Events:** FastAPI lifespan context manager handles startup (health checks) and shutdown (connection cleanup) events.

