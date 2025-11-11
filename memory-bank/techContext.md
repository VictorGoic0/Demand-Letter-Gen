# Technical Context: Demand Letter Generator

## Technology Stack

### Frontend

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
- ESLint 9.36.0
- Autoprefixer 10.4.20
- PostCSS 8.4.47
- @vitejs/plugin-react 5.0.4

### Backend

**Core:**
- Python 3.11
- FastAPI (latest stable version)
- Pydantic 2.5.0+ (data validation)

**Key Dependencies:**
```python
fastapi>=0.104.1
uvicorn[standard]>=0.24.0  # Local development only
mangum>=0.17.0  # FastAPI to Lambda adapter
sqlalchemy>=2.0.23
pydantic>=2.5.0
python-dotenv>=1.0.0
boto3>=1.29.7  # AWS SDK
openai>=1.0.0  # OpenAI API client
python-docx>=1.0.0  # .docx generation
pypdf>=3.0.0  # PDF parsing
psycopg2-binary>=2.9.0  # PostgreSQL driver
alembic>=1.12.0  # Database migrations
```

### Infrastructure

**AWS Services:**
- **Lambda:** Python 3.11 runtime, serverless compute
- **API Gateway:** HTTP endpoints for Lambda functions
- **S3:** Document storage (PDFs and .docx files)
- **RDS:** PostgreSQL 15 for relational database
- **CloudWatch:** Logging and monitoring
- **IAM:** Access control and permissions

**External APIs:**
- **OpenAI API:** GPT-4 or GPT-3.5-turbo for letter generation

## Development Environment

### Prerequisites
- Docker & Docker Compose
- Python 3.11
- Node.js 18+ (for frontend)

### Local Development Setup

**Docker Compose Services:**
- PostgreSQL 15 (port 5432)
- Backend FastAPI (port 8000)
- Frontend Vite dev server (port 5173)

**Utility Scripts:**
- Located in `backend/scripts/` directory
- `test_db.py` - Database connection and schema validation
- All scripts use `.env.local` for configuration

**Environment Variables:**

Backend (.env):
```
DB_HOST=postgres
DB_NAME=demand_letters
DB_USER=dev_user
DB_PASSWORD=dev_password
OPENAI_API_KEY=<key>
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<key>
AWS_REGION=us-east-2
S3_BUCKET_DOCUMENTS=goico-demand-letters-documents-dev
S3_BUCKET_EXPORTS=goico-demand-letters-exports-dev
```

Frontend (.env):
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

**Configuration:** `serverless.yml` in backend directory

**Key Settings:**
- Service name: demand-letter-generator
- Provider: AWS
- Region: us-east-2 (configurable)
- Runtime: python3.11
- CORS enabled for all endpoints

**Functions:** Each service endpoint as separate Lambda function

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
- Location: `backend/shared/s3_client.py`
- Features: Upload, download, delete, presigned URL generation, bucket existence check, file listing
- Singleton pattern: `get_s3_client()` for easy access
- Error handling: Comprehensive exception handling for all operations

### RDS

**PostgreSQL 15** instance:
- Automated backups
- Point-in-time recovery
- Encryption at rest
- Connection pooling via SQLAlchemy

## Build & Deployment

### Frontend Build

```bash
cd frontend
npm install
npm run build
# Output: dist/ directory
```

**Deployment:** Static files to S3 + CloudFront

### Backend Build

**Local Development:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Lambda Deployment:**
```bash
# Using Serverless Framework
cd backend
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
- Model: GPT-4 (hardcoded in `shared/config.py` - currently "gpt-4")
- Temperature: 0.7 (hardcoded in `shared/config.py`)
- Max Tokens: 2000 (hardcoded in `shared/config.py`)
- Purpose: Generate demand letter text
- Authentication: API key from environment variable `OPENAI_API_KEY`
- Error Handling: Retry logic for rate limits and transient failures

**Note:** Model, temperature, and max_tokens are hardcoded in the code for easier development iteration. These can be adjusted directly in `shared/config.py` as needed.

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

1. Start Docker Compose: `docker-compose up`
2. Run migrations: `alembic upgrade head`
3. Backend auto-reloads on code changes
4. Frontend hot-reloads on code changes
5. Access:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Testing

**Backend:**
- pytest for unit and integration tests
- Test database with transactions
- Mocked S3 and OpenAI for tests
- Target: >80% code coverage

**Frontend:**
- Vitest for unit tests
- React Testing Library for component tests
- Mocked API calls
- Integration tests for user flows

### Code Quality

**Backend:**
- Type hints (Python)
- Pydantic models for validation
- SQLAlchemy models for database
- Error handling with custom exceptions

**Frontend:**
- TypeScript (optional but recommended)
- ESLint for linting
- Component-based architecture
- Custom hooks for API calls

## Performance Considerations

### Backend
- Database query optimization (indexes)
- Connection pooling
- Lambda cold start mitigation (provisioned concurrency if needed)
- S3 upload/download optimization

### Frontend
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

