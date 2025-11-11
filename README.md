# Demand Letter Generator

**Organization:** 
**Project ID:** DLG_2025_001  
**Status:** MVP Development

## Overview

The Demand Letter Generator is an AI-driven solution designed to streamline the creation of demand letters for law firms. By leveraging OpenAI's models to automate the drafting of these documents, this tool aims to significantly reduce the time attorneys spend on this task, increasing efficiency and productivity.

## Features

- **Document Management:** Upload and manage source documents (PDFs) including medical records, police reports, and other supporting materials
- **Template Management:** Create and manage firm-specific letter templates with customizable sections and boilerplate text
- **AI-Powered Generation:** Automatically generate draft demand letters from selected source documents using OpenAI
- **Letter Editing:** View and edit generated letters with a rich text editor before finalization
- **Export Functionality:** Finalize and export letters as .docx files for sharing with clients or opposing counsel
- **Letter Library:** View, edit, and re-export previously generated letters

## Technology Stack

### Frontend
- React 18.3.1
- Vite 7.1.7
- Tailwind CSS 3.4.17
- shadcn/ui components
- React Router DOM 7.9.5

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy 2.0.23+
- PostgreSQL 15
- OpenAI API

### Infrastructure
- AWS Lambda (serverless functions)
- AWS S3 (document storage)
- AWS RDS (PostgreSQL database)
- API Gateway
- CloudWatch

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11
- Node.js 18+
- AWS Account (for production deployment)
- OpenAI API Key

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Demand-Letter-Gen
   ```

2. **Set up environment variables**

   Backend (create `backend/.env`):
   ```env
   DB_HOST=postgres
   DB_NAME=demand_letters
   DB_USER=dev_user
   DB_PASSWORD=dev_password
   OPENAI_API_KEY=your_openai_key
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_REGION=us-east-2
   S3_BUCKET_DOCUMENTS=your_documents_bucket
   S3_BUCKET_EXPORTS=your_exports_bucket
   ```

   Frontend (create `frontend/.env`):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **Start services with Docker Compose**
   ```bash
   cd backend
   docker-compose up
   ```

4. **Run database migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Test database connection and schema** (optional)
   
   **Option A: Run from host (requires venv with dependencies):**
   ```bash
   cd backend
   source venv/bin/activate  # If using venv
   python test_db.py
   ```
   
   **Option B: Run from Docker container (dependencies already installed):**
   ```bash
   cd backend
   docker-compose exec backend python test_db.py
   ```
   
   This script will verify:
   - Database connection
   - All tables exist
   - Table columns are correct
   - Indexes are created
   - Foreign key constraints
   - Basic CRUD operations

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Workflow

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Project Structure

```
.
├── backend/              # Python FastAPI backend
│   ├── services/        # Service modules (document, template, parser, AI, letter)
│   ├── shared/          # Shared utilities (database, S3, config)
│   ├── main.py          # Local development entry point
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   └── utils/       # Utility functions
│   └── package.json     # Node dependencies
├── memory-bank/         # Project documentation and context
└── backend/
    └── docker-compose.yml   # Local development setup
```

## Architecture

The application follows a service-oriented architecture with AWS Lambda functions:

- **Document Service:** Handles document uploads and management
- **Template Service:** Manages letter templates
- **Parser Service:** Extracts text from PDF documents
- **AI Service:** Generates demand letters using OpenAI
- **Letter Service:** Manages generated letters and .docx export

Each service is deployed as a separate Lambda function but shares common dependencies through Lambda Layers.

## Database Schema

The application uses PostgreSQL with the following main tables:
- `firms` - Law firm information
- `users` - User accounts
- `documents` - Uploaded source documents
- `letter_templates` - Firm-specific templates
- `generated_letters` - Generated demand letters
- `letter_source_documents` - Junction table linking letters to source documents

## Database Migrations

The project uses Alembic for database schema versioning and migrations.

### Running Migrations

**Apply all pending migrations:**
```bash
cd backend
alembic upgrade head
```

**Apply migrations to a specific revision:**
```bash
alembic upgrade <revision_id>
```

**Rollback to previous migration:**
```bash
alembic downgrade -1
```

**Rollback to a specific revision:**
```bash
alembic downgrade <revision_id>
```

**View current migration status:**
```bash
alembic current
```

**View migration history:**
```bash
alembic history
```

### Creating New Migrations

**Auto-generate migration from model changes:**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

**Create empty migration (manual):**
```bash
alembic revision -m "Description of changes"
```

### Migration Workflow

1. Make changes to models in `backend/shared/models/`
2. Generate migration: `alembic revision --autogenerate -m "your message"`
3. Review the generated migration file in `backend/alembic/versions/`
4. Apply migration: `alembic upgrade head`
5. Test the changes

### Important Notes

- Always review auto-generated migrations before applying them
- Test migrations on a development database first
- Never edit existing migration files that have been applied to production
- Create new migrations for schema changes instead of modifying old ones
- The database URL is configured from environment variables (see `backend/alembic/env.py`)

## AWS Infrastructure Setup

### Overview

The application uses several AWS services:
- **S3:** Document storage (uploads) and exports (generated letters)
- **RDS:** PostgreSQL database for application data
- **Lambda:** Serverless function execution
- **API Gateway:** HTTP API endpoints
- **CloudWatch:** Logging and monitoring

### Initial Setup

For detailed AWS infrastructure setup instructions, see:
- [AWS Setup Guide](docs/aws-setup.md) - Comprehensive guide for IAM, S3, RDS, and Lambda configuration
- [IAM Policies](terraform/iam-policies/) - JSON policy examples for Terraform/CloudFormation

### Quick Start

1. **Create S3 Buckets:**
   ```bash
   AWS_REGION="us-east-1"
   ENV="dev"
   
   # Documents bucket
   aws s3api create-bucket \
     --bucket demand-letters-documents-${ENV} \
     --region ${AWS_REGION}
   
   # Exports bucket
   aws s3api create-bucket \
     --bucket demand-letters-exports-${ENV} \
     --region ${AWS_REGION}
   ```

2. **Create RDS Instance:**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier demand-letters-db-${ENV} \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --engine-version 15.4 \
     --master-username demand_admin \
     --master-user-password YOUR_PASSWORD \
     --allocated-storage 20 \
     --storage-encrypted
   ```

3. **Configure IAM Policies:**
   - Create Lambda execution role with policies from `terraform/iam-policies/`
   - Attach S3 access policy
   - Attach RDS access policy
   - Attach CloudWatch logs policy

4. **Update Environment Variables:**
   - Set AWS credentials and bucket names in `backend/.env`
   - Configure database connection details

For complete setup instructions, troubleshooting, and security best practices, refer to the [AWS Setup Guide](docs/aws-setup.md).

## Deployment

### Production Deployment

Deployment is handled via the Serverless Framework:

```bash
cd backend
serverless deploy
```

See `backend/serverless.yml` for configuration details.

### Environment Setup

Ensure all required environment variables are configured in your AWS Lambda environment or `.env` file for local development.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please open an issue in the repository or contact the development team.

## Roadmap

### MVP (Current Phase)
- [x] Project setup and infrastructure
- [ ] Document upload and management
- [ ] Template management
- [ ] AI-powered letter generation
- [ ] Letter editing and finalization
- [ ] .docx export functionality

### Post-MVP Features
- OCR for scanned documents
- Real-time collaboration
- Advanced template features
- Analytics and insights
- Mobile applications

## Acknowledgments

- Built with React, FastAPI, and AWS Serverless technologies
- Powered by OpenAI for AI-driven letter generation

