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
    config.py         # Environment variables, settings
  services/
    document_service/  # Document upload/management
    template_service/ # Template CRUD operations
    parser_service/   # PDF text extraction
    ai_service/       # Letter generation orchestration
    letter_service/   # Letter CRUD, finalize, export
  scripts/            # Utility scripts (testing, migrations, etc.)
    test_db.py        # Database connection and schema validation
  main.py             # Local dev: combines all routers
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
- CRUD operations for generated letters
- Generates .docx files from HTML content
- Handles finalize and re-export actions
- Manages letter-document associations
- Uploads .docx exports to S3 (using `shared/s3_client.py`)
- Uses bucket: `goico-demand-letters-exports-dev` (presigned URLs for frontend access)

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
  1. Fetches letter from RDS
  2. Converts HTML content to .docx using python-docx
  3. Uploads .docx to S3
  4. Updates letter record:
     - status = 'created'
     - docx_s3_key = S3 key
  5. Generates presigned download URL
  6. Returns download URL
```

## Design Patterns

### Repository Pattern (Implicit)
- Business logic separated from database access
- Each service has `logic.py` for business rules
- Database models in `shared/models/`

### Dependency Injection
- FastAPI dependency system for database sessions
- Auth dependencies for user verification
- Config singleton for environment variables

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
- All queries filtered by `firm_id` from authenticated user
- No cross-firm data access

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

### Authentication
- JWT tokens stored in localStorage
- Token included in Authorization header
- Token validation on every request
- Automatic redirect to login on 401

### Authorization
- Firm-level access control
- All queries filtered by user's firm_id
- No direct database access from frontend
- API validates user access on every request

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
- Custom exception classes in `shared/exceptions.py`
- Global exception handlers in FastAPI
- Structured error responses
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

### Production
- Each service as separate Lambda function
- API Gateway routes to appropriate Lambda
- RDS for production database
- S3 for document storage
- CloudFront for frontend CDN

### Lambda Deployment
- Serverless Framework for configuration
- Lambda Layers for shared dependencies
- Environment variables for configuration
- Separate deployments per service (or monorepo deployment)

## Key Technical Decisions

1. **HTML Storage:** Letter content stored as HTML in database (source of truth)
2. **On-Demand Parsing:** PDF text extracted when needed, not pre-stored
3. **Status-Based Workflow:** Explicit draft/created status for business logic
4. **Firm-Level Templates:** Templates shared across firm, not per-user
5. **Service Separation:** Clear boundaries but shared codebase for development speed
6. **Environment Configuration:** `.env` files are source of truth for most configuration. OpenAI model, temperature, and max_tokens are hardcoded in `shared/config.py` for easier development iteration.
7. **Scripts Organization:** All utility scripts live in `backend/scripts/` directory
8. **Port Standardization:** Use 5432 for PostgreSQL in all environments (local matches production)

