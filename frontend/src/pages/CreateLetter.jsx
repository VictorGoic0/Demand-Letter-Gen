import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { DocumentSelector } from '@/components/CreateLetter/DocumentSelector';
import { TemplateSelector } from '@/components/CreateLetter/TemplateSelector';
import { GenerationProgress } from '@/components/CreateLetter/GenerationProgress';
import { useGenerateLetter } from '@/hooks/useLetterGeneration';

export function CreateLetter() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [templateId, setTemplateId] = useState(null);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [errors, setErrors] = useState({});
  
  const { generateLetter, generating, error, setError } = useGenerateLetter();

  const validate = () => {
    const newErrors = {};

    if (!templateId) {
      newErrors.template = 'Template is required';
    }

    if (selectedDocuments.length === 0) {
      newErrors.documents = 'At least one document is required';
    } else if (selectedDocuments.length > 5) {
      newErrors.documents = 'Maximum 5 documents allowed';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleGenerate = async () => {
    // Clear previous errors
    setErrors({});
    setError(null);

    if (!validate()) {
      return;
    }

    try {
      const result = await generateLetter(
        templateId,
        selectedDocuments,
        title.trim() || null
      );
      
      // Redirect to finalize page
      navigate(`/letters/${result.letter_id}/finalize`);
    } catch (err) {
      // Error is already set in the hook
      console.error('Failed to generate letter:', err);
    }
  };

  const handleRetry = () => {
    setError(null);
    handleGenerate();
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Create Letter</h1>
        <p className="text-muted-foreground">
          Generate a new demand letter from a template and documents
        </p>
      </div>

      {/* Error Banner */}
      <ErrorMessage error={error} onRetry={handleRetry} />

      {/* Generation Progress */}
      {generating && (
        <Card>
          <CardContent className="p-8">
            <GenerationProgress />
          </CardContent>
        </Card>
      )}

      {/* Form (hidden during generation) */}
      {!generating && (
        <div className="space-y-8">
          {/* Optional Title */}
          <div className="space-y-2">
            <Label htmlFor="letter-title">Letter Title (Optional)</Label>
            <Input
              id="letter-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Demand Letter - Case #2024-001"
              maxLength={255}
            />
            <p className="text-sm text-muted-foreground">
              Leave blank to use a default title
            </p>
          </div>

          {/* Template Selection */}
          <div className="bg-card border rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Select Template</h2>
            <TemplateSelector
              selectedTemplateId={templateId}
              onTemplateChange={setTemplateId}
              error={errors.template}
            />
          </div>

          {/* Document Selection */}
          <div className="bg-card border rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Select Documents</h2>
            {errors.documents && (
              <p className="text-sm text-destructive mb-4">{errors.documents}</p>
            )}
            <DocumentSelector
              selectedDocuments={selectedDocuments}
              onSelectionChange={setSelectedDocuments}
            />
          </div>

          {/* Generate Button */}
          <div className="flex justify-end">
            <Button
              onClick={handleGenerate}
              disabled={generating || !templateId || selectedDocuments.length === 0}
              size="lg"
            >
              Generate Letter
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
