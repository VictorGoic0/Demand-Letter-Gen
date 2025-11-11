# Demand Letter Generator - PR Implementation List
# Part 2: Backend Services

## PR #6: Shared Backend Utilities

### Configuration Management
- [ ] 1. Create shared/config.py
- [ ] 2. Define Settings class with pydantic BaseSettings
- [ ] 3. Add database configuration fields
- [ ] 4. Add AWS configuration fields
- [ ] 5. Add OpenAI configuration fields
- [ ] 6. Add CORS configuration fields
- [ ] 7. Create function to load settings singleton
- [ ] 8. Add validation for required fields
- [ ] 9. Add development vs production config handling

### Common Schemas
- [ ] 10. Create shared/schemas/__init__.py
- [ ] 11. Create shared/schemas/common.py with base schemas
- [ ] 12. Define SuccessResponse schema
- [ ] 13. Define ErrorResponse schema
- [ ] 14. Define PaginationParams schema
- [ ] 15. Define PaginatedResponse schema

### Error Handling
- [ ] 16. Create shared/exceptions.py
- [ ] 17. Define custom exception classes:
  - [ ] DocumentNotFoundException
  - [ ] TemplateNotFoundException
  - [ ] LetterNotFoundException
  - [ ] S3UploadException
  - [ ] OpenAIException
- [ ] 18. Create exception handlers for FastAPI
- [ ] 19. Add global exception handler

### Utilities
- [ ] 20. Create shared/utils.py
- [ ] 21. Add function to generate UUIDs
- [ ] 22. Add function for datetime formatting
- [ ] 23. Add function for file size formatting
- [ ] 24. Add function for filename sanitization
- [ ] 25. Add function for HTML sanitization

---

## PR #7: Document Service - Backend

### Document Schemas
- [ ] 1. Create services/document_service/schemas.py
- [ ] 2. Define DocumentBase schema
- [ ] 3. Define DocumentCreate schema
- [ ] 4. Define DocumentResponse schema
- [ ] 5. Define DocumentListResponse schema
- [ ] 6. Define UploadResponse schema
- [ ] 7. Add validation for file types
- [ ] 8. Add validation for file size

### Document Business Logic
- [ ] 9. Create services/document_service/logic.py
- [ ] 10. Implement upload_document function:
  - [ ] Validate file type and size
  - [ ] Generate unique S3 key
  - [ ] Upload to S3
  - [ ] Create database record with firm_id (firm-level isolation)
  - [ ] Return document metadata
- [ ] 11. Implement get_documents function:
  - [ ] Query documents by firm_id (firm-level isolation)
  - [ ] Apply sorting (filename, upload date)
  - [ ] Apply pagination
  - [ ] Return list with metadata
- [ ] 12. Implement get_document_by_id function:
  - [ ] Verify document exists
  - [ ] Verify document belongs to firm_id (firm-level isolation)
  - [ ] Return document metadata
- [ ] 13. Implement delete_document function:
  - [ ] Verify document exists
  - [ ] Verify document belongs to firm_id (firm-level isolation)
  - [ ] Delete from S3
  - [ ] Delete from database
  - [ ] Return success response
- [ ] 14. Implement generate_download_url function:
  - [ ] Verify document exists
  - [ ] Verify document belongs to firm_id (firm-level isolation)
  - [ ] Generate presigned S3 URL
  - [ ] Return URL with expiration
- [ ] 15. Add error handling for all functions

### Document Router
- [ ] 16. Create services/document_service/router.py
- [ ] 17. Create APIRouter with prefix "/documents"
- [ ] 18. Implement POST /upload endpoint:
  - [ ] Accept multipart/form-data
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Use UploadFile from FastAPI
  - [ ] Call upload_document logic with firm_id
  - [ ] Return 201 with document metadata
- [ ] 19. Implement GET / endpoint:
  - [ ] Accept query params for sorting and pagination
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Call get_documents logic with firm_id
  - [ ] Return 200 with document list
- [ ] 20. Implement GET /{document_id} endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Call get_document_by_id logic with firm_id
  - [ ] Return 200 with document metadata
- [ ] 21. Implement DELETE /{document_id} endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Call delete_document logic with firm_id
  - [ ] Return 204 no content
- [ ] 22. Implement GET /{document_id}/download endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Call generate_download_url logic with firm_id
  - [ ] Return 200 with presigned URL
- [ ] 23. Add OpenAPI documentation for all endpoints

