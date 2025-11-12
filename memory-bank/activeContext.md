# Active Context: Demand Letter Generator

## Current Status

**Phase:** Backend Services Implementation  
**Last Updated:** November 2025

The project has completed all foundation PRs (PRs #1-5), PR #6 (Shared Backend Utilities), PR #7 (Document Service - Backend), PR #8 (Template Service - Backend), PR #9 (Parser Service - Backend), PR #10 (AI Service - Backend Part 1: OpenAI Integration), PR #11 (AI Service - Backend Part 2: Generation Logic), PR #12 (Letter Service - Backend Part 1: CRUD Operations), PR #13 (Letter Service - Backend Part 2: DOCX Export), PR #14 (Local Development Main Application), PR #15 (Frontend Foundation and Routing), PR #16 (Document Library Page), and PR #23 (Authentication Flow - Frontend and Backend). Parser service is complete with PDF text extraction and metadata extraction. AI service is complete with OpenAI integration, prompt engineering, and full letter generation logic that creates draft letters from templates and documents. Letter service is complete with CRUD operations and DOCX export functionality (HTML to DOCX conversion, finalize, and export endpoints). Main FastAPI application is complete with all service routers integrated, detailed health checks, and startup/shutdown events. Frontend authentication is complete with login page, protected routes, and auth context. Backend login endpoint is implemented with mock authentication.

## Current Work Focus

### Immediate Next Steps

**PR #16 Complete** - Document Library Page ready for testing:

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
   - Testing scripts: seed_test_firm.py, seed_test_users.py, check_firm_table.py, check_users_table.py, test_document_api.py
   - Fixed Docker Compose environment variable loading
   - Fixed Pydantic Settings validation for nested configs (extra="ignore" + custom AWSConfig env source)
   - Added database CheckConstraints for User.role and GeneratedLetter.status

3. ✅ **PR #15: Frontend Foundation and Routing** - COMPLETE
   - App.jsx with React Router and all routes (/dashboard, /upload-assets, /templates, /create-letter, /letters, etc.)
   - MainLayout with header, navigation, and main content area
   - Navigation component with underline active states (modern design)
   - All shadcn/ui components installed (button, input, card, dialog, checkbox, switch, select, textarea, badge, table)
   - API client (axios) with interceptors and error handling
   - Type definitions (Document, Template, Letter, API types)
   - AuthContext with user state management
   - Utility files (utils.js, api.ts, constants.ts)
   - Neutral theme with primary color matching shadcn default
   - All placeholder pages created (Dashboard, Documents, Templates, CreateLetter, Letters, FinalizeLetter, EditLetter, NotFound)

4. ✅ **PR #16: Document Library Page - Frontend** - COMPLETE
   - Document listing UI with table view and sorting
   - Multi-file upload with drag-and-drop (always visible, no modal)
   - Auto-upload on file selection
   - Parallel uploads with individual progress tracking
   - Document management (download, delete with confirmation)
   - Empty states and error handling
   - All hooks implemented (useDocuments, useDocumentUpload, useDocumentDelete, useDocumentDownload)

## Recent Changes

- ✅ PR #14: Local Development Main Application - Complete
  - Updated `backend/main.py` with FastAPI lifespan events:
    - Startup: Detailed database connection health check (tests with `SELECT 1`)
    - Startup: Detailed S3 bucket health checks (checks both documents and exports buckets)
    - Shutdown: Proper database connection cleanup (engine.dispose())
    - Enhanced `/health` endpoint with detailed status (database and S3 connection states)
  - Added Docker management scripts to `package.json`:
    - `npm run start` - Start docker-compose services
    - `npm run end` - Stop docker-compose services
    - `npm run restart` - Restart docker-compose services
  - Created migration scripts in `/backend/migration_scripts/`:
    - `migrate-up.sh` - Run `alembic upgrade head`
    - `migrate-down.sh` - Run `alembic downgrade -1`
    - `migrate-create.sh` - Create new migration with `alembic revision --autogenerate`
  - Created check scripts for all database tables:
    - `scripts/check_letter_table.py` - Check generated_letters table (first 5 results)
    - `scripts/check_letter_document_table.py` - Check letter_source_documents table (first 5 results)
  - All service routers already integrated in main.py
  - CORS middleware configured with development origins
  - Exception handlers registered
  - OpenAPI documentation configured
  - Testing setup deferred to MVP+ (optional)

- ✅ PR #13: Letter Service - Backend (Part 2: DOCX Export) - Complete
  - Created `services/letter_service/docx_generator.py` with HTML to DOCX conversion:
    - Custom HTML parser (`HTMLToDocxParser`) supporting `<p>`, `<h1>`, `<h2>`, `<h3>`, `<strong>`, `<b>`, `<em>`, `<i>`, `<ul>`, `<ol>`, `<li>`
    - Handles nested formatting (bold + italic)
    - `html_to_docx()` function for conversion
    - `generate_filename()` with sanitization (50 char limit, format: `Demand_Letter_[Title]_[Date].docx`)
    - `save_docx_to_s3()` for uploading DOCX files to S3
    - Error handling for HTML parsing, DOCX generation, and S3 upload
  - Added `finalize_letter()` function to `logic.py`:
    - Works on letters with status 'draft' OR 'created' (allows re-finalizing)
    - Always generates new DOCX (overwrites existing if present)
    - Changes status to 'created' if not already
    - Generates filename and uploads to S3 (key format: `{firmId}/letters/{filename}.docx`)
    - Cleans up old file if filename changes
    - Returns letter with presigned download URL
  - Added `export_letter()` function to `logic.py`:
    - Returns existing presigned URL if docx_s3_key exists
    - Generates new DOCX if no docx_s3_key exists
    - Updates docx_s3_key if filename changes
    - Cleans up old file if filename changes
    - Returns presigned download URL
  - Added endpoints to `router.py`:
    - POST /{firm_id}/letters/{letter_id}/finalize - Finalize letter
    - POST /{firm_id}/letters/{letter_id}/export - Export letter
    - OpenAPI documentation included
  - Created `services/letter_service/handler.py` with Lambda handlers for all endpoints
  - All error handling implemented throughout

- ✅ PR #12: Letter Service - Backend (Part 1: CRUD Operations) - Complete
  - Created `services/letter_service/schemas.py` with all letter schemas:
    - LetterBase, LetterResponse, LetterListResponse, LetterUpdate
    - DocumentMetadata for source document info
    - FinalizeResponse and ExportResponse (for PR #13)
  - Created `services/letter_service/logic.py` with CRUD operations:
    - `get_letters()` - Paginated listing with sorting (created_at, updated_at, title, status)
    - `get_letter_by_id()` - Single letter retrieval with presigned URL generation
    - `update_letter()` - Update title and/or content
    - `delete_letter()` - Delete letter and associated .docx from S3
    - All operations enforce firm-level isolation
    - Eager loading for template and source documents
    - Comprehensive error handling and logging
  - Created `services/letter_service/router.py`:
    - GET /{firm_id}/letters/ - List letters with pagination and sorting
    - GET /{firm_id}/letters/{letter_id} - Get single letter
    - PUT /{firm_id}/letters/{letter_id} - Update letter
    - DELETE /{firm_id}/letters/{letter_id} - Delete letter
    - OpenAPI documentation included
  - Created `services/letter_service/__init__.py` to export router
  - Router follows same patterns as document_service for consistency
  - Ready for integration into main FastAPI application

- ✅ PR #11: AI Service - Backend (Part 2: Generation Logic) - Complete
  - Created `services/ai_service/logic.py` with `generate_letter()` function:
    - Validates document count (1-5 documents)
    - Fetches and verifies template with firm-level isolation
    - Fetches and verifies all documents with firm-level isolation
    - Calls parser service to extract text from each document
    - Validates extracted text is not empty
    - Builds prompt using template and document context
    - Calls OpenAI API to generate letter content
    - Validates and sanitizes HTML output
    - Creates GeneratedLetter record in database with status='draft'
    - Creates LetterSourceDocument associations for all source documents
    - Returns GenerateResponse with letter_id, content, and status
    - Comprehensive error handling for all failure points
    - Logging for generation requests, successes, and failures
  - Created `services/ai_service/router.py`:
    - POST /generate/letter endpoint
    - Accepts firm_id and optional created_by as query params (MVP approach)
    - Validates GenerateRequest schema
    - Returns 201 with GenerateResponse
    - OpenAPI documentation included
    - Proper error handling with appropriate HTTP status codes
  - Created `services/ai_service/handler.py`:
    - FastAPI app setup for Lambda deployment
    - Mangum handler configured
    - Exception handlers registered
    - Ready for 60-second timeout configuration in Lambda
  - Router exported in `__init__.py` and registered in `main.py`
  - Full integration with parser service and template service
  - Testing utilities deferred for MVP (optional)

- ✅ PR #10: AI Service - Backend (Part 1: OpenAI Integration) - Complete
  - Created `services/ai_service/openai_client.py` with OpenAI client:
    - Singleton client with API key from config
    - `build_generation_prompt()` - builds structured prompts (delegates to prompts.py)
    - `call_openai_api()` - calls OpenAI with temperature from config (0.7), no streaming
    - Retry logic with exponential backoff for rate limits and transient failures
    - Error handling for API errors with OpenAIException
    - `estimate_token_count()` - rough token estimation for logging
    - `validate_response_format()` - validates HTML output
  - Created `services/ai_service/prompts.py` with prompt engineering:
    - Comprehensive BASE_SYSTEM_PROMPT for legal writing (structured process, guidelines, do's/don'ts)
    - `build_context_from_documents()` - formats document text with labels, separators, optional truncation
    - `build_template_instructions()` - formats template structure (letterhead, sections, opening/closing)
    - `build_output_format_instructions()` - HTML formatting requirements
    - `combine_prompt_components()` - combines all components into OpenAI message list
    - `get_html_formatting_examples()` - example HTML structure
  - Created `services/ai_service/schemas.py`:
    - GenerateRequest - template_id, document_ids (max 5), optional title
    - GenerateResponse - letter_id, content (HTML), status (draft)
    - Validation for document count (1-5 documents)
  - System prompt expanded from "too vague" to "just right" with clear structure, process steps, guidelines, and explicit do's/don'ts

- ✅ PR #9: Parser Service - Backend - Complete
  - Created `services/parser_service/pdf_parser.py` with PDF parsing:
    - `extract_text_from_pdf()` - extracts text from all pages with separators
    - `extract_metadata_from_pdf()` - extracts page count, file size, creation date
    - `validate_pdf_structure()` - validates PDF format and structure
    - Error handling for corrupted PDFs, encrypted PDFs, unsupported versions
  - Created `services/parser_service/schemas.py`:
    - ParseRequest - document_ids (max 10)
    - ParseResponse - document_id, extracted_text, page_count, file_size, metadata, success, error
    - ParseBatchResponse - results list with total/successful/failed counts
  - Created `services/parser_service/logic.py`:
    - `parse_document()` - downloads from S3, extracts text, returns ParseResponse
    - `parse_documents_batch()` - processes multiple documents, collects results
    - Firm-level isolation enforced
    - Error handling for S3 download and parsing failures
  - Created `services/parser_service/router.py`:
    - POST /parse/document/{document_id} - parse single document (firm_id query param)
    - POST /parse/batch - parse multiple documents (firm_id query param)
    - Firm-level isolation enforced on all endpoints
  - Created `services/parser_service/handler.py` with Lambda handlers
  - Router registered in main.py for local development

- ✅ PR #8: Template Service - Backend - Complete
  - Created `services/template_service/schemas.py` with all template schemas (TemplateBase, TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse)
  - Created `services/template_service/logic.py` with business logic:
    - create_template(): Validates, handles default flag logic, creates DB record
    - get_templates(): Lists templates with sorting (name, created_at)
    - get_template_by_id(): Retrieval with firm-level isolation
    - update_template(): Updates with default flag handling
    - delete_template(): Deletes with usage check (prevents deletion if in use by letters)
    - get_default_template(): Retrieves default template for firm
  - Created `services/template_service/router.py` with router prefix `/{firm_id}/templates`:
    - POST /{firm_id}/templates/ - Create template
    - GET /{firm_id}/templates/ - List templates (with sorting)
    - GET /{firm_id}/templates/default - Get default template
    - GET /{firm_id}/templates/{template_id} - Get template by ID
    - PUT /{firm_id}/templates/{template_id} - Update template
    - DELETE /{firm_id}/templates/{template_id} - Delete template
  - Created `services/template_service/handler.py` with Lambda handlers
  - All operations enforce firm-level isolation
  - Router registered in main.py for local development
  - Validation for template name length (1-255 chars) and section names (non-empty)
  - Default template logic: setting is_default=True unsets other defaults for the firm

- ✅ PR #23: Authentication Flow - Frontend and Backend - Complete
  - Created Login page with email and password fields
  - Implemented AuthContext with localStorage persistence and validation
  - Created ProtectedRoute component to guard routes
  - Updated App.jsx to protect all routes except /login
  - Created auth service with /login endpoint
  - Backend login endpoint queries User by email and returns user/firm info + role
  - Mock authentication (password accepted but not validated)
  - Added NotFoundException to shared exceptions
  - All routes protected - unauthenticated users redirected to login
  - User dropdown menu with email, role, and logout functionality
  - Logo clickable to navigate to dashboard
  - Firm name displayed in header
  - Axios interceptors add firmId/userId headers to all requests
  - Fixed useDocuments hooks to use firmId (camelCase) instead of firm_id
  - User data persists across page reloads via localStorage

- ✅ PR #15: Frontend Foundation and Routing - Complete
  - Created App.jsx with React Router and all route definitions
  - Routes: /dashboard, /upload-assets, /templates, /create-letter, /letters, /letters/:id/finalize, /letters/:id/edit
  - Created MainLayout.jsx with header (logo, navigation, user profile)
  - Created Navigation.jsx with horizontal nav and underline active states
  - Installed all shadcn/ui components (10 components total)
  - Created API client (lib/api.ts) with axios, interceptors, and error handling
  - Created constants file (lib/constants.ts) with API endpoints, file limits, supported types
  - Created TypeScript type definitions (types/document.ts, types/template.ts, types/letter.ts, types/api.ts)
  - Created AuthContext.jsx with user state, login/logout functions, and useAuth hook
  - Created all placeholder pages (Dashboard, Documents, Templates, CreateLetter, Letters, FinalizeLetter, EditLetter, NotFound)
  - Configured neutral theme with primary color (24 9.8% 10%) matching shadcn default
  - Navigation uses underline style for active items (modern look)
  - Build passes successfully

- ✅ PR #16: Document Library Page - Frontend - Complete
  - Created useDocuments hook (useDocuments, useDocumentUpload, useDocumentDelete, useDocumentDownload)
  - Created DocumentUpload component with modern drag-and-drop UI
    - Always visible at top of page (no modal)
    - Auto-upload on file selection
    - Multi-file support with parallel uploads
    - Individual progress tracking per file
    - File validation (PDF only, 50MB max)
    - Progress cards showing upload status
  - Created DocumentList component with table view
    - Sortable columns (filename, upload date)
    - Download and delete actions
    - Delete confirmation dialog
    - Empty state
    - Loading skeletons
  - Created DocumentCard component (alternative card view)
  - Updated Documents page to integrate all components
  - Navigation updated: "My Campaigns" → "My Letters"
  - Error handling and loading states throughout

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
  - OpenAI model (gpt-4) and temperature (0.7) in `shared/config.py` for easier development
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
  - Created testing scripts:
    - `scripts/seed_test_firm.py` - Standalone script to seed test firm
    - `scripts/seed_test_users.py` - Standalone script to seed test users (6 users)
    - `scripts/check_firm_table.py` - Query and display firms
    - `scripts/check_users_table.py` - Query and display users
    - `scripts/test_document_api.py` - Test document upload endpoint only
  - Fixed Docker Compose environment variable loading (removed env_file, use environment section with ${VAR} syntax)
  - Fixed Pydantic Settings validation for nested configs (added extra="ignore" to Settings.model_config, implemented custom env source for AWSConfig to map AWS_S3_BUCKET_* variables)
  - Added database CheckConstraints:
    - User.role: only 'attorney' or 'paralegal'
    - GeneratedLetter.status: only 'draft' or 'created'
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

1. **OpenAI Configuration:** Model (gpt-4) and temperature (0.7) are in `shared/config.py` for easier development iteration. These can be adjusted directly in code as needed, avoiding environment variable friction during development.

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

### Phase 2: Core Features (100% - 7/7 PRs Complete)
- [x] Document service (upload, list, delete) - PR #7 Complete
- [x] Template service (CRUD) - PR #8 Complete
- [x] Parser service (PDF extraction) - PR #9 Complete
- [x] AI service OpenAI integration - PR #10 Complete
- [x] AI service generation logic - PR #11 Complete
- [x] Letter service CRUD operations - PR #12 Complete
- [x] Letter service DOCX export - PR #13 Complete
- [x] Frontend foundation (routing, components, layout) - PR #15 Complete

### Phase 3: Frontend Pages (14% - 1/7 PRs Complete)
- [x] Document library page - PR #16 Complete
- [ ] Template management page - PR #17 Next
- [ ] Create letter page - PR #18
- [ ] Finalize letter page - PR #19
- [ ] Generated letters library page - PR #20
- [ ] Edit letter page - PR #21

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
3. **Authentication:** Mock authentication implemented - password accepted but not validated. Login endpoint queries User by email and returns user/firm/role information. Frontend stores user data in localStorage with validation, protects all routes except /login, displays user menu with logout, and injects firmId/userId headers in all API requests. All hooks use camelCase property names (firmId, userId, firmName, role).
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

