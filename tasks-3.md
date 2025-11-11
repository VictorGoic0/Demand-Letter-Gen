# Demand Letter Generator - PR Implementation List
# Part 3: AI Service and Letter Service

## PR #11: AI Service - Backend (Part 2: Generation Logic)

### AI Business Logic
- [ ] 1. Create services/ai_service/logic.py
- [ ] 2. Implement generate_letter function:
  - [ ] Validate document count (max 5)
  - [ ] Fetch template from database
  - [ ] Verify template exists and user has access
  - [ ] Fetch all documents from database
  - [ ] Verify all documents exist and user has access
  - [ ] Call parser service to extract text from documents
  - [ ] Build prompt with template and document context
  - [ ] Call OpenAI client to generate letter
  - [ ] Sanitize HTML output
  - [ ] Create letter record in database with status='draft'
  - [ ] Create letter-document associations
  - [ ] Return letter ID and content
- [ ] 3. Add validation for empty document text
- [ ] 4. Add validation for OpenAI response
- [ ] 5. Add error handling for parser service failures
- [ ] 6. Add error handling for OpenAI API failures
- [ ] 7. Add error handling for database operations
- [ ] 8. Add logging for generation requests
- [ ] 9. Add logging for successful generations
- [ ] 10. Add logging for failed generations

### AI Router
- [ ] 11. Create services/ai_service/router.py
- [ ] 12. Create APIRouter with prefix "/generate"
- [ ] 13. Implement POST /letter endpoint:
  - [ ] Get current user from auth
  - [ ] Validate request body
  - [ ] Call generate_letter logic
  - [ ] Return 201 with letter ID and content
- [ ] 14. Add rate limiting for generation endpoint (optional)
- [ ] 15. Add OpenAPI documentation
- [ ] 16. Add example request/response

### Lambda Handler
- [ ] 17. Create services/ai_service/handler.py
- [ ] 18. Import router and create FastAPI app
- [ ] 19. Create generate handler function using Mangum
- [ ] 20. Configure timeout to 60 seconds

### Testing Utilities
- [ ] 21. Create services/ai_service/test_prompts.py
- [ ] 22. Add sample document text for testing
- [ ] 23. Add sample template for testing
- [ ] 24. Add function to test prompt generation locally
- [ ] 25. Add function to test OpenAI API without database

---

## PR #12: Letter Service - Backend (Part 1: CRUD Operations)

### Letter Schemas
- [ ] 1. Create services/letter_service/schemas.py
- [ ] 2. Define LetterBase schema
- [ ] 3. Define LetterResponse schema:
  - [ ] id (UUID)
  - [ ] title (string)
  - [ ] content (HTML string)
  - [ ] status (draft or created)
  - [ ] template_id (UUID)
  - [ ] template_name (string)
  - [ ] source_documents (list of document metadata)
  - [ ] docx_url (string, nullable)
  - [ ] created_at (datetime)
  - [ ] updated_at (datetime)
- [ ] 4. Define LetterListResponse schema
- [ ] 5. Define LetterUpdate schema:
  - [ ] title (optional)
  - [ ] content (optional)
- [ ] 6. Define FinalizeResponse schema
- [ ] 7. Define ExportResponse schema

### Letter Business Logic - CRUD
- [ ] 8. Create services/letter_service/logic.py
- [ ] 9. Implement get_letters function:
  - [ ] Query letters by firm_id
  - [ ] Join with template for template name
  - [ ] Join with documents for source documents
  - [ ] Apply sorting (created_at, updated_at, title, status)
  - [ ] Apply pagination
  - [ ] Return list with full metadata
- [ ] 10. Implement get_letter_by_id function:
  - [ ] Verify letter exists
  - [ ] Verify user has access (firm_id match)
  - [ ] Join with template
  - [ ] Join with source documents
  - [ ] Generate presigned URL if docx exists
  - [ ] Return full letter data
- [ ] 11. Implement update_letter function:
  - [ ] Verify letter exists
  - [ ] Verify user has access
  - [ ] Update title and/or content
  - [ ] Update updated_at timestamp
  - [ ] Return updated letter
- [ ] 12. Implement delete_letter function:
  - [ ] Verify letter exists
  - [ ] Verify user has access
  - [ ] Delete .docx from S3 if exists
  - [ ] Delete letter-document associations
  - [ ] Delete letter from database
  - [ ] Return success response
- [ ] 13. Add error handling for all functions

