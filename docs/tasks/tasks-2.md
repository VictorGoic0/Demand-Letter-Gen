# Demand Letter Generator - PR Implementation List
# Part 2: Backend Services

## PR #6: Shared Backend Utilities

### Configuration Management
- [x] 1. Create shared/config.py
- [x] 2. Define Settings class with pydantic BaseSettings
- [x] 3. Add database configuration fields
- [x] 4. Add AWS configuration fields
- [x] 5. Add OpenAI configuration fields
- [x] 6. Add CORS configuration fields
- [x] 7. Create function to load settings singleton
- [x] 8. Add validation for required fields
- [x] 9. Add development vs production config handling

### Common Schemas
- [x] 10. Create shared/schemas/__init__.py
- [x] 11. Create shared/schemas/common.py with base schemas
- [x] 12. Define SuccessResponse schema
- [x] 13. Define ErrorResponse schema
- [x] 14. Define PaginationParams schema
- [x] 15. Define PaginatedResponse schema

### Error Handling
- [x] 16. Create shared/exceptions.py
- [x] 17. Define custom exception classes:
  - [x] DocumentNotFoundException
  - [x] TemplateNotFoundException
  - [x] LetterNotFoundException
  - [x] S3UploadException
  - [x] OpenAIException
- [x] 18. Create exception handlers for FastAPI
- [x] 19. Add global exception handler

### Utilities
- [x] 20. Create shared/utils.py
- [x] 21. Add function to generate UUIDs
- [x] 22. Add function for datetime formatting
- [x] 23. Add function for file size formatting
- [x] 24. Add function for filename sanitization
- [x] 25. Add function for HTML sanitization

---

## PR #7: Document Service - Backend

### Document Schemas
- [x] 1. Create services/document_service/schemas.py
- [x] 2. Define DocumentBase schema
- [x] 3. Define DocumentCreate schema
- [x] 4. Define DocumentResponse schema
- [x] 5. Define DocumentListResponse schema
- [x] 6. Define UploadResponse schema
- [x] 7. Add validation for file types
- [x] 8. Add validation for file size

### Document Business Logic
- [x] 9. Create services/document_service/logic.py
- [x] 10. Implement upload_document function:
  - [x] Validate file type and size
  - [x] Generate unique S3 key
  - [x] Upload to S3
  - [x] Create database record with firm_id (firm-level isolation)
  - [x] Return document metadata
- [x] 11. Implement get_documents function:
  - [x] Query documents by firm_id (firm-level isolation)
  - [x] Apply sorting (filename, upload date)
  - [x] Apply pagination
  - [x] Return list with metadata
- [x] 12. Implement get_document_by_id function:
  - [x] Verify document exists
  - [x] Verify document belongs to firm_id (firm-level isolation)
  - [x] Return document metadata
- [x] 13. Implement delete_document function:
  - [x] Verify document exists
  - [x] Verify document belongs to firm_id (firm-level isolation)
  - [x] Delete from S3
  - [x] Delete from database
  - [x] Return success response
- [x] 14. Implement generate_download_url function:
  - [x] Verify document exists
  - [x] Verify document belongs to firm_id (firm-level isolation)
  - [x] Generate presigned S3 URL
  - [x] Return URL with expiration
- [x] 15. Add error handling for all functions

### Document Router
- [x] 16. Create services/document_service/router.py
- [x] 17. Create APIRouter with prefix "/{firm_id}/documents"
- [x] 18. Implement POST / endpoint:
  - [x] Accept multipart/form-data
  - [x] Accept firm_id (path parameter)
  - [x] Use UploadFile from FastAPI
  - [x] Call upload_document logic with firm_id
  - [x] Return 201 with document metadata
- [x] 19. Implement GET / endpoint:
  - [x] Accept query params for sorting and pagination
  - [x] Accept firm_id (path parameter)
  - [x] Call get_documents logic with firm_id
  - [x] Return 200 with document list
- [x] 20. Implement GET /{document_id} endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Call get_document_by_id logic with firm_id
  - [x] Return 200 with document metadata
- [x] 21. Implement DELETE /{document_id} endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Call delete_document logic with firm_id
  - [x] Return 204 no content
- [x] 22. Implement GET /{document_id}/download endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Call generate_download_url logic with firm_id
  - [x] Return 200 with presigned URL
- [x] 23. Add OpenAPI documentation for all endpoints

### Lambda Handler
- [x] 24. Create services/document_service/handler.py
- [x] 25. Import router and create FastAPI app
- [x] 26. Create upload handler function using Mangum
- [x] 27. Create list handler function using Mangum
- [x] 28. Create get handler function using Mangum
- [x] 29. Create delete handler function using Mangum
- [x] 30. Create download handler function using Mangum

