export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  s3_key: string;
  upload_status: 'pending' | 'processing' | 'completed' | 'failed';
  extracted_text?: string;
  created_at: string;
  updated_at: string;
  firm_id: string;
}

export interface DocumentUploadResponse {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_status: string;
  created_at: string;
}

