# Demand Letter Generator - PR Implementation List
# Part 1: Setup and Infrastructure

## PR #1: Project Initialization and Repository Setup

### Frontend Setup
- [ ] 1. Initialize Vite project with React 18.3.1
- [ ] 2. Configure TypeScript (tsconfig.json)
- [ ] 3. Install core dependencies:
  - [ ] react@18.3.1
  - [ ] react-dom@18.3.1
  - [ ] react-router-dom@7.9.5
  - [ ] axios@1.13.2
- [ ] 4. Install Tailwind CSS 3.4.17 and configure
- [ ] 5. Install PostCSS 8.4.47 and Autoprefixer 10.4.20
- [ ] 6. Install shadcn/ui dependencies:
  - [ ] @radix-ui/react-checkbox@1.3.3
  - [ ] @radix-ui/react-dialog@1.1.15
  - [ ] @radix-ui/react-slot@1.2.4
  - [ ] @radix-ui/react-switch@1.2.6
  - [ ] class-variance-authority@0.7.1
  - [ ] clsx@2.1.1
  - [ ] tailwind-merge@3.3.1
  - [ ] tailwindcss-animate@1.0.7
- [ ] 7. Install additional UI libraries:
  - [ ] lucide-react@0.552.0
  - [ ] react-markdown@10.1.0
  - [ ] recharts@3.3.0
- [ ] 8. Install dev dependencies:
  - [ ] @vitejs/plugin-react@5.0.4
  - [ ] eslint@9.36.0
  - [ ] eslint-plugin-react-hooks@5.2.0
  - [ ] eslint-plugin-react-refresh@0.4.22
  - [ ] globals@16.4.0
- [ ] 9. Configure Tailwind config file
- [ ] 10. Configure PostCSS config file
- [ ] 11. Set up ESLint configuration
- [ ] 12. Create base folder structure (src, components, pages, lib, hooks, utils)
- [ ] 13. Create index.css with Tailwind directives
- [ ] 14. Set up vite.config.ts with path aliases
- [ ] 15. Create .env.example with VITE_API_URL
- [ ] 16. Add .gitignore for frontend

### Backend Setup
- [ ] 17. Initialize Python project with requirements.txt
- [ ] 18. Add core dependencies to requirements.txt:
  - [ ] fastapi>=0.104.1
  - [ ] uvicorn[standard]>=0.24.0
  - [ ] mangum>=0.17.0
  - [ ] sqlalchemy>=2.0.23
  - [ ] pydantic>=2.5.0
  - [ ] python-dotenv>=1.0.0
  - [ ] boto3>=1.29.7
  - [ ] openai>=1.0.0
  - [ ] python-docx>=1.0.0
  - [ ] pypdf>=3.0.0
  - [ ] psycopg2-binary>=2.9.0
  - [ ] alembic>=1.12.0
- [ ] 19. Create backend folder structure:
  - [ ] shared/
  - [ ] services/document_service/
  - [ ] services/template_service/
  - [ ] services/parser_service/
  - [ ] services/ai_service/
  - [ ] services/letter_service/
- [ ] 20. Create main.py for local development
- [ ] 21. Create shared/__init__.py
- [ ] 22. Create .env.example with all required variables
- [ ] 23. Add .gitignore for Python

### Repository Root
- [ ] 24. Create root README.md with project overview
- [ ] 25. Create root .gitignore
- [ ] 26. Add LICENSE file
- [ ] 27. Create CONTRIBUTING.md

---

## PR #2: Docker Configuration for Local Development

### Docker Compose Setup
- [ ] 1. Create docker-compose.yml in root
- [ ] 2. Configure PostgreSQL service:
  - [ ] Set image to postgres:15
  - [ ] Configure environment variables
  - [ ] Set up port mapping (5432:5432)
  - [ ] Configure volume for data persistence
