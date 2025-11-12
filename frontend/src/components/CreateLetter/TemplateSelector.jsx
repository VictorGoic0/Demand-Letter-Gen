import { useState, useEffect } from 'react';
import { Star } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useTemplates, useDefaultTemplate } from '@/hooks/useTemplates';
import { Label } from '@/components/ui/label';

export function TemplateSelector({ selectedTemplateId, onTemplateChange, error }) {
  const { templates, loading } = useTemplates();
  const { template: defaultTemplate } = useDefaultTemplate();
  const [hasInitialized, setHasInitialized] = useState(false);

  // Pre-select default template on mount
  useEffect(() => {
    if (!hasInitialized && defaultTemplate && !selectedTemplateId) {
      onTemplateChange(defaultTemplate.id);
      setHasInitialized(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultTemplate, selectedTemplateId, hasInitialized]);

  if (loading) {
    return (
      <div className="space-y-2">
        <Label>Template</Label>
        <div className="h-10 bg-muted animate-pulse rounded-md" />
      </div>
    );
  }

  if (templates.length === 0) {
    return (
      <div className="space-y-2">
        <Label>Template</Label>
        <div className="p-4 border border-dashed rounded-lg text-center text-sm text-muted-foreground">
          No templates available. Create a template first to generate letters.
        </div>
      </div>
    );
  }

  const selectedTemplate = templates.find(t => t.id === selectedTemplateId);

  return (
    <div className="space-y-2">
      <Label htmlFor="template-select">
        Template <span className="text-destructive">*</span>
      </Label>
      <Select
        value={selectedTemplateId || ''}
        onValueChange={onTemplateChange}
      >
        <SelectTrigger id="template-select" className={error ? 'border-destructive' : ''}>
          <SelectValue placeholder="Select a template">
            {selectedTemplate && (
              <div className="flex items-center gap-2">
                <span>{selectedTemplate.name}</span>
                {selectedTemplate.is_default && (
                  <Star className="h-4 w-4 text-primary" />
                )}
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {templates.map((template) => (
            <SelectItem key={template.id} value={template.id}>
              <div className="flex items-center gap-2">
                <span>{template.name}</span>
                {template.is_default && (
                  <Star className="h-4 w-4 text-primary" />
                )}
                <span className="text-xs text-muted-foreground ml-2">
                  ({template.sections?.length || 0} sections)
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}
      {selectedTemplate && (
        <p className="text-sm text-muted-foreground">
          {selectedTemplate.sections?.length || 0} sections
          {selectedTemplate.is_default && ' • Default template'}
        </p>
      )}
    </div>
  );
}

