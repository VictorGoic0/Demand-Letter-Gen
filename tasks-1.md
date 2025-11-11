# Demand Letter Generator - PR Implementation List
# Part 1: Setup and Infrastructure

## PR #1: Project Initialization and Repository Setup

### Frontend Setup
- [x] 1. Initialize Vite project with React 18.3.1
- [ ] 2. Configure TypeScript (tsconfig.json) - SKIPPED: Using JavaScript with jsconfig.json
- [x] 3. Install core dependencies:
  - [x] react@18.3.1
  - [x] react-dom@18.3.1
  - [x] react-router-dom@7.9.5
  - [x] axios@1.13.2
- [x] 4. Install Tailwind CSS 3.4.17 and configure
- [x] 5. Install PostCSS 8.4.47 and Autoprefixer 10.4.20
- [x] 6. Install shadcn/ui dependencies:
  - [x] @radix-ui/react-checkbox@1.3.3
  - [x] @radix-ui/react-dialog@1.1.15
  - [x] @radix-ui/react-slot@1.2.4
  - [x] @radix-ui/react-switch@1.2.6
  - [x] class-variance-authority@0.7.1
  - [x] clsx@2.1.1
  - [x] tailwind-merge@3.3.1
  - [x] tailwindcss-animate@1.0.7
- [x] 7. Install additional UI libraries:
  - [x] lucide-react@0.552.0
  - [x] react-markdown@10.1.0
  - [x] recharts@3.3.0
- [x] 8. Install dev dependencies:
  - [x] @vitejs/plugin-react@5.0.4
  - [x] eslint@9.36.0
  - [x] eslint-plugin-react-hooks@5.2.0
  - [x] eslint-plugin-react-refresh@0.4.22
  - [x] globals@16.4.0
- [x] 9. Configure Tailwind config file
- [x] 10. Configure PostCSS config file
- [x] 11. Set up ESLint configuration
- [x] 12. Create base folder structure (src, components, pages, lib, hooks, utils)
- [x] 13. Create index.css with Tailwind directives
- [x] 14. Set up vite.config.ts with path aliases
- [x] 15. Create .env.example with VITE_API_URL
- [x] 16. Add .gitignore for frontend

### Backend Setup
- [x] 17. Initialize Python project with requirements.txt
- [x] 18. Add core dependencies to requirements.txt:
  - [x] fastapi>=0.104.1
  - [x] uvicorn[standard]>=0.24.0
  - [x] mangum>=0.17.0
  - [x] sqlalchemy>=2.0.23
  - [x] pydantic>=2.5.0
  - [x] python-dotenv>=1.0.0
  - [x] boto3>=1.29.7
  - [x] openai>=1.0.0
  - [x] python-docx>=1.0.0
  - [x] pypdf>=3.0.0
  - [x] psycopg2-binary>=2.9.0
  - [x] alembic>=1.12.0
- [x] 19. Create backend folder structure:
  - [x] shared/
  - [x] services/document_service/
  - [x] services/template_service/
  - [x] services/parser_service/
  - [x] services/ai_service/
  - [x] services/letter_service/
- [x] 20. Create main.py for local development
- [x] 21. Create shared/__init__.py
- [x] 22. Create .env.example with all required variables
- [ ] 23. Add .gitignore for Python - SKIPPED: Using root .gitignore

### Repository Root
- [x] 24. Create root README.md with project overview
- [x] 25. Create root .gitignore
- [x] 26. Add LICENSE file
- [x] 27. Create CONTRIBUTING.md

---

## PR #2: Docker Configuration for Local Development

### Docker Compose Setup
- [x] 1. Create docker-compose.yml in backend directory
- [x] 2. Configure PostgreSQL service:
  - [x] Set image to postgres:15
  - [x] Configure environment variables
  - [x] Set up port mapping (5432:5432)
  - [x] Configure volume for data persistence
- [x] 3. Configure backend service:
  - [x] Reference backend Dockerfile
  - [x] Set up volume mounts for hot reload
  - [x] Configure port mapping (8000:8000)
  - [x] Set environment variables
  - [x] Add depends_on for postgres

### Backend Dockerfile (Development)
- [x] 4. Create backend/Dockerfile
- [x] 5. Use python:3.11-slim as base image
- [x] 6. Set working directory to /app
- [x] 7. Copy requirements.txt
- [x] 8. Install dependencies with pip
- [x] 9. Copy application code
- [x] 10. Set CMD for uvicorn with reload