### Letter Router - CRUD
- [ ] 14. Create services/letter_service/router.py
- [ ] 15. Create APIRouter with prefix "/letters"
- [ ] 16. Implement GET / endpoint:
  - [ ] Get current user from auth
  - [ ] Accept query params for sorting, filtering, pagination
  - [ ] Call get_letters logic
  - [ ] Return 200 with letter list
- [ ] 17. Implement GET /{letter_id} endpoint:
  - [ ] Get current user from auth
  - [ ] Call get_letter_by_id logic
  - [ ] Return 200 with letter data
- [ ] 18. Implement PUT /{letter_id} endpoint:
  - [ ] Get current user from auth
  - [ ] Validate request body
  - [ ] Call update_letter logic
  - [ ] Return 200 with updated letter
- [ ] 19. Implement DELETE /{letter_id} endpoint:
  - [ ] Get current user from auth
  - [ ] Call delete_letter logic
  - [ ] Return 204 no content
- [ ] 20. Add OpenAPI documentation for CRUD endpoints

---

## PR #13: Letter Service - Backend (Part 2: DOCX Export)

### DOCX Generator Implementation
- [ ] 1. Create services/letter_service/docx_generator.py
- [ ] 2. Import python-docx library
- [ ] 3. Implement html_to_docx function:
  - [ ] Parse HTML content
  - [ ] Create new Document
  - [ ] Convert HTML tags to docx formatting:
    - [ ] <p> → paragraph
    - [ ] <h1>, <h2>, <h3> → headings
    - [ ] <strong>, <b> → bold
    - [ ] <em>, <i> → italic
    - [ ] <ul>, <ol>, <li> → lists
  - [ ] Handle nested tags
  - [ ] Apply styling
  - [ ] Return Document object
- [ ] 4. Implement generate_filename function:
  - [ ] Accept letter title and date
  - [ ] Sanitize title
  - [ ] Format as "Demand_Letter_[Title]_[Date].docx"
  - [ ] Return filename
- [ ] 5. Implement save_docx_to_s3 function:
  - [ ] Accept Document object
  - [ ] Save to BytesIO buffer
  - [ ] Upload buffer to S3
  - [ ] Return S3 key
- [ ] 6. Add error handling for HTML parsing
- [ ] 7. Add error handling for docx generation
- [ ] 8. Add error handling for S3 upload

### Letter Business Logic - Export
- [ ] 9. Add finalize_letter function to logic.py:
  - [ ] Verify letter exists
  - [ ] Verify user has access
  - [ ] Verify status is 'draft'
  - [ ] Generate .docx from content
  - [ ] Upload .docx to S3
  - [ ] Update letter record:
    - [ ] Set status to 'created'
    - [ ] Set docx_s3_key
  - [ ] Return letter with download URL
- [ ] 10. Add export_letter function to logic.py:
  - [ ] Verify letter exists
  - [ ] Verify user has access
  - [ ] Generate new .docx from current content
  - [ ] Upload to S3 (overwrite or new file)
  - [ ] Update docx_s3_key if changed
  - [ ] Return download URL
- [ ] 11. Add error handling for finalize operations
- [ ] 12. Add error handling for export operations

### Letter Router - Export
- [ ] 13. Implement POST /{letter_id}/finalize endpoint:
  - [ ] Get current user from auth
  - [ ] Call finalize_letter logic
  - [ ] Return 200 with letter data and download URL
- [ ] 14. Implement POST /{letter_id}/export endpoint:
  - [ ] Get current user from auth
  - [ ] Call export_letter logic
  - [ ] Return 200 with download URL
- [ ] 15. Add OpenAPI documentation for export endpoints

### Lambda Handler
- [ ] 16. Create services/letter_service/handler.py
- [ ] 17. Import router and create FastAPI app
- [ ] 18. Create list handler function using Mangum
- [ ] 19. Create get handler function using Mangum
- [ ] 20. Create update handler function using Mangum
- [ ] 21. Create delete handler function using Mangum
- [ ] 22. Create finalize handler function using Mangum
- [ ] 23. Create export handler function using Mangum

---

## PR #14: Local Development Main Application

### Main FastAPI Application
- [ ] 1. Update backend/main.py
- [ ] 2. Create FastAPI app instance
- [ ] 3. Configure CORS middleware:
  - [ ] Allow frontend origin
  - [ ] Allow credentials
  - [ ] Allow all methods
  - [ ] Allow all headers
- [ ] 4. Add exception handlers
- [ ] 5. Import all service routers:
  - [ ] document_service.router
  - [ ] template_service.router
  - [ ] parser_service.router
  - [ ] ai_service.router
  - [ ] letter_service.router
