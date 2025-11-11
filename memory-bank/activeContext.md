# Active Context: Demand Letter Generator

## Current Status

**Phase:** Backend Services Implementation - In Progress  
**Last Updated:** November 2025

The project has completed all foundation PRs (PRs #1-5), PR #6 (Shared Backend Utilities), and PR #7 (Document Service - Backend). Document service is fully implemented with firm-level isolation, S3 integration, and all CRUD operations.

## Current Work Focus

### Immediate Next Steps

**PR #6 Complete** - Shared utilities ready for use:

1. ✅ **PR #6: Shared Backend Utilities** - COMPLETE
   - Configuration management with Pydantic BaseSettings
   - Error handling utilities and exception classes
   - Common schemas (SuccessResponse, ErrorResponse, PaginationParams, PaginatedResponse)
   - Shared exceptions with FastAPI handlers
   - Utility functions (UUID, datetime, file size, filename/HTML sanitization)

2. ✅ **PR #7: Document Service - Backend** - COMPLETE
   - Document schemas with validation (file type, size)
   - Business logic with firm-level isolation
   - Router with firm_id in path: `/{firm_id}/documents`
   - All endpoints: upload, list, get, delete, download URL
   - Lambda handlers using Mangum
   - S3 integration with presigned URLs

3. **PR #8: Template Service - Backend** (Next)
   - Template CRUD operations
   - Firm-level template management
   - Default template logic

## Recent Changes

- ✅ PR #1: Project Initialization - Frontend and backend setup complete
- ✅ PR #2: Docker Configuration - Docker Compose and Dockerfiles created
- ✅ PR #3: Database Schema and Migrations - All models, migrations, and utilities implemented
  - Created all database models (Firm, User, Document, LetterTemplate, GeneratedLetter, LetterSourceDocument)
  - Set up Alembic with proper configuration
  - Created initial migration with all tables and indexes
  - Added database utilities for connection testing and table management
  - Added comprehensive migration documentation to README
- ✅ PR #4: S3 Client and Bucket Setup - Complete
  - Created `shared/s3_client.py` with full S3 operations (upload, download, delete, presigned URLs)
  - Created S3 buckets in AWS: `goico-demand-letters-documents-dev` and `goico-demand-letters-exports-dev` (us-east-2)
  - Configured buckets: versioning enabled, encryption (AES256), public access blocked for documents only
  - Created comprehensive documentation: `docs/s3-bucket-setup.md` and `docs/s3-usage.md`
  - Updated all references to use correct bucket naming convention
- ✅ PR #5: Lambda-Optimized Application Structure - Complete
  - Created `serverless.yml` with full AWS Lambda configuration
  - Created `handlers/` directory with base handler utility and example handlers
  - Added serverless plugins: serverless-offline and serverless-python-requirements
  - Created `backend/package.json` for npm scripts
  - Created comprehensive deployment documentation: `backend/docs/lambda-deployment.md`
  - Hardcoded OpenAI model (gpt-4), temperature (0.7), and max_tokens (2000) in `shared/config.py` for easier development
- ✅ PR #6: Shared Backend Utilities - Complete
  - Updated `shared/config.py` to use Pydantic BaseSettings (from pydantic-settings package)
  - Created Settings class with nested configuration models (Database, AWS, OpenAI, CORS)
  - Added CORS configuration fields (allow_origins, allow_credentials, allow_methods, allow_headers)
  - Created `shared/schemas/` directory with common schemas:
    - SuccessResponse, ErrorResponse, PaginationParams, PaginatedResponse
  - Created `shared/exceptions.py` with custom exception classes:
    - BaseAppException, DocumentNotFoundException, TemplateNotFoundException, LetterNotFoundException
    - S3UploadException, S3DownloadException, OpenAIException
    - ValidationException, UnauthorizedException, ForbiddenException
  - Created FastAPI exception handlers (app_exception_handler, http_exception_handler, validation_exception_handler, general_exception_handler)
  - Added `register_exception_handlers()` function for easy setup
  - Created `shared/utils.py` with utility functions:
    - generate_uuid(), format_datetime(), format_file_size(), sanitize_filename(), sanitize_html(), parse_file_size()
  - Updated all validators to use Pydantic v2 API (field_validator)
  - Added pydantic-settings>=2.1.0 to requirements.txt
- ✅ PR #7: Document Service - Backend - Complete
  - Created `services/document_service/schemas.py` with all document schemas (DocumentBase, DocumentCreate, DocumentResponse, DocumentListResponse, UploadResponse, DownloadUrlResponse)
  - Created `services/document_service/logic.py` with business logic:
    - upload_document(): Validates, uploads to S3, creates DB record
    - get_documents(): Paginated listing with sorting
    - get_document_by_id(): Retrieval with firm-level isolation
    - delete_document(): Deletes from S3 and database
    - generate_download_url(): Presigned URLs (1 hour expiration)
  - Created `services/document_service/router.py` with router prefix `/{firm_id}/documents`:
    - POST /{firm_id}/documents/ - Upload document
    - GET /{firm_id}/documents/ - List documents (pagination & sorting)
    - GET /{firm_id}/documents/{document_id} - Get document by ID
    - DELETE /{firm_id}/documents/{document_id} - Delete document
    - GET /{firm_id}/documents/{document_id}/download - Get download URL
  - Created `services/document_service/handler.py` with Lambda handlers
  - All operations enforce firm-level isolation
  - S3 key pattern: `{firm_id}/{document_id}/{sanitized_filename}`
- Created test script (backend/scripts/test_db.py) for database connection and schema validation

## Active Decisions & Considerations

### Architecture Decisions Made

1. **Service Structure:** Service-oriented Lambda functions with shared code
2. **Local Development:** Single FastAPI app combining all routers
3. **Database:** PostgreSQL 15 with SQLAlchemy ORM
4. **Frontend:** React 18 + Vite + Tailwind + shadcn/ui
5. **Storage:** S3 for files, RDS for metadata

### Pending Decisions

1. **Node.js Version:** Need to confirm Node.js 18+ compatibility with all packages
2. **Lambda Layer Strategy:** Finalize which dependencies go in common layer
3. **Testing Strategy:** Unit test coverage targets and testing frameworks
4. **CI/CD:** Whether to set up automated deployment pipeline

### Recent Decisions

1. **OpenAI Configuration:** Model (gpt-4), temperature (0.7), and max_tokens (2000) are hardcoded in `shared/config.py` for easier development iteration. These can be adjusted directly in code as needed, avoiding environment variable friction during development.

### Current Blockers

None identified yet - project is in initial setup phase.

## Next Milestones

### Phase 1: Foundation ✅ COMPLETE (100% - 6/6 PRs)
- [x] Project initialization
- [x] Docker setup
- [x] Database schema
- [x] AWS infrastructure configuration (S3)
- [x] Lambda-optimized structure setup
- [x] Shared backend utilities

### Phase 2: Core Features (In Progress)
- [x] Document service (upload, list, delete) - PR #7 Complete
- [ ] Template service (CRUD) - PR #8 Next
- [ ] Parser service (PDF extraction) - PR #9
- [ ] Basic UI for documents and templates

### Phase 3: AI Integration
- [ ] AI service (letter generation)
- [ ] OpenAI integration
- [ ] Finalize page UI

### Phase 4: Letter Management
- [ ] Letter service (CRUD, finalize, export)
- [ ] Generated letters library UI
- [ ] Edit functionality
- [ ] .docx export

### Phase 5: Polish & Testing
- [ ] End-to-end testing
- [ ] Bug fixes
- [ ] UI/UX refinements
- [ ] Performance optimization

### Phase 6: Deployment
- [ ] Lambda deployment
- [ ] Production environment setup
- [ ] User acceptance testing
- [ ] Launch

## Development Priorities

### P0 (Must Have)
All features listed in PRD Section 6 (Functional Requirements - P0)

### P1 (Post-MVP)
Features listed in PRD Section 6.7 (P1: Post-MVP Features)

## Key Files to Reference

- **PRD.md:** Complete product requirements
- **architecture.mermaid:** System architecture diagram
- **tasks-1.md:** Setup and infrastructure tasks (PRs #1-5)
- **tasks-2.md:** Backend services tasks (PRs #6-10)
- **tasks-3.md:** AI and letter services (PRs #11-14)
- **tasks-4.md:** Frontend pages (PRs #15-21)
- **tasks-5.md:** Integration, testing, deployment (PRs #22-29)

## Important Notes

1. **MVP Focus:** Only P0 features should be implemented initially
2. **Firm-Level Isolation:** All data must be filtered by firm_id - all users within a firm see the same documents, templates, and letters. All queries filter by firm_id for multi-tenancy. Document service uses firm_id as path parameter: `/{firm_id}/documents`.
3. **No Auth for MVP:** JWT authentication removed from MVP scope. firm_id is provided as path parameter in URL (e.g., `/{firm_id}/documents`).
4. **Error Handling:** Comprehensive error handling at all layers
5. **Documentation:** Keep documentation updated as code is written

## Questions to Resolve

1. ~~Authentication system details (JWT implementation specifics)~~ - Deferred to post-MVP
2. OpenAI API key management (AWS Secrets Manager vs environment variables)
3. Frontend deployment strategy (S3 + CloudFront vs Vercel/Netlify)
4. Database migration strategy (Alembic vs manual SQL)
5. Local S3 testing (LocalStack vs actual S3 bucket)

## Workflow Notes

- Use task lists (tasks-1.md through tasks-5.md) as implementation guide
- Each PR should be focused and complete
- Test locally before deployment
- Update documentation as features are built
- Keep memory bank updated with new patterns and decisions

