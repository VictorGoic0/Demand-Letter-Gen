# Project Brief: Demand Letter Generator

**Organization:** Steno  
**Project ID:** DLG_2025_001  
**Status:** MVP Development  
**Last Updated:** November 2025

## Project Overview

The Demand Letter Generator is an AI-driven solution designed to streamline the creation of demand letters for law firms. By leveraging OpenAI's models to automate the drafting of these documents, this tool aims to significantly reduce the time attorneys spend on this task, increasing efficiency and productivity.

## Core Purpose

Lawyers spend considerable time reviewing source documents (medical records, police reports, etc.) to draft demand letters, an essential step in litigation. This manual process is time-consuming and can delay the litigation process. The tool automates this by:

1. Allowing attorneys to upload source documents
2. Creating firm-specific letter templates
3. Using AI to generate draft demand letters from uploaded documents
4. Providing editing capabilities before finalization
5. Exporting finalized letters as .docx files

## Primary Goals

- **Efficiency:** Reduce attorney time spent on demand letter drafting by at least 50%
- **Automation:** Leverage AI to generate draft letters from source documents
- **Customization:** Provide firm-specific templates for consistency
- **Quality:** Maintain professional standards while accelerating production

## Success Metrics

- Reduction in time taken to draft demand letters by at least 50%
- At least 80% user adoption rate within the first year
- Positive user feedback on ease of use and document quality
- Generation of new sales leads through innovative AI solutions

## Target Users

**Primary:** Attorneys at law firms who need to create demand letters efficiently  
**Secondary:** Paralegals and legal assistants who support document preparation

## Scope (MVP - P0 Features Only)

### In Scope
- Document upload and management (PDFs)
- Firm-level template creation and management
- AI-powered letter generation from selected documents
- Letter editing and finalization
- .docx export functionality
- Generated letters library with edit/re-export capabilities

### Out of Scope (Post-MVP)
- Mobile applications
- Real-time collaboration
- OCR for scanned documents
- Advanced AI customization
- Integration with third-party legal software
- Analytics dashboards
- Multi-language support

## Technical Approach

**Architecture:** Service-oriented Lambda functions with shared dependencies  
**Frontend:** React 18 + Vite + Tailwind CSS + shadcn/ui  
**Backend:** Python 3.11 + FastAPI (Lambda deployment)  
**Infrastructure:** AWS (Lambda, S3, RDS PostgreSQL, API Gateway)  
**AI:** OpenAI API (GPT-4/3.5-turbo)

## Timeline

The project is organized into 6 phases:
1. Foundation (setup, infrastructure)
2. Core Features (documents, templates, parsing)
3. AI Integration (letter generation)
4. Letter Management (CRUD, export)
5. Polish & Testing
6. Deployment & Launch

## Key Constraints

- MVP focuses on P0 features only
- PDF documents only (no OCR in MVP)
- Maximum 5 documents per letter generation
- 50MB file size limit per document
- .docx export format only (no PDF export in MVP)
- Desktop-first design (mobile responsive but not primary)

## Success Criteria

- Zero critical bugs at launch
- < 5 minor bugs (non-blocking)
- 100% of P0 user stories completed
- Successful load testing with expected concurrent users
- Legal/compliance review passed