- [ ] 6. Include document router with prefix "/documents"
- [ ] 7. Include template router with prefix "/templates"
- [ ] 8. Include parser router with prefix "/parse"
- [ ] 9. Include ai router with prefix "/generate"
- [ ] 10. Include letter router with prefix "/letters"
- [ ] 11. Create health check endpoint GET /health
- [ ] 12. Create root endpoint GET / with API info
- [ ] 13. Add startup event to check database connection
- [ ] 14. Add startup event to check S3 connection
- [ ] 15. Add shutdown event for cleanup
- [ ] 16. Configure OpenAPI documentation
- [ ] 17. Add API version to docs
- [ ] 18. Add contact info to docs

### Development Scripts
- [ ] 19. Create scripts/run_local.sh
- [ ] 20. Add commands to start Docker Compose
- [ ] 21. Add commands to wait for database
- [ ] 22. Add commands to run migrations
- [ ] 23. Add commands to start uvicorn
- [ ] 24. Create scripts/seed_data.py for test data
- [ ] 25. Add function to create test firm
- [ ] 26. Add function to create test users
- [ ] 27. Add function to create test templates
- [ ] 28. Add function to upload test documents

### Testing Setup
- [ ] 29. Create tests/__init__.py
- [ ] 30. Create tests/conftest.py with pytest fixtures
- [ ] 31. Add fixture for test database
- [ ] 32. Add fixture for test client
- [ ] 33. Add fixture for authenticated user
- [ ] 34. Create tests/test_health.py
- [ ] 35. Add test for health check endpoint
- [ ] 36. Create requirements-dev.txt with test dependencies

---

## PR #15: Frontend Foundation and Routing

### App Structure
- [ ] 1. Create src/App.tsx
- [ ] 2. Set up React Router with BrowserRouter
- [ ] 3. Define route structure:
  - [ ] / → Dashboard (redirect to /documents)
  - [ ] /documents → Document Library
  - [ ] /templates → Template Management
  - [ ] /create-letter → Letter Generation
  - [ ] /letters → Generated Letters Library
  - [ ] /letters/:id/finalize → Finalize Letter
  - [ ] /letters/:id/edit → Edit Letter
- [ ] 4. Create layout component with navigation
- [ ] 5. Create 404 Not Found page

### Base Components
- [ ] 6. Create src/components/ui/ directory (for shadcn components)
- [ ] 7. Install and configure shadcn button component
- [ ] 8. Install and configure shadcn input component
- [ ] 9. Install and configure shadcn card component
- [ ] 10. Install and configure shadcn dialog component
- [ ] 11. Install and configure shadcn checkbox component
- [ ] 12. Install and configure shadcn switch component
- [ ] 13. Install and configure shadcn select component
- [ ] 14. Install and configure shadcn textarea component
- [ ] 15. Install and configure shadcn badge component
- [ ] 16. Install and configure shadcn table component

### Layout Components
- [ ] 17. Create src/components/Layout/MainLayout.tsx
- [ ] 18. Add navigation header
- [ ] 19. Add sidebar navigation menu
- [ ] 20. Add main content area
- [ ] 21. Add user profile dropdown (placeholder)
- [ ] 22. Create src/components/Layout/Navigation.tsx
- [ ] 23. Add navigation links with active states
- [ ] 24. Add icons from lucide-react

### Utility Setup
- [ ] 25. Create src/lib/utils.ts
- [ ] 26. Add cn() function for className merging
- [ ] 27. Create src/lib/api.ts for axios configuration
- [ ] 28. Configure axios base URL from env
- [ ] 29. Configure axios interceptors for auth tokens
- [ ] 30. Configure axios error handling
- [ ] 31. Create src/lib/constants.ts
- [ ] 32. Define API endpoints as constants
- [ ] 33. Define file size limits
- [ ] 34. Define supported file types

### Type Definitions
- [ ] 35. Create src/types/document.ts
- [ ] 36. Define Document interface
- [ ] 37. Create src/types/template.ts
- [ ] 38. Define Template interface
- [ ] 39. Create src/types/letter.ts
- [ ] 40. Define Letter interface
- [ ] 41. Define LetterStatus enum
- [ ] 42. Create src/types/api.ts
- [ ] 43. Define ApiResponse interface
- [ ] 44. Define PaginatedResponse interface

### Context and State Management
- [ ] 45. Create src/contexts/AuthContext.tsx
- [ ] 46. Define AuthContext with user state
- [ ] 47. Create login and logout functions (placeholder)
- [ ] 48. Create useAuth custom hook
- [ ] 49. Wrap App with AuthProvider

