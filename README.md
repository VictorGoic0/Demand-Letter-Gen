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
- Docker / Docker Compose (local PostgreSQL + API)
- AWS S3 (document storage; optional local testing against real buckets)
- PostgreSQL 15

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

   API: create `api/.env` (full variable list and examples: **[api/README.md](api/README.md)**).

   Webapp (create `webapp/.env`):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **API: Docker, database, migrations, venv, and server**

   Follow **[api/README.md](api/README.md)** — virtualenv, `docker-compose`, `alembic upgrade head`, optional `test_db.py`, and `uvicorn` for local API.

4. **Access the application**
   - Webapp: http://localhost:5173
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Workflow

**Webapp:**
```bash
cd webapp
npm install
npm run dev
```

**API:** venv, install, run server, lint — see **[api/README.md](api/README.md)**.

## Project Structure

```
.
├── api/              # Python FastAPI API (see api/README.md)
│   ├── services/         # Service modules (document, template, parser, AI, letter)
│   ├── shared/           # Shared utilities (database, S3, config)
│   ├── main.py           # FastAPI application entrypoint
│   ├── docker-compose.yml
│   └── requirements.txt
├── webapp/             # React webapp
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── utils/
│   └── package.json
├── docs/                 # Guides, PRD, tasks, S3, Docker local setup, lambda deployment
│   ├── tasks/
│   ├── PRD.md
│   ├── docker-local-setup.md
│   ├── lambda-deployment.md
│   └── s3-*.md
└── memory-bank/          # Cursor memory bank (project state for AI)
```

## Architecture

The backend is organized as FastAPI **routers** under `api/services/` (document, template, parser, AI, letter, auth). A single **`main.py`** registers all routers and runs under **uvicorn** (locally or in Docker).

- **Document Service:** Document uploads and management
- **Template Service:** Letter templates
- **Parser Service:** PDF text extraction
- **AI Service:** Demand letter generation (OpenAI)
- **Letter Service:** Generated letters and .docx export

## Database Schema

The application uses PostgreSQL with the following main tables:
- `firms` - Law firm information
- `users` - User accounts
- `documents` - Uploaded source documents
- `letter_templates` - Firm-specific templates
- `generated_letters` - Generated demand letters
- `letter_source_documents` - Junction table linking letters to source documents

## Database Migrations

Alembic commands, autogenerate workflow, and scripts live in **[api/README.md](api/README.md)**.

## S3 Bucket Setup

The application uses AWS S3 for document storage. You need to create two S3 buckets before using the S3 client.

### Quick Setup

1. **Create S3 Buckets:**
   ```bash
   AWS_REGION="us-east-2"
   ENV="dev"
   
   # Documents bucket
   aws s3api create-bucket \
     --bucket goico-demand-letters-documents-${ENV} \
     --region ${AWS_REGION}
   
   # Exports bucket
   aws s3api create-bucket \
     --bucket goico-demand-letters-exports-${ENV} \
     --region ${AWS_REGION}
   ```

2. **Update Environment Variables:**
   Add to your `api/.env` file:
   ```env
   AWS_REGION=us-east-2
   AWS_S3_BUCKET_DOCUMENTS=goico-demand-letters-documents-dev
   AWS_S3_BUCKET_EXPORTS=goico-demand-letters-exports-dev
   ```

For detailed S3 bucket setup instructions, including bucket configuration (versioning, encryption), see [S3 Bucket Setup Guide](docs/s3-bucket-setup.md).

## Deployment

Run the API as a container or process: **[api/README.md](api/README.md)**, **`api/Dockerfile`**, and **`api/docker-compose.yml`**. Environment variables are documented in **`api/.env.example`**.

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

- Built with React, FastAPI, and Docker-backed local infrastructure
- Powered by OpenAI for AI-driven letter generation

