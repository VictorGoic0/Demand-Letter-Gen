# Technical Context: Demand Letter Generator

## Technology Stack

### Webapp

**Core Framework:**
- React 18.3.1
- Vite 7.1.7 (build tool)
- React Router DOM 7.9.5

**UI & Styling:**
- Tailwind CSS 3.4.17
- shadcn/ui components
- Radix UI primitives:
  - @radix-ui/react-checkbox 1.3.3
  - @radix-ui/react-dialog 1.1.15
  - @radix-ui/react-slot 1.2.4
  - @radix-ui/react-switch 1.2.6
- lucide-react 0.552.0 (icons)
- class-variance-authority 0.7.1
- clsx 2.1.1
- tailwind-merge 3.3.1
- tailwindcss-animate 1.0.7

**Additional Libraries:**
- axios 1.13.2 (HTTP client)
- react-markdown 10.1.0 (formatted text display)

**Development Tools:**
- TypeScript (recommended but optional)
- oxlint (with `oxlint-plugin-eslint`, type-aware via `oxlint-tsgolint` when `typeAware` is enabled in `.oxlintrc.json`)
- Autoprefixer 10.4.20
- PostCSS 8.4.47
- @vitejs/plugin-react 5.0.4

### API

**Core:**
- Python 3.11
- FastAPI (latest stable version)
- Pydantic 2.5.0+ (data validation)

**Key Dependencies:**
```python
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.23
pydantic>=2.5.0
pydantic-settings>=2.1.0  # BaseSettings for configuration management
python-dotenv>=1.0.0
boto3>=1.29.7  # AWS SDK
openai>=1.0.0  # OpenAI API client
python-docx>=1.0.0  # .docx generation
pypdf>=3.0.0  # PDF parsing
psycopg2-binary>=2.9.0  # PostgreSQL driver
alembic>=1.12.0  # Database migrations
```

### Infrastructure

**Local / deployment:**
- **Docker Compose** (`api/docker-compose.yml`): PostgreSQL 15 + API (uvicorn with reload in dev)
- **Dockerfile** (`api/Dockerfile`): production-style API image (uvicorn, no reload by default)

**AWS (optional for app features):**
- **S3:** Document storage (PDFs and .docx files)
- **IAM / credentials:** Explicit keys via env or instance/task role via boto3 default chain

**External APIs:**
- **OpenAI API:** GPT-4 or GPT-3.5-turbo for letter generation

## Development Environment

**Documentation:** Guides, PRD, task lists, S3 docs, Docker local setup (`docs/docker-local-setup.md`), and Lambda deployment guide live under **`docs/`**. The Cursor memory bank stays at **`memory-bank/`** (repository root).

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (local venv under `api/.venv` — create with `python3 -m venv .venv`, install `requirements.txt` + `requirements-dev.txt`; not committed, listed in `.gitignore`; full API setup in `api/README.md`)
- Node.js 18+ (for webapp)

### Local Development Setup

**Docker Compose Services:**
- PostgreSQL 15 (port 5432)
- API FastAPI (port 8000)
- Webapp Vite dev server (port 5173)

**Utility Scripts:**
- Located in `api/scripts/` directory:
  - `check_*.py` - Table check scripts (firm, user, document, template, letter, letter_document) - returns first 5 results
  - `seed_*.py` - Seed scripts (test_firm, test_users)
  - `test_*.py` - Test scripts (db_connection, upload_document_api)
- Alembic shell wrappers in `api/scripts/`:
  - `migrate-up.sh` - Run `alembic upgrade head`
  - `migrate-down.sh` - Run `alembic downgrade -1`
  - `migrate-create.sh` - Create new migration with message
- Start stack: `cd api && docker compose up` (see `api/README.md`, `docs/docker-local-setup.md`); stop with `docker compose down`
- All scripts use `.env` for configuration

**Environment Variables:**

