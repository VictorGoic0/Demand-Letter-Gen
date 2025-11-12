// API Endpoints
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/login',
  
  // Documents
  DOCUMENTS: '/documents',
  DOCUMENT_BY_ID: (id: string) => `/documents/${id}`,
  DOCUMENT_UPLOAD: '/documents/upload',
  DOCUMENT_DELETE: (id: string) => `/documents/${id}`,
  
  // Templates
  TEMPLATES: '/templates',
  TEMPLATE_BY_ID: (id: string) => `/templates/${id}`,
  TEMPLATE_CREATE: '/templates',
  TEMPLATE_UPDATE: (id: string) => `/templates/${id}`,
  TEMPLATE_DELETE: (id: string) => `/templates/${id}`,
  
  // Parser
  PARSE_DOCUMENT: (id: string) => `/parse/${id}`,
  
  // AI Generation
  GENERATE_LETTER: '/generate/letter',
  
  // Letters
  LETTERS: '/letters',
  LETTER_BY_ID: (id: string) => `/letters/${id}`,
  LETTER_UPDATE: (id: string) => `/letters/${id}`,
  LETTER_DELETE: (id: string) => `/letters/${id}`,
  LETTER_FINALIZE: (id: string) => `/letters/${id}/finalize`,
  LETTER_EXPORT: (id: string) => `/letters/${id}/export`,
  
  // Health
  HEALTH: '/health',
} as const;

// File Constraints
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const MAX_DOCUMENTS_PER_LETTER = 5;

export const SUPPORTED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
] as const;

export const SUPPORTED_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt'] as const;

