# Demand Letter Generator - PR Implementation List
# Part 3: AI Service and Letter Service

## PR #11: AI Service - Backend (Part 2: Generation Logic)

### AI Business Logic
- [x] 1. Create services/ai_service/logic.py
- [x] 2. Implement generate_letter function:
  - [x] Validate document count (max 5)
  - [x] Fetch template from database
  - [x] Verify template exists and user has access
  - [x] Fetch all documents from database
  - [x] Verify all documents exist and user has access
  - [x] Call parser service to extract text from documents
  - [x] Build prompt with template and document context
  - [x] Call OpenAI client to generate letter
  - [x] Sanitize HTML output
  - [x] Create letter record in database with status='draft'
  - [x] Create letter-document associations
  - [x] Return letter ID and content
- [x] 3. Add validation for empty document text
- [x] 4. Add validation for OpenAI response
- [x] 5. Add error handling for parser service failures
- [x] 6. Add error handling for OpenAI API failures
- [x] 7. Add error handling for database operations
- [x] 8. Add logging for generation requests
- [x] 9. Add logging for successful generations
- [x] 10. Add logging for failed generations

### AI Router
- [x] 11. Create services/ai_service/router.py
- [x] 12. Create APIRouter with prefix "/generate"
- [x] 13. Implement POST /letter endpoint:
  - [x] Get firm_id from query param (MVP approach)
  - [x] Validate request body
  - [x] Call generate_letter logic
  - [x] Return 201 with letter ID and content
- [ ] 14. Add rate limiting for generation endpoint (optional - skipped for MVP)
- [x] 15. Add OpenAPI documentation
- [x] 16. Add example request/response (in schema)

### Lambda Handler
- [x] 17. Create services/ai_service/handler.py
- [x] 18. Import router and create FastAPI app
- [x] 19. Create generate handler function using Mangum
- [x] 20. Configure timeout to 60 seconds (note: configured in Lambda, handler ready)

### Testing Utilities
- [ ] 21. Create services/ai_service/test_prompts.py (optional - skipped for MVP)
- [x] 22. Add sample document text for testing (user created sample docs)
- [x] 23. Add sample template for testing (user created sample templates)
- [ ] 24. Add function to test prompt generation locally (optional - skipped for MVP)
- [ ] 25. Add function to test OpenAI API without database (optional - skipped for MVP)

**PR #11 Status: ✅ COMPLETE** (Core functionality complete, optional testing utilities deferred)

---

## PR #12: Letter Service - Backend (Part 1: CRUD Operations)

### Letter Schemas
- [x] 1. Create services/letter_service/schemas.py
- [x] 2. Define LetterBase schema
- [x] 3. Define LetterResponse schema:
  - [x] id (UUID)
  - [x] title (string)
  - [x] content (HTML string)
  - [x] status (draft or created)
  - [x] template_id (UUID)
  - [x] template_name (string)
  - [x] source_documents (list of document metadata)
  - [x] docx_url (string, nullable)
  - [x] created_at (datetime)
  - [x] updated_at (datetime)
- [x] 4. Define LetterListResponse schema
- [x] 5. Define LetterUpdate schema:
  - [x] title (optional)
  - [x] content (optional)
- [x] 6. Define FinalizeResponse schema
- [x] 7. Define ExportResponse schema

### Letter Business Logic - CRUD
- [x] 8. Create services/letter_service/logic.py
- [x] 9. Implement get_letters function:
  - [x] Query letters by firm_id
  - [x] Join with template for template name
  - [x] Join with documents for source documents
  - [x] Apply sorting (created_at, updated_at, title, status)
  - [x] Apply pagination
  - [x] Return list with full metadata
- [x] 10. Implement get_letter_by_id function:
  - [x] Verify letter exists
  - [x] Verify user has access (firm_id match)
  - [x] Join with template
  - [x] Join with source documents
  - [x] Generate presigned URL if docx exists
  - [x] Return full letter data
- [x] 11. Implement update_letter function:
  - [x] Verify letter exists
  - [x] Verify user has access
  - [x] Update title and/or content
  - [x] Update updated_at timestamp
  - [x] Return updated letter