API (.env):
```
# Application
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=demand_letters
DB_USER=dev_user
DB_PASSWORD=dev_password

# AWS
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<key>
AWS_REGION=us-east-2
AWS_S3_BUCKET_DOCUMENTS=goico-demand-letters-documents-dev
AWS_S3_BUCKET_EXPORTS=goico-demand-letters-exports-dev

# OpenAI
OPENAI_API_KEY=<key>
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# CORS (optional, defaults to allow all)
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

Webapp (.env):
```
VITE_API_URL=http://localhost:8000
```

### Database

**PostgreSQL 15** with schema:
- firms
- users
- documents
- letter_templates
- generated_letters
- letter_source_documents (junction table)

**Migrations:** Alembic for schema versioning

## Deployment Architecture

### Lambda Configuration

**Runtime:** Python 3.11  
**Memory:** 512MB - 1GB per service  
**Timeout:** 
- Standard operations: 30 seconds
- AI generation: 60 seconds

**Lambda Layers:**
- Common dependencies layer (fastapi, sqlalchemy, boto3, pydantic)
- Service-specific code in each Lambda

### Serverless Framework

**Configuration:** Environment variables and `api/.env` (see `api/.env.example`, `shared/config.py`)

**Key Settings:**
- Service name: demand-letter-generator
- Provider: AWS
- Region: us-east-2 (configurable)
- Runtime: python3.11
- CORS enabled for all endpoints
- Lambda layers for shared dependencies
- Package optimization (excludes tests, docs, cache files)

**Functions:** Each service endpoint as separate Lambda function

**Handler Structure:**
- `handlers/` directory with base handler utility
- Mangum adapter for FastAPI → Lambda conversion
- Example handlers for each service (document, template, letter)
- Comprehensive handler pattern documentation

**Local Development:**
- `serverless-offline` plugin for local Lambda/API Gateway emulation
- Runs on port 3000 (configurable)
- Full request/response transformation support

### API Gateway

- REST API with HTTP endpoints
- CORS configuration
- Request/response transformation
- Error handling

### S3 Buckets

**Buckets Created:**
- `goico-demand-letters-documents-dev` (us-east-2) - Uploaded PDFs
- `goico-demand-letters-exports-dev` (us-east-2) - Generated .docx files

**Configuration:**
- Encryption at rest: AES256 (both buckets)
- Versioning: Enabled (both buckets)
- Public access: Blocked for documents bucket, allowed for exports bucket (presigned URLs)
- Presigned URLs: 1 hour expiration for downloads
- Region: us-east-2

**S3 Client:**
- Location: `api/shared/s3_client.py`
- Features: Upload, download, delete, presigned URL generation, bucket existence check, file listing
- Singleton pattern: `get_s3_client()` for easy access
- Error handling: Comprehensive exception handling for all operations

**Shared Utilities:**
- Location: `api/shared/`
- `config.py`: Pydantic BaseSettings with nested configs (Database, AWS, OpenAI, CORS)
- `exceptions.py`: Custom exception classes and FastAPI exception handlers
- `schemas/common.py`: Common API response schemas (SuccessResponse, ErrorResponse, PaginationParams, PaginatedResponse)
- `utils.py`: Utility functions (UUID generation, datetime formatting, file size formatting, filename/HTML sanitization)

### RDS

**PostgreSQL 15** instance:
- Automated backups
- Point-in-time recovery
- Encryption at rest
- Connection pooling via SQLAlchemy

## Build & Deployment

### Webapp build

```bash
cd webapp
npm install
npm run build
# Output: dist/ directory
```

**Deployment:** Static files to S3 + CloudFront

### API build

**Local Development:**
```bash
# Start Docker services
cd api
npm run start

# Run migrations (if needed)
./scripts/migrate-up.sh