- [ ] 3. Configure backend service:
  - [ ] Reference backend Dockerfile
  - [ ] Set up volume mounts for hot reload
  - [ ] Configure port mapping (8000:8000)
  - [ ] Set environment variables
  - [ ] Add depends_on for postgres
- [ ] 4. Configure frontend service:
  - [ ] Reference frontend Dockerfile
  - [ ] Set up volume mounts for hot reload
  - [ ] Configure port mapping (5173:5173)
  - [ ] Set environment variables
  - [ ] Add node_modules volume

### Backend Dockerfile (Development)
- [ ] 5. Create backend/Dockerfile
- [ ] 6. Use python:3.11-slim as base image
- [ ] 7. Set working directory to /app
- [ ] 8. Copy requirements.txt
- [ ] 9. Install dependencies with pip
- [ ] 10. Copy application code
- [ ] 11. Set CMD for uvicorn with reload

### Frontend Dockerfile (Development)
- [ ] 12. Create frontend/Dockerfile
- [ ] 13. Use node:18-alpine as base image
- [ ] 14. Set working directory to /app
- [ ] 15. Copy package.json and package-lock.json
- [ ] 16. Run npm install
- [ ] 17. Copy application code
- [ ] 18. Expose port 5173
- [ ] 19. Set CMD for npm run dev

### Lambda Build Dockerfile (Production)
- [ ] 20. Create backend/Dockerfile.lambda
- [ ] 21. Create multi-stage build with builder stage
- [ ] 22. Use public.ecr.aws/lambda/python:3.11 as base
- [ ] 23. Install dependencies in builder stage
- [ ] 24. Add cleanup commands to remove tests, docs, __pycache__
- [ ] 25. Add commands to remove .pyc, .pyo files
- [ ] 26. Add commands to remove .dist-info directories
- [ ] 27. Copy application code
- [ ] 28. Create runtime stage from lambda base image
- [ ] 29. Copy artifacts from builder stage
- [ ] 30. Set default CMD (will be overridden per function)

### Docker Documentation
- [ ] 31. Create docker/README.md with setup instructions
- [ ] 32. Document how to start services
- [ ] 33. Document how to stop services
- [ ] 34. Document how to view logs
- [ ] 35. Document how to rebuild containers
- [ ] 36. Add troubleshooting section

---

## PR #3: Database Schema and Migrations

### Database Configuration
- [ ] 1. Create shared/database.py
- [ ] 2. Set up SQLAlchemy engine with connection pooling
- [ ] 3. Create SessionLocal factory
- [ ] 4. Create Base declarative base
- [ ] 5. Create get_db() dependency function
- [ ] 6. Add database URL configuration from environment

### Database Models
- [ ] 7. Create shared/models/__init__.py
- [ ] 8. Create shared/models/firm.py with Firm model:
  - [ ] id (UUID, primary key)
  - [ ] name (VARCHAR)
  - [ ] created_at (TIMESTAMP)
  - [ ] updated_at (TIMESTAMP)
- [ ] 9. Create shared/models/user.py with User model:
  - [ ] id (UUID, primary key)
  - [ ] firm_id (UUID, foreign key)
  - [ ] email (VARCHAR, unique)
  - [ ] name (VARCHAR)
  - [ ] role (VARCHAR)
  - [ ] created_at (TIMESTAMP)
  - [ ] updated_at (TIMESTAMP)
- [ ] 10. Create shared/models/document.py with Document model:
  - [ ] id (UUID, primary key)
  - [ ] firm_id (UUID, foreign key)
  - [ ] uploaded_by (UUID, foreign key)
  - [ ] filename (VARCHAR)
  - [ ] file_size (BIGINT)
  - [ ] s3_key (VARCHAR)
  - [ ] mime_type (VARCHAR)
  - [ ] uploaded_at (TIMESTAMP)
