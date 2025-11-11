# Active Context: Demand Letter Generator

## Current Status

**Phase:** Project Initialization  
**Last Updated:** November 2025

The project is in the initial planning and setup phase. The PRD, architecture diagram, and detailed task lists have been created, but no code has been implemented yet.

## Current Work Focus

### Immediate Next Steps

1. **Project Setup (PR #1)**
   - Initialize frontend project with Vite + React
   - Initialize backend project structure
   - Configure dependencies and build tools
   - Set up folder structure

2. **Docker Configuration (PR #2)**
   - Create docker-compose.yml
   - Create Dockerfiles for frontend and backend
   - Set up local development environment

3. **Database Schema (PR #3)**
   - Set up SQLAlchemy models
   - Configure Alembic migrations
   - Create initial migration

4. **AWS Infrastructure Setup (PR #4)**
   - Configure S3 client utilities
   - Document IAM policies
   - Set up environment configuration

5. **Serverless Framework (PR #5)**
   - Create serverless.yml
   - Configure Lambda functions
   - Set up deployment scripts

## Recent Changes

- Memory bank initialized
- Project structure documented
- All task lists created (tasks-1.md through tasks-5.md)
- Architecture diagram created
- PRD finalized

## Active Decisions & Considerations

### Architecture Decisions Made

1. **Service Structure:** Service-oriented Lambda functions with shared code
2. **Local Development:** Single FastAPI app combining all routers
3. **Database:** PostgreSQL 15 with SQLAlchemy ORM
4. **Frontend:** React 18 + Vite + Tailwind + shadcn/ui
5. **Storage:** S3 for files, RDS for metadata

### Pending Decisions

1. **Node.js Version:** Need to confirm Node.js 18+ compatibility with all packages
2. **OpenAI Model:** Decide between GPT-4 and GPT-3.5-turbo (cost vs quality)
3. **Lambda Layer Strategy:** Finalize which dependencies go in common layer
4. **Testing Strategy:** Unit test coverage targets and testing frameworks
5. **CI/CD:** Whether to set up automated deployment pipeline

### Current Blockers

None identified yet - project is in initial setup phase.

## Next Milestones

### Phase 1: Foundation (Current)
- [ ] Project initialization
- [ ] Docker setup
- [ ] Database schema
- [ ] AWS infrastructure configuration
- [ ] Serverless framework setup

### Phase 2: Core Features
- [ ] Document service (upload, list, delete)
- [ ] Template service (CRUD)
- [ ] Parser service (PDF extraction)
- [ ] Basic UI for documents and templates

### Phase 3: AI Integration
- [ ] AI service (letter generation)
- [ ] OpenAI integration
- [ ] Finalize page UI

### Phase 4: Letter Management
- [ ] Letter service (CRUD, finalize, export)
- [ ] Generated letters library UI
- [ ] Edit functionality
- [ ] .docx export

### Phase 5: Polish & Testing
- [ ] End-to-end testing
- [ ] Bug fixes
- [ ] UI/UX refinements
- [ ] Performance optimization

### Phase 6: Deployment
- [ ] Lambda deployment
- [ ] Production environment setup
- [ ] User acceptance testing
- [ ] Launch

## Development Priorities

### P0 (Must Have)
All features listed in PRD Section 6 (Functional Requirements - P0)

### P1 (Post-MVP)
Features listed in PRD Section 6.7 (P1: Post-MVP Features)

## Key Files to Reference

- **PRD.md:** Complete product requirements
- **architecture.mermaid:** System architecture diagram
- **tasks-1.md:** Setup and infrastructure tasks (PRs #1-5)
- **tasks-2.md:** Backend services tasks (PRs #6-10)
- **tasks-3.md:** AI and letter services (PRs #11-14)
- **tasks-4.md:** Frontend pages (PRs #15-21)
- **tasks-5.md:** Integration, testing, deployment (PRs #22-29)

## Important Notes

1. **MVP Focus:** Only P0 features should be implemented initially
2. **Firm-Level Isolation:** All data must be filtered by firm_id
3. **Security First:** Authentication and authorization required for all endpoints
4. **Error Handling:** Comprehensive error handling at all layers
5. **Documentation:** Keep documentation updated as code is written

## Questions to Resolve

1. Authentication system details (JWT implementation specifics)
2. OpenAI API key management (AWS Secrets Manager vs environment variables)
3. Frontend deployment strategy (S3 + CloudFront vs Vercel/Netlify)
4. Database migration strategy (Alembic vs manual SQL)
5. Local S3 testing (LocalStack vs actual S3 bucket)

## Workflow Notes

- Use task lists (tasks-1.md through tasks-5.md) as implementation guide
- Each PR should be focused and complete
- Test locally before deployment
- Update documentation as features are built
- Keep memory bank updated with new patterns and decisions