### Lambda Build Dockerfile (Production)
- [x] 11. Create backend/Dockerfile.lambda
- [x] 12. Create multi-stage build with builder stage
- [x] 13. Use public.ecr.aws/lambda/python:3.11 as base
- [x] 14. Install dependencies in builder stage
- [x] 15. Add cleanup commands to remove tests, docs, __pycache__
- [x] 16. Add commands to remove .pyc, .pyo files
- [x] 17. Add commands to remove .dist-info directories
- [x] 18. Copy application code
- [x] 19. Create runtime stage from lambda base image
- [x] 20. Copy artifacts from builder stage
- [x] 21. Set default CMD (will be overridden per function)

### Docker Documentation
- [x] 22. Create docker/README.md with setup instructions
- [x] 23. Document how to start services
- [x] 24. Document how to stop services
- [x] 25. Document how to view logs
- [x] 26. Document how to rebuild containers
- [x] 27. Add troubleshooting section

---

## PR #3: Database Schema and Migrations

### Database Configuration
- [x] 1. Create shared/database.py
- [x] 2. Set up SQLAlchemy engine with connection pooling
- [x] 3. Create SessionLocal factory
- [x] 4. Create Base declarative base
- [x] 5. Create get_db() dependency function
- [x] 6. Add database URL configuration from environment

### Database Models
- [x] 7. Create shared/models/__init__.py
- [x] 8. Create shared/models/firm.py with Firm model:
  - [x] id (UUID, primary key)
  - [x] name (VARCHAR)
  - [x] created_at (TIMESTAMP)
  - [x] updated_at (TIMESTAMP)
- [x] 9. Create shared/models/user.py with User model:
  - [x] id (UUID, primary key)
  - [x] firm_id (UUID, foreign key)
  - [x] email (VARCHAR, unique)
  - [x] name (VARCHAR)
  - [x] role (VARCHAR)
  - [x] created_at (TIMESTAMP)
  - [x] updated_at (TIMESTAMP)
- [x] 10. Create shared/models/document.py with Document model:
  - [x] id (UUID, primary key)
  - [x] firm_id (UUID, foreign key)
  - [x] uploaded_by (UUID, foreign key)
  - [x] filename (VARCHAR)
  - [x] file_size (BIGINT)
  - [x] s3_key (VARCHAR)
  - [x] mime_type (VARCHAR)
  - [x] uploaded_at (TIMESTAMP)
- [x] 11. Create shared/models/template.py with LetterTemplate model:
  - [x] id (UUID, primary key)
  - [x] firm_id (UUID, foreign key)
  - [x] name (VARCHAR)
  - [x] letterhead_text (TEXT)
  - [x] opening_paragraph (TEXT)
  - [x] closing_paragraph (TEXT)
  - [x] sections (JSONB)
  - [x] is_default (BOOLEAN)
  - [x] created_by (UUID, foreign key)
  - [x] created_at (TIMESTAMP)
  - [x] updated_at (TIMESTAMP)
- [x] 12. Create shared/models/letter.py with GeneratedLetter model:
  - [x] id (UUID, primary key)
  - [x] firm_id (UUID, foreign key)
  - [x] created_by (UUID, foreign key)
  - [x] title (VARCHAR)
  - [x] content (TEXT)
  - [x] status (VARCHAR)
  - [x] template_id (UUID, foreign key)
  - [x] docx_s3_key (VARCHAR, nullable)
  - [x] created_at (TIMESTAMP)
  - [x] updated_at (TIMESTAMP)
- [x] 13. Create shared/models/letter_document.py with LetterSourceDocument model:
  - [x] letter_id (UUID, foreign key, primary key)
  - [x] document_id (UUID, foreign key, primary key)

### Alembic Setup
- [x] 14. Initialize Alembic in backend directory
- [x] 15. Configure alembic.ini with database URL
- [x] 16. Update env.py to import models
- [x] 17. Configure env.py for async if needed
- [x] 18. Create initial migration with all tables
- [x] 19. Add indexes in migration:
  - [x] idx_documents_firm_id
  - [x] idx_documents_uploaded_at
  - [x] idx_letters_firm_id
  - [x] idx_letters_created_at
  - [x] idx_letters_status
- [ ] 20. Test migration up
- [ ] 21. Test migration down
- [x] 22. Add migration instructions to README

### Database Utilities
- [x] 23. Create shared/db_utils.py
- [x] 24. Add function to check database connection
- [x] 25. Add function to create all tables
- [x] 26. Add function to drop all tables (dev only)
- [x] 27. Create database initialization script

---

## PR #4: AWS Infrastructure Setup

### S3 Configuration
- [x] 1. Create shared/s3_client.py
- [x] 2. Initialize boto3 S3 client with credentials from env
- [x] 3. Create function to upload file to S3
- [x] 4. Create function to download file from S3
- [x] 5. Create function to delete file from S3
- [x] 6. Create function to generate presigned URL
- [x] 7. Add error handling for all S3 operations
- [x] 8. Add function to check if bucket exists
- [x] 9. Add function to list files in bucket (for debugging)
- [x] 10. Create S3 bucket naming configuration