- [x] 12. Implement delete_letter function:
  - [x] Verify letter exists
  - [x] Verify user has access
  - [x] Delete .docx from S3 if exists
  - [x] Delete letter-document associations
  - [x] Delete letter from database
  - [x] Return success response
- [x] 13. Add error handling for all functions

### Letter Router - CRUD
- [x] 14. Create services/letter_service/router.py
- [x] 15. Create APIRouter with prefix "/letters"
- [x] 16. Implement GET / endpoint:
  - [x] Get current user from auth
  - [x] Accept query params for sorting, filtering, pagination
  - [x] Call get_letters logic
  - [x] Return 200 with letter list
- [x] 17. Implement GET /{letter_id} endpoint:
  - [x] Get current user from auth
  - [x] Call get_letter_by_id logic
  - [x] Return 200 with letter data
- [x] 18. Implement PUT /{letter_id} endpoint:
  - [x] Get current user from auth
  - [x] Validate request body
  - [x] Call update_letter logic
  - [x] Return 200 with updated letter
- [x] 19. Implement DELETE /{letter_id} endpoint:
  - [x] Get current user from auth
  - [x] Call delete_letter logic
  - [x] Return 204 no content
- [x] 20. Add OpenAPI documentation for CRUD endpoints

**PR #12 Status: ✅ COMPLETE**

---

## PR #13: Letter Service - Backend (Part 2: DOCX Export)

### Requirements & Design Decisions

**HTML to DOCX Conversion:**
- Create custom HTML parser that converts HTML to python-docx Document objects
- Parser service is for PDFs only, not HTML, so we build our own HTML parser
- Support: `<p>`, `<h1>`, `<h2>`, `<h3>`, `<strong>`, `<b>`, `<em>`, `<i>`, `<ul>`, `<ol>`, `<li>`
- Handle nested tags appropriately
- We're using HTML here instead of having the LLM go straight to python-docx BECAUSE we want to display it to the user and make it editable before finalizing

**Filename Generation:**
- Format: `Demand_Letter_[Title]_[Date].docx`
- Sanitize title: remove special characters, keep alphanumeric + spaces/underscores/hyphens
- Replace spaces with underscores
- Length limit: 50 characters (truncate if needed)

**S3 Key Structure:**
- Format: `{firmId}/letters/{filename}.docx`
- No letter_id in path (simpler structure)

**Finalize Letter Behavior:**
- Allow finalizing letters with status 'draft' OR 'created' (user may edit finalized letters)
- Always generate new DOCX (overwrite existing if present)
- Change status to 'created' if not already
- If filename changes (docx_s3_key changes), clean up old file from S3 if possible

**Export Letter Behavior:**
- Return existing presigned URL if docx_s3_key exists
- If no docx_s3_key exists, generate DOCX and upload
- Update docx_s3_key if it changes
- If filename changes, clean up old file from S3 if possible

### DOCX Generator Implementation
- [x] 1. Create services/letter_service/docx_generator.py
- [x] 2. Import python-docx library
- [x] 3. Implement html_to_docx function:
  - [x] Parse HTML content
  - [x] Create new Document
  - [x] Convert HTML tags to docx formatting:
    - [x] <p> → paragraph
    - [x] <h1>, <h2>, <h3> → headings
    - [x] <strong>, <b> → bold
    - [x] <em>, <i> → italic
    - [x] <ul>, <ol>, <li> → lists
  - [x] Handle nested tags
  - [x] Apply styling
  - [x] Return Document object
- [x] 4. Implement generate_filename function:
  - [x] Accept letter title and date
  - [x] Sanitize title
  - [x] Format as "Demand_Letter_[Title]_[Date].docx"
  - [x] Return filename
- [x] 5. Implement save_docx_to_s3 function:
  - [x] Accept Document object
  - [x] Save to BytesIO buffer
  - [x] Upload buffer to S3
  - [x] Return S3 key
- [x] 6. Add error handling for HTML parsing
- [x] 7. Add error handling for docx generation
- [x] 8. Add error handling for S3 upload

