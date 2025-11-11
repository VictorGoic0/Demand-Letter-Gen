export enum LetterStatus {
  DRAFT = 'draft',
  CREATED = 'created',
}

export interface Letter {
  id: string;
  title: string;
  content: string;
  status: LetterStatus;
  template_id: string;
  template_name: string;
  source_documents: Array<{
    id: string;
    filename: string;
    file_type: string;
  }>;
  docx_url?: string;
  created_at: string;
  updated_at: string;
}

export interface LetterCreate {
  template_id: string;
  document_ids: string[];
}

export interface LetterUpdate {
  title?: string;
  content?: string;
}

export interface LetterGenerateResponse {
  id: string;
  content: string;
  status: LetterStatus;
}

export interface LetterFinalizeResponse {
  id: string;
  status: LetterStatus;
  docx_url: string;
}

export interface LetterExportResponse {
  docx_url: string;
}