# API auto-reloads via docker-compose (uvicorn --reload)
# Or run manually:
pip install -r requirements.txt
uvicorn main:app --reload
```

**Lambda Deployment:**
```bash
# Using Serverless Framework
cd api
serverless deploy
```

**Lambda Build Process:**
1. Install dependencies
2. Copy service code
3. Remove unnecessary files (tests, docs, __pycache__)
4. Package for Lambda
5. Deploy via Serverless Framework

## External Integrations

### OpenAI API

**Usage:**
- Model: GPT-4 (in `shared/config.py` - currently "gpt-4")
- Temperature: 0.7 (in `shared/config.py`)
- Purpose: Generate demand letter text
- Authentication: API key from environment variable `OPENAI_API_KEY`
- Error Handling: Retry logic for rate limits and transient failures

**Note:** Model and temperature are in `shared/config.py` for easier development iteration. These can be adjusted directly in code as needed.

**Prompt Engineering:**
- System prompt for legal writing style
- Template structure injection
- Document context formatting
- HTML output formatting instructions

### AWS Services

**S3:**
- boto3 client for operations (via `shared/s3_client.py`)
- Presigned URL generation (GET, PUT, DELETE methods supported)
- File upload/download (from file path or file object)
- Error handling for network issues
- Bucket existence validation
- File listing with prefix filtering
- Metadata management

**RDS:**
- SQLAlchemy ORM
- Connection pooling
- Transaction management
- Query optimization with indexes

## Development Workflow

### Local Development

1. Start Docker Compose: `npm run start` (or `docker-compose up -d`)
2. Run migrations: `./scripts/migrate-up.sh` (or `alembic upgrade head`)
3. API auto-reloads on code changes (via docker-compose uvicorn --reload)
4. Webapp hot-reloads on code changes
5. Access:
   - Webapp: http://localhost:5173
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health (returns database and S3 status)
6. Check database tables: `python scripts/check_*.py` (returns first 5 results)
7. Stop services: `npm run end` (or `docker-compose down`)
8. Restart services: `npm run restart` (or `docker-compose restart`)

### Testing

**API:**
- pytest for unit and integration tests
- Test database with transactions
- Mocked S3 and OpenAI for tests
- Target: >80% code coverage

**Webapp:**
- Vitest for unit tests
- React Testing Library for component tests
- Mocked API calls
- Integration tests for user flows

### Code Quality

**API:**
- Ruff (`ruff check`, `ruff format`) per `api/pyproject.toml`; run from activated `api/.venv` or use `npm run lint` / `lint:fix` / `format` in `api/`
- Type hints (Python)
- Pydantic v2 models for validation (field_validator, json_schema_extra)
- Pydantic BaseSettings (from pydantic-settings) for configuration
- SQLAlchemy models for database
- Error handling with custom exceptions and FastAPI handlers
- Common schemas for API responses (SuccessResponse, ErrorResponse, PaginatedResponse)
- Utility functions for common operations (UUID generation, datetime formatting, file size, sanitization)

**Webapp:**
- TypeScript (optional but recommended)
- oxlint for linting (`npm run lint`, `npm run lint:fix`)
- Component-based architecture
- Custom hooks for API calls

## Performance Considerations

### API
- Database query optimization (indexes)
- Connection pooling
- Lambda cold start mitigation (provisioned concurrency if needed)
- S3 upload/download optimization

### Webapp
- Code splitting
- Lazy loading for routes
- Image optimization
- Bundle size optimization

### API Response Times
- Standard operations: < 2 seconds
- AI generation: < 30 seconds
- File uploads: Progress indication for large files

## Security Considerations

### Authentication
- JWT tokens
- Token expiration
- Secure token storage (localStorage with HTTPS)

### Authorization
- Firm-level access control
- User role management
- API endpoint protection

### Data Protection
- Encryption in transit (HTTPS)
- Encryption at rest (S3, RDS)
- Presigned URLs with expiration
- No sensitive data in logs

### Compliance
- Legal industry data privacy requirements
- Attorney-client privilege considerations
- Audit logging
- Data retention policies

## Monitoring & Logging

### CloudWatch
- Lambda function logs
- API Gateway logs
- Error tracking
- Performance metrics

### Alerts
- High error rates
- High latency
- Database connection issues
- S3 upload failures

## Known Technical Constraints

1. **PDF Parsing:** Only text-based PDFs (no OCR in MVP)
2. **File Size:** 50MB limit per document
3. **Document Count:** Maximum 5 documents per letter generation
4. **Export Format:** .docx only (no PDF export in MVP)
5. **Lambda Timeout:** 60 seconds max for AI generation
6. **OpenAI Rate Limits:** Retry logic handles rate limits