### Testing Scripts
- [x] 31. Create scripts/seed_test_firm.py - Standalone script to seed test firm
- [x] 32. Create scripts/seed_test_users.py - Standalone script to seed test users
- [x] 33. Create scripts/check_firm_table.py - Standalone script to query firms table
- [x] 34. Create scripts/check_users_table.py - Standalone script to query users table
- [x] 35. Create scripts/test_document_api.py - Test script for document upload endpoint only

### Configuration Fixes
- [x] 36. Fix docker-compose.yml environment variable loading (removed env_file, use environment section with ${VAR} syntax)
- [x] 37. Fix Pydantic Settings validation for nested configs (added extra="ignore" to Settings.model_config, implemented custom env source for AWSConfig)

### Database Constraints
- [x] 38. Add CheckConstraint to User.role column (only 'attorney' or 'paralegal')
- [x] 39. Add CheckConstraint to GeneratedLetter.status column (only 'draft' or 'created')

**PR #7 Status: ✅ COMPLETE**

---

## PR #8: Template Service - Backend

### Template Schemas
- [x] 1. Create services/template_service/schemas.py
- [x] 2. Define TemplateBase schema
- [x] 3. Define TemplateCreate schema:
  - [x] name (required)
  - [x] letterhead_text (optional)
  - [x] opening_paragraph (optional)
  - [x] closing_paragraph (optional)
  - [x] sections (list of strings)
  - [x] is_default (boolean, default false)
- [x] 4. Define TemplateUpdate schema (all fields optional)
- [x] 5. Define TemplateResponse schema
- [x] 6. Define TemplateListResponse schema
- [x] 7. Add validation for section names
- [x] 8. Add validation for template name length

### Template Business Logic
- [x] 9. Create services/template_service/logic.py
- [x] 10. Implement create_template function:
  - [x] Validate template data
  - [x] If is_default=True, unset other defaults for firm
  - [x] Create database record with firm_id (firm-level isolation)
  - [x] Return template data
- [x] 11. Implement get_templates function:
  - [x] Query templates by firm_id (firm-level isolation)
  - [x] Apply sorting (name, created date)
  - [x] Return list of templates
- [x] 12. Implement get_template_by_id function:
  - [x] Verify template exists
  - [x] Verify template belongs to firm_id (firm-level isolation)
  - [x] Return template data
- [x] 13. Implement update_template function:
  - [x] Verify template exists
  - [x] Verify template belongs to firm_id (firm-level isolation)
  - [x] If is_default=True, unset other defaults for firm
  - [x] Update fields
  - [x] Return updated template
- [x] 14. Implement delete_template function:
  - [x] Verify template exists
  - [x] Verify template belongs to firm_id (firm-level isolation)
  - [x] Check if template is in use by letters
  - [x] Delete from database
  - [x] Return success response
- [x] 15. Implement get_default_template function:
  - [x] Query for is_default=True and firm_id (firm-level isolation)
  - [x] Return template or None
- [x] 16. Add error handling for all functions

### Template Router
- [x] 17. Create services/template_service/router.py
- [x] 18. Create APIRouter with prefix "/{firm_id}/templates" (path parameter, consistent with document_service)
- [x] 19. Implement POST / endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Validate request body
  - [x] Call create_template logic with firm_id
  - [x] Return 201 with template data
- [x] 20. Implement GET / endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Call get_templates logic with firm_id
  - [x] Return 200 with template list
- [x] 21. Implement GET /default endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Call get_default_template logic with firm_id
  - [x] Return 200 with template or 404
- [x] 22. Implement GET /{template_id} endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Call get_template_by_id logic with firm_id
  - [x] Return 200 with template data
- [x] 23. Implement PUT /{template_id} endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Validate request body
  - [x] Call update_template logic with firm_id
  - [x] Return 200 with updated template
- [x] 24. Implement DELETE /{template_id} endpoint:
  - [x] Accept firm_id (path parameter)
  - [x] Call delete_template logic with firm_id
  - [x] Return 204 no content
- [x] 25. Add OpenAPI documentation for all endpoints

### Lambda Handler
- [x] 26. Create services/template_service/handler.py
- [x] 27. Import router and create FastAPI app
- [x] 28. Create create handler function using Mangum
- [x] 29. Create list handler function using Mangum
- [x] 30. Create get handler function using Mangum
- [x] 31. Create update handler function using Mangum
- [x] 32. Create delete handler function using Mangum

**PR #8 Status: ✅ COMPLETE**

---

## PR #9: Parser Service - Backend

