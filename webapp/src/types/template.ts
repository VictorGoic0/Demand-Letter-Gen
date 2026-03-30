export interface Template {
  id: string;
  firm_id: string;
  name: string;
  letterhead_text?: string;
  opening_paragraph?: string;
  closing_paragraph?: string;
  sections?: string[];
  is_default: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateCreate {
  name: string;
  letterhead_text?: string;
  opening_paragraph?: string;
  closing_paragraph?: string;
  sections?: string[];
  is_default?: boolean;
}

export interface TemplateUpdate {
  name?: string;
  letterhead_text?: string;
  opening_paragraph?: string;
  closing_paragraph?: string;
  sections?: string[];
  is_default?: boolean;
}

