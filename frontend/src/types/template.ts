export interface Template {
  id: string;
  name: string;
  content: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  firm_id: string;
}

export interface TemplateCreate {
  name: string;
  content: string;
  description?: string;
}

export interface TemplateUpdate {
  name?: string;
  content?: string;
  description?: string;
  is_active?: boolean;
}