### Lambda Handler
- [ ] 24. Create services/document_service/handler.py
- [ ] 25. Import router and create FastAPI app
- [ ] 26. Create upload handler function using Mangum
- [ ] 27. Create list handler function using Mangum
- [ ] 28. Create get handler function using Mangum
- [ ] 29. Create delete handler function using Mangum
- [ ] 30. Create download handler function using Mangum

---

## PR #8: Template Service - Backend

### Template Schemas
- [ ] 1. Create services/template_service/schemas.py
- [ ] 2. Define TemplateBase schema
- [ ] 3. Define TemplateCreate schema:
  - [ ] name (required)
  - [ ] letterhead_text (optional)
  - [ ] opening_paragraph (optional)
  - [ ] closing_paragraph (optional)
  - [ ] sections (list of strings)
  - [ ] is_default (boolean, default false)
- [ ] 4. Define TemplateUpdate schema (all fields optional)
- [ ] 5. Define TemplateResponse schema
- [ ] 6. Define TemplateListResponse schema
- [ ] 7. Add validation for section names
- [ ] 8. Add validation for template name length

### Template Business Logic
- [ ] 9. Create services/template_service/logic.py
- [ ] 10. Implement create_template function:
  - [ ] Validate template data
  - [ ] If is_default=True, unset other defaults for firm
  - [ ] Create database record with firm_id (firm-level isolation)
  - [ ] Return template data
- [ ] 11. Implement get_templates function:
  - [ ] Query templates by firm_id (firm-level isolation)
  - [ ] Apply sorting (name, created date)
  - [ ] Return list of templates
- [ ] 12. Implement get_template_by_id function:
  - [ ] Verify template exists
  - [ ] Verify template belongs to firm_id (firm-level isolation)
  - [ ] Return template data
- [ ] 13. Implement update_template function:
  - [ ] Verify template exists
  - [ ] Verify template belongs to firm_id (firm-level isolation)
  - [ ] If is_default=True, unset other defaults for firm
  - [ ] Update fields
  - [ ] Return updated template
- [ ] 14. Implement delete_template function:
  - [ ] Verify template exists
  - [ ] Verify template belongs to firm_id (firm-level isolation)
  - [ ] Check if template is in use by letters
  - [ ] Delete from database
  - [ ] Return success response
- [ ] 15. Implement get_default_template function:
  - [ ] Query for is_default=True and firm_id (firm-level isolation)
  - [ ] Return template or None
- [ ] 16. Add error handling for all functions

### Template Router
- [ ] 17. Create services/template_service/router.py
- [ ] 18. Create APIRouter with prefix "/templates"
- [ ] 19. Implement POST / endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Validate request body
  - [ ] Call create_template logic with firm_id
  - [ ] Return 201 with template data
- [ ] 20. Implement GET / endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Call get_templates logic with firm_id
  - [ ] Return 200 with template list
- [ ] 21. Implement GET /default endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Call get_default_template logic with firm_id
  - [ ] Return 200 with template or 404
- [ ] 22. Implement GET /{template_id} endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Call get_template_by_id logic with firm_id
  - [ ] Return 200 with template data
- [ ] 23. Implement PUT /{template_id} endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Validate request body
  - [ ] Call update_template logic with firm_id
  - [ ] Return 200 with updated template
- [ ] 24. Implement DELETE /{template_id} endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Call delete_template logic with firm_id
  - [ ] Return 204 no content
- [ ] 25. Add OpenAPI documentation for all endpoints

### Lambda Handler
- [ ] 26. Create services/template_service/handler.py
- [ ] 27. Import router and create FastAPI app
- [ ] 28. Create create handler function using Mangum
- [ ] 29. Create list handler function using Mangum
- [ ] 30. Create get handler function using Mangum
- [ ] 31. Create update handler function using Mangum
- [ ] 32. Create delete handler function using Mangum

---

## PR #9: Parser Service - Backend

### PDF Parser Implementation
- [ ] 1. Create services/parser_service/pdf_parser.py
- [ ] 2. Import pypdf library
- [ ] 3. Implement extract_text_from_pdf function:
  - [ ] Accept file bytes or file path
  - [ ] Open PDF with pypdf
  - [ ] Extract text from all pages
  - [ ] Concatenate pages with separators
  - [ ] Handle encrypted PDFs
  - [ ] Return extracted text
- [ ] 4. Implement extract_metadata_from_pdf function:
  - [ ] Extract page count
  - [ ] Extract file size
  - [ ] Extract creation date if available
  - [ ] Return metadata dict