### PDF Parser Implementation
- [x] 1. Create services/parser_service/pdf_parser.py
- [x] 2. Import pypdf library
- [x] 3. Implement extract_text_from_pdf function:
  - [x] Accept file bytes or file path
  - [x] Open PDF with pypdf
  - [x] Extract text from all pages
  - [x] Concatenate pages with separators
  - [x] Handle encrypted PDFs
  - [x] Return extracted text
- [x] 4. Implement extract_metadata_from_pdf function:
  - [x] Extract page count
  - [x] Extract file size
  - [x] Extract creation date if available
  - [x] Return metadata dict
- [x] 5. Add error handling for corrupted PDFs
- [x] 6. Add error handling for unsupported PDF versions
- [x] 7. Add function to validate PDF structure

### Parser Schemas
- [x] 8. Create services/parser_service/schemas.py
- [x] 9. Define ParseRequest schema:
  - [x] document_ids (list of UUIDs)
- [x] 10. Define ParseResponse schema:
  - [x] document_id (UUID)
  - [x] extracted_text (string)
  - [x] page_count (int)
- [x] 11. Define ParseBatchResponse schema:
  - [x] results (list of ParseResponse)

### Parser Business Logic
- [x] 12. Create services/parser_service/logic.py
- [x] 13. Implement parse_document function:
  - [x] Get document from database
  - [x] Download file from S3
  - [x] Call extract_text_from_pdf
  - [x] Return extracted text with metadata
- [x] 14. Implement parse_documents_batch function:
  - [x] Accept list of document IDs
  - [x] Process each document
  - [x] Collect results
  - [x] Return batch response
- [x] 15. Add caching for recently parsed documents (optional - skipped for MVP)
- [x] 16. Add error handling for S3 download failures
- [x] 17. Add error handling for parsing failures

### Parser Router
- [x] 18. Create services/parser_service/router.py
- [x] 19. Create APIRouter with prefix "/parse"
- [x] 20. Implement POST /document/{document_id} endpoint:
  - [x] Accept firm_id (query param for MVP)
  - [x] Verify document exists
  - [x] Verify document belongs to firm_id (firm-level isolation)
  - [x] Call parse_document logic
  - [x] Return 200 with parsed text
- [x] 21. Implement POST /batch endpoint:
  - [x] Accept firm_id (query param for MVP)
  - [x] Validate all document IDs
  - [x] Verify all documents exist and belong to firm_id (firm-level isolation)
  - [x] Call parse_documents_batch logic
  - [x] Return 200 with batch results
- [x] 22. Add OpenAPI documentation

### Lambda Handler
- [x] 23. Create services/parser_service/handler.py
- [x] 24. Import router and create FastAPI app
- [x] 25. Create parse handler function using Mangum
- [x] 26. Create batch handler function using Mangum

**PR #9 Status: ✅ COMPLETE**

---

## PR #10: AI Service - Backend (Part 1: OpenAI Integration)

### OpenAI Client Setup
- [x] 1. Create services/ai_service/openai_client.py
- [x] 2. Import OpenAI library
- [x] 3. Initialize OpenAI client with API key from config
- [x] 4. Create function to build generation prompt:
  - [x] Accept template data
  - [x] Accept list of parsed documents
  - [x] Format into structured prompt
  - [x] Include instructions for formatting output as HTML
- [x] 5. Create function to call OpenAI API:
  - [x] Use GPT-4 or GPT-3.5-turbo (configurable)
  - [x] Set appropriate temperature (defaults to 0.7 from config)
  - [x] Return generated text
- [x] 6. Add retry logic for rate limits
- [x] 7. Add retry logic for transient failures
- [x] 8. Add timeout handling
- [x] 9. Add error handling for API errors
- [x] 10. Add function to estimate token count
- [x] 11. Add function to validate response format

### Prompt Engineering
- [x] 12. Create services/ai_service/prompts.py
- [x] 13. Define base system prompt for demand letter generation
- [x] 14. Create function to build context from documents:
  - [x] Format document text with labels
  - [x] Add section separators
  - [x] Truncate if needed to fit context window
- [x] 15. Create function to build template instructions:
  - [x] Include letterhead
  - [x] Include section structure
  - [x] Include opening/closing paragraphs
- [x] 16. Create function to combine all prompt components
- [x] 17. Add prompt for HTML formatting instructions
- [x] 18. Add examples of expected output format

### AI Service Schemas
- [x] 19. Create services/ai_service/schemas.py
- [x] 20. Define GenerateRequest schema:
  - [x] template_id (UUID)
  - [x] document_ids (list of UUIDs, max 5)
  - [x] title (string, optional)
- [x] 21. Define GenerateResponse schema:
  - [x] letter_id (UUID)
  - [x] content (HTML string)
  - [x] status (draft)
- [x] 22. Add validation for document count (max 5)

**PR #10 Status: ✅ COMPLETE**