### Letter Business Logic - Export
- [x] 9. Add finalize_letter function to logic.py:
  - [x] Verify letter exists
  - [x] Verify user has access
  - [x] Allow status 'draft' OR 'created' (re-finalizing allowed)
  - [x] Generate .docx from content
  - [x] Upload .docx to S3
  - [x] Update letter record:
    - [x] Set status to 'created'
    - [x] Set docx_s3_key
  - [x] Clean up old file if filename changed
  - [x] Return letter with download URL
- [x] 10. Add export_letter function to logic.py:
  - [x] Verify letter exists
  - [x] Verify user has access
  - [x] Return existing presigned URL if docx_s3_key exists
  - [x] Generate new .docx from current content if needed
  - [x] Upload to S3
  - [x] Update docx_s3_key if changed
  - [x] Clean up old file if filename changed
  - [x] Return download URL
- [x] 11. Add error handling for finalize operations
- [x] 12. Add error handling for export operations

### Letter Router - Export
- [x] 13. Implement POST /{letter_id}/finalize endpoint:
  - [x] Get firm_id from path
  - [x] Call finalize_letter logic
  - [x] Return 200 with letter data and download URL
- [x] 14. Implement POST /{letter_id}/export endpoint:
  - [x] Get firm_id from path
  - [x] Call export_letter logic
  - [x] Return 200 with download URL
- [x] 15. Add OpenAPI documentation for export endpoints

### Lambda Handler
- [x] 16. Create services/letter_service/handler.py
- [x] 17. Import router and create FastAPI app
- [x] 18. Create list handler function using Mangum
- [x] 19. Create get handler function using Mangum
- [x] 20. Create update handler function using Mangum
- [x] 21. Create delete handler function using Mangum
- [x] 22. Create finalize handler function using Mangum
- [x] 23. Create export handler function using Mangum

**PR #13 Status: ✅ COMPLETE**

---

## PR #14: Local Development Main Application

### Main FastAPI Application
- [x] 1. Update backend/main.py
- [x] 2. Create FastAPI app instance
- [x] 3. Configure CORS middleware:
  - [x] Allow frontend origin
  - [x] Allow credentials
  - [x] Allow all methods
  - [x] Allow all headers
- [x] 4. Add exception handlers
- [x] 5. Import all service routers:
  - [x] document_service.router
  - [x] template_service.router
  - [x] parser_service.router
  - [x] ai_service.router
  - [x] letter_service.router
- [x] 6. Include document router with prefix "/documents"
- [x] 7. Include template router with prefix "/templates"
- [x] 8. Include parser router with prefix "/parse"
- [x] 9. Include ai router with prefix "/generate"
- [x] 10. Include letter router with prefix "/letters"
- [x] 11. Create health check endpoint GET /health
- [x] 12. Create root endpoint GET / with API info
- [x] 13. Add startup event to check database connection
- [x] 14. Add startup event to check S3 connection
- [x] 15. Add shutdown event for cleanup
- [x] 16. Configure OpenAPI documentation
- [x] 17. Add API version to docs
- [x] 18. Add contact info to docs

### Development Scripts
- [ ] 19. Create scripts/run_local.sh (SKIPPED - Using docker-compose directly with start_server.sh, end_server.sh, restart_server.sh)
- [ ] 20. Add commands to start Docker Compose (SKIPPED - Handled by start_server.sh)
- [ ] 21. Add commands to wait for database (SKIPPED - Handled by docker-compose healthchecks)
- [ ] 22. Add commands to run migrations (COMPLETE - Created migration_scripts/migrate-up.sh, migrate-down.sh, migrate-create.sh)
- [ ] 23. Add commands to start uvicorn (SKIPPED - Handled by docker-compose)
- [ ] 24. Create scripts/seed_data.py for test data (SKIPPED - seed_test_firm.py and seed_test_users.py already exist)
- [ ] 25. Add function to create test firm (SKIPPED - seed_test_firm.py exists)
- [ ] 26. Add function to create test users (SKIPPED - seed_test_users.py exists)
- [ ] 27. Add function to create test templates (SKIPPED - Can be added later if needed)
- [ ] 28. Add function to upload test documents (SKIPPED - Can be added later if needed)