- [ ] 11. Create shared/models/template.py with LetterTemplate model:
  - [ ] id (UUID, primary key)
  - [ ] firm_id (UUID, foreign key)
  - [ ] name (VARCHAR)
  - [ ] letterhead_text (TEXT)
  - [ ] opening_paragraph (TEXT)
  - [ ] closing_paragraph (TEXT)
  - [ ] sections (JSONB)
  - [ ] is_default (BOOLEAN)
  - [ ] created_by (UUID, foreign key)
  - [ ] created_at (TIMESTAMP)
  - [ ] updated_at (TIMESTAMP)
- [ ] 12. Create shared/models/letter.py with GeneratedLetter model:
  - [ ] id (UUID, primary key)
  - [ ] firm_id (UUID, foreign key)
  - [ ] created_by (UUID, foreign key)
  - [ ] title (VARCHAR)
  - [ ] content (TEXT)
  - [ ] status (VARCHAR)
  - [ ] template_id (UUID, foreign key)
  - [ ] docx_s3_key (VARCHAR, nullable)
  - [ ] created_at (TIMESTAMP)
  - [ ] updated_at (TIMESTAMP)
- [ ] 13. Create shared/models/letter_document.py with LetterSourceDocument model:
  - [ ] letter_id (UUID, foreign key, primary key)
  - [ ] document_id (UUID, foreign key, primary key)

### Alembic Setup
- [ ] 14. Initialize Alembic in backend directory
- [ ] 15. Configure alembic.ini with database URL
- [ ] 16. Update env.py to import models
- [ ] 17. Configure env.py for async if needed
- [ ] 18. Create initial migration with all tables
- [ ] 19. Add indexes in migration:
  - [ ] idx_documents_firm_id
  - [ ] idx_documents_uploaded_at
  - [ ] idx_letters_firm_id
  - [ ] idx_letters_created_at
  - [ ] idx_letters_status
- [ ] 20. Test migration up
- [ ] 21. Test migration down
- [ ] 22. Add migration instructions to README

### Database Utilities
- [ ] 23. Create shared/db_utils.py
- [ ] 24. Add function to check database connection
- [ ] 25. Add function to create all tables
- [ ] 26. Add function to drop all tables (dev only)
- [ ] 27. Create database initialization script

---

## PR #4: AWS Infrastructure Setup

### S3 Configuration
- [ ] 1. Create shared/s3_client.py
- [ ] 2. Initialize boto3 S3 client with credentials from env
- [ ] 3. Create function to upload file to S3
- [ ] 4. Create function to download file from S3
- [ ] 5. Create function to delete file from S3
- [ ] 6. Create function to generate presigned URL
- [ ] 7. Add error handling for all S3 operations
- [ ] 8. Add function to check if bucket exists
- [ ] 9. Add function to list files in bucket (for debugging)
- [ ] 10. Create S3 bucket naming configuration

### IAM Configuration Documentation
- [ ] 11. Create docs/aws-setup.md
- [ ] 12. Document IAM policy for S3 access
- [ ] 13. Document IAM policy for Lambda execution
- [ ] 14. Document IAM policy for RDS access
- [ ] 15. Document IAM policy for CloudWatch logs
- [ ] 16. Create terraform/IAM policy JSON examples

### Environment Configuration
- [ ] 17. Update backend .env.example with AWS variables:
  - [ ] AWS_ACCESS_KEY_ID
  - [ ] AWS_SECRET_ACCESS_KEY
  - [ ] AWS_REGION
  - [ ] S3_BUCKET_DOCUMENTS
  - [ ] S3_BUCKET_EXPORTS
- [ ] 18. Create shared/config.py for centralized config
- [ ] 19. Add validation for required environment variables
- [ ] 20. Add function to load and validate config on startup

### RDS Setup Documentation
- [ ] 21. Document RDS instance creation steps
- [ ] 22. Document security group configuration
- [ ] 23. Document connection string format
- [ ] 24. Add RDS connection troubleshooting guide
- [ ] 25. Document backup configuration recommendations

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