- [ ] 5. Add error handling for corrupted PDFs
- [ ] 6. Add error handling for unsupported PDF versions
- [ ] 7. Add function to validate PDF structure

### Parser Schemas
- [ ] 8. Create services/parser_service/schemas.py
- [ ] 9. Define ParseRequest schema:
  - [ ] document_ids (list of UUIDs)
- [ ] 10. Define ParseResponse schema:
  - [ ] document_id (UUID)
  - [ ] extracted_text (string)
  - [ ] page_count (int)
- [ ] 11. Define ParseBatchResponse schema:
  - [ ] results (list of ParseResponse)

### Parser Business Logic
- [ ] 12. Create services/parser_service/logic.py
- [ ] 13. Implement parse_document function:
  - [ ] Get document from database
  - [ ] Download file from S3
  - [ ] Call extract_text_from_pdf
  - [ ] Return extracted text with metadata
- [ ] 14. Implement parse_documents_batch function:
  - [ ] Accept list of document IDs
  - [ ] Process each document
  - [ ] Collect results
  - [ ] Return batch response
- [ ] 15. Add caching for recently parsed documents (optional)
- [ ] 16. Add error handling for S3 download failures
- [ ] 17. Add error handling for parsing failures

### Parser Router
- [ ] 18. Create services/parser_service/router.py
- [ ] 19. Create APIRouter with prefix "/parse"
- [ ] 20. Implement POST /document/{document_id} endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Verify document exists
  - [ ] Verify document belongs to firm_id (firm-level isolation)
  - [ ] Call parse_document logic
  - [ ] Return 200 with parsed text
- [ ] 21. Implement POST /batch endpoint:
  - [ ] Accept firm_id (query param or header for MVP)
  - [ ] Validate all document IDs
  - [ ] Verify all documents exist and belong to firm_id (firm-level isolation)
  - [ ] Call parse_documents_batch logic
  - [ ] Return 200 with batch results
- [ ] 22. Add OpenAPI documentation

### Lambda Handler
- [ ] 23. Create services/parser_service/handler.py
- [ ] 24. Import router and create FastAPI app
- [ ] 25. Create parse handler function using Mangum
- [ ] 26. Create batch handler function using Mangum

---

## PR #10: AI Service - Backend (Part 1: OpenAI Integration)

### OpenAI Client Setup
- [ ] 1. Create services/ai_service/openai_client.py
- [ ] 2. Import OpenAI library
- [ ] 3. Initialize OpenAI client with API key from config
- [ ] 4. Create function to build generation prompt:
  - [ ] Accept template data
  - [ ] Accept list of parsed documents
  - [ ] Format into structured prompt
  - [ ] Include instructions for formatting output as HTML
- [ ] 5. Create function to call OpenAI API:
  - [ ] Use GPT-4 or GPT-3.5-turbo (configurable)
  - [ ] Set appropriate temperature
  - [ ] Set max_tokens
  - [ ] Handle streaming response (optional)
  - [ ] Return generated text
- [ ] 6. Add retry logic for rate limits
- [ ] 7. Add retry logic for transient failures
- [ ] 8. Add timeout handling
- [ ] 9. Add error handling for API errors
- [ ] 10. Add function to estimate token count
- [ ] 11. Add function to validate response format

### Prompt Engineering
- [ ] 12. Create services/ai_service/prompts.py
- [ ] 13. Define base system prompt for demand letter generation
- [ ] 14. Create function to build context from documents:
  - [ ] Format document text with labels
  - [ ] Add section separators
  - [ ] Truncate if needed to fit context window
- [ ] 15. Create function to build template instructions:
  - [ ] Include letterhead
  - [ ] Include section structure
  - [ ] Include opening/closing paragraphs
- [ ] 16. Create function to combine all prompt components
- [ ] 17. Add prompt for HTML formatting instructions
- [ ] 18. Add examples of expected output format

### AI Service Schemas
- [ ] 19. Create services/ai_service/schemas.py
- [ ] 20. Define GenerateRequest schema:
  - [ ] template_id (UUID)
  - [ ] document_ids (list of UUIDs, max 5)
  - [ ] title (string, optional)
- [ ] 21. Define GenerateResponse schema:
  - [ ] letter_id (UUID)
  - [ ] content (HTML string)
  - [ ] status (draft)
- [ ] 22. Add validation for document count (max 5)