### Testing Setup
- [ ] 29. Create tests/__init__.py (SKIPPED - Optional for MVP)
- [ ] 30. Create tests/conftest.py with pytest fixtures (SKIPPED - Optional for MVP)
- [ ] 31. Add fixture for test database (SKIPPED - Optional for MVP)
- [ ] 32. Add fixture for test client (SKIPPED - Optional for MVP)
- [ ] 33. Add fixture for authenticated user (SKIPPED - Optional for MVP)
- [ ] 34. Create tests/test_health.py (SKIPPED - Optional for MVP)
- [ ] 35. Add test for health check endpoint (SKIPPED - Optional for MVP)
- [ ] 36. Create requirements-dev.txt with test dependencies (SKIPPED - Optional for MVP)

### Additional Scripts Created
- [x] Created start_server.sh, end_server.sh, restart_server.sh in /backend for docker-compose management
- [x] Created migration_scripts/migrate-up.sh, migrate-down.sh, migrate-create.sh for alembic migrations
- [x] Created scripts/check_letter_table.py for checking generated_letters table (first 5 results)

**PR #14 Status: ✅ COMPLETE** (Core functionality complete, testing setup deferred to MVP+)

---

## PR #15: Frontend Foundation and Routing

### App Structure
- [x] 1. Create src/App.jsx
- [x] 2. Set up React Router with BrowserRouter
- [x] 3. Define route structure:
  - [x] / → Dashboard (redirect to /dashboard)
  - [x] /dashboard → Dashboard (Document Library)
  - [x] /upload-assets → Upload Assets
  - [x] /templates → Template Management
  - [x] /create-letter → Letter Generation
  - [x] /letters → Generated Letters Library
  - [x] /letters/:id/finalize → Finalize Letter
  - [x] /letters/:id/edit → Edit Letter
- [x] 4. Create layout component with navigation
- [x] 5. Create 404 Not Found page

### Base Components
- [x] 6. Create src/components/ui/ directory (for shadcn components)
- [x] 7. Install and configure shadcn button component
- [x] 8. Install and configure shadcn input component
- [x] 9. Install and configure shadcn card component
- [x] 10. Install and configure shadcn dialog component
- [x] 11. Install and configure shadcn checkbox component
- [x] 12. Install and configure shadcn switch component
- [x] 13. Install and configure shadcn select component
- [x] 14. Install and configure shadcn textarea component
- [x] 15. Install and configure shadcn badge component
- [x] 16. Install and configure shadcn table component

### Layout Components
- [x] 17. Create src/components/Layout/MainLayout.jsx
- [x] 18. Add navigation header
- [x] 19. Add navigation menu (horizontal, not sidebar)
- [x] 20. Add main content area
- [x] 21. Add user profile display in header
- [x] 22. Create src/components/Layout/Navigation.jsx
- [x] 23. Add navigation links with active states (underline style)
- [x] 24. Add icons from lucide-react

### Utility Setup
- [x] 25. Create src/lib/utils.js (already existed)
- [x] 26. Add cn() function for className merging
- [x] 27. Create src/lib/api.ts for axios configuration
- [x] 28. Configure axios base URL from env
- [x] 29. Configure axios interceptors for auth tokens
- [x] 30. Configure axios error handling
- [x] 31. Create src/lib/constants.ts
- [x] 32. Define API endpoints as constants
- [x] 33. Define file size limits
- [x] 34. Define supported file types

### Type Definitions
- [x] 35. Create src/types/document.ts
- [x] 36. Define Document interface
- [x] 37. Create src/types/template.ts
- [x] 38. Define Template interface
- [x] 39. Create src/types/letter.ts
- [x] 40. Define Letter interface
- [x] 41. Define LetterStatus enum
- [x] 42. Create src/types/api.ts
- [x] 43. Define ApiResponse interface
- [x] 44. Define PaginatedResponse interface

### Context and State Management
- [x] 45. Create src/contexts/AuthContext.jsx
- [x] 46. Define AuthContext with user state
- [x] 47. Create login and logout functions (placeholder)
- [x] 48. Create useAuth custom hook
- [x] 49. Wrap App with AuthProvider

