import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { TemplateForm } from '@/components/Templates/TemplateForm';
import { useTemplate, useUpdateTemplate, useCreateTemplate } from '@/hooks/useTemplates';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { PageLoader } from '@/components/ui/PageLoader';
import { useState, useEffect } from 'react';

export function TemplateEdit() {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const isNewTemplate = !templateId || templateId === 'new';
  const { template, loading, error, refetch } = useTemplate(isNewTemplate ? null : templateId);
  const { updateTemplate, updating } = useUpdateTemplate();
  const { createTemplate, creating } = useCreateTemplate();
  const [successMessage, setSuccessMessage] = useState(null);

  // Scroll to top when success message appears
  useEffect(() => {
    if (successMessage) {
      window.scrollTo({ top: 0 });
    }
  }, [successMessage]);

  const handleSubmit = async (data) => {
    try {
      if (isNewTemplate) {
        const newTemplate = await createTemplate(data);
        setSuccessMessage(`${newTemplate.name} created successfully!`);
        // Clear success message after 5 seconds
        setTimeout(() => setSuccessMessage(null), 5000);
        // Optionally navigate to view page
        // navigate(`/templates/${newTemplate.id}/view`);
      } else {
        const updatedTemplate = await updateTemplate(templateId, data);
        setSuccessMessage(`${updatedTemplate.name} edit successful!`);
        // Clear success message after 5 seconds
        setTimeout(() => setSuccessMessage(null), 5000);
        // Refetch to get updated data
        refetch();
      }
    } catch (error) {
      console.error('Failed to save template:', error);
      throw error; // Re-throw to let form handle error display
    }
  };

  const handleCancel = () => {
    navigate('/templates');
  };

  if (!isNewTemplate && loading) {
    return <PageLoader message="Loading template..." />;
  }

  if (!isNewTemplate && (error || !template)) {
    return (
      <div className="space-y-8">
        <Button
          variant="ghost"
          onClick={() => navigate('/templates')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Templates
        </Button>
        <ErrorMessage error={error || 'Template not found'} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <Button
          variant="ghost"
          onClick={handleCancel}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Templates
        </Button>
        <h1 className="text-3xl font-bold mb-2">
          {isNewTemplate ? 'Create Template' : 'Edit Template'}
        </h1>
        <p className="text-muted-foreground">
          {isNewTemplate
            ? 'Create a new letter template for your firm'
            : 'Update your template settings and structure'}
        </p>
      </div>

      {/* Success Banner */}
      {successMessage && (
        <Card className="bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
              <CheckCircle2 className="h-5 w-5 shrink-0" />
              <p className="text-sm font-medium">{successMessage}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Form */}
      <div className="bg-card border rounded-xl p-8 shadow-sm max-w-4xl">
        <TemplateForm
          template={template}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={creating || updating}
        />
      </div>
    </div>
  );
}