### IAM Configuration Documentation
- [x] 11. Create docs/aws-setup.md
- [x] 12. Document IAM policy for S3 access
- [x] 13. Document IAM policy for Lambda execution
- [x] 14. Document IAM policy for RDS access
- [x] 15. Document IAM policy for CloudWatch logs
- [x] 16. Create terraform/IAM policy JSON examples

### Environment Configuration
- [x] 17. Update backend .env.example with AWS variables:
  - [x] AWS_ACCESS_KEY_ID
  - [x] AWS_SECRET_ACCESS_KEY
  - [x] AWS_REGION
  - [x] S3_BUCKET_DOCUMENTS
  - [x] S3_BUCKET_EXPORTS
- [x] 18. Create shared/config.py for centralized config
- [x] 19. Add validation for required environment variables
- [x] 20. Add function to load and validate config on startup

### RDS Setup Documentation
- [x] 21. Document RDS instance creation steps
- [x] 22. Document security group configuration
- [x] 23. Document connection string format
- [x] 24. Add RDS connection troubleshooting guide
- [x] 25. Document backup configuration recommendations

---

## PR #5: Serverless Framework Configuration

### Serverless.yml Setup
- [ ] 1. Create serverless.yml in backend directory
- [ ] 2. Configure service name
- [ ] 3. Configure provider section:
  - [ ] Set provider to aws
  - [ ] Set runtime to python3.11
  - [ ] Set region
  - [ ] Configure stage variable
- [ ] 4. Configure environment variables section
- [ ] 5. Configure package exclusions:
  - [ ] tests/**
  - [ ] docs/**
  - [ ] **/__pycache__/**
  - [ ] **/*.pyc
  - [ ] .git/**
  - [ ] .env
  - [ ] README.md
  - [ ] docker-compose.yml
  - [ ] node_modules/**
- [ ] 6. Configure Lambda layers section
- [ ] 7. Define commonDependencies layer with path

### Lambda Function Definitions
- [ ] 8. Define documentUpload function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (POST /documents/upload)
  - [ ] Set timeout to 30
  - [ ] Enable CORS
- [ ] 9. Define documentList function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (GET /documents)
  - [ ] Enable CORS
- [ ] 10. Define documentGet function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (GET /documents/{id})
  - [ ] Enable CORS
- [ ] 11. Define documentDelete function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (DELETE /documents/{id})
  - [ ] Enable CORS
- [ ] 12. Define templateCreate function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (POST /templates)
  - [ ] Enable CORS
- [ ] 13. Define templateList function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (GET /templates)
  - [ ] Enable CORS
- [ ] 14. Define templateGet function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (GET /templates/{id})
  - [ ] Enable CORS
- [ ] 15. Define templateUpdate function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (PUT /templates/{id})
  - [ ] Enable CORS
- [ ] 16. Define templateDelete function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (DELETE /templates/{id})
  - [ ] Enable CORS
- [ ] 17. Define generateLetter function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (POST /letters/generate)
  - [ ] Set timeout to 60
  - [ ] Enable CORS
- [ ] 18. Define letterList function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (GET /letters)
  - [ ] Enable CORS
- [ ] 19. Define letterGet function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (GET /letters/{id})
  - [ ] Enable CORS
- [ ] 20. Define letterUpdate function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (PUT /letters/{id})
  - [ ] Enable CORS
- [ ] 21. Define letterFinalize function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (POST /letters/{id}/finalize)
  - [ ] Set timeout to 30
  - [ ] Enable CORS
- [ ] 22. Define letterExport function:
  - [ ] Set handler path
  - [ ] Configure HTTP event (POST /letters/{id}/export)
  - [ ] Set timeout to 30
  - [ ] Enable CORS

### Deployment Scripts
- [ ] 23. Create deploy.sh script for deployment
- [ ] 24. Add commands to build Lambda layers
- [ ] 25. Add commands to run serverless deploy
- [ ] 26. Add error checking and rollback steps
- [ ] 27. Create deploy-dev.sh for development deployment
- [ ] 28. Create deploy-prod.sh for production deployment
- [ ] 29. Add deployment documentation to README

### Plugins and Additional Config
- [ ] 30. Add serverless-python-requirements plugin
- [ ] 31. Configure plugin for Lambda layer building
- [ ] 32. Add serverless-offline plugin for local testing
- [ ] 33. Configure API Gateway settings
- [ ] 34. Configure CloudWatch log retention
- [ ] 35. Add custom domain configuration (optional)

