import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Star, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useTemplate } from '@/hooks/useTemplates';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { PageLoader } from '@/components/ui/PageLoader';

export function TemplateView() {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const { template, loading, error } = useTemplate(templateId);

  if (loading) {
    return <PageLoader message="Loading template..." />;
  }

  if (error || !template) {
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
          onClick={() => navigate('/templates')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Templates
        </Button>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{template.name}</h1>
              {template.is_default && (
                <Badge variant="default">
                  <Star className="h-3 w-3 mr-1" />
                  Default
                </Badge>
              )}
            </div>
            <p className="text-muted-foreground">
              View template details and structure
            </p>
          </div>
        </div>
      </div>

      {/* Template Content */}
      <div className="bg-card border rounded-xl p-8 shadow-sm max-w-4xl space-y-8">
        {/* Template Name */}
        <div className="space-y-2">
          <Label className="text-base font-semibold">Template Name</Label>
          <p className="text-lg">{template.name}</p>
        </div>

        {/* Letterhead Text */}
        {template.letterhead_text && (
          <div className="space-y-2">
            <Label className="text-base font-semibold">Letterhead Text</Label>
            <div className="whitespace-pre-wrap text-sm bg-muted/50 p-4 rounded-lg border">
              {template.letterhead_text}
            </div>
          </div>
        )}

        {/* Opening Paragraph */}
        {template.opening_paragraph && (
          <div className="space-y-2">
            <Label className="text-base font-semibold">Opening Paragraph</Label>
            <div className="whitespace-pre-wrap text-sm bg-muted/50 p-4 rounded-lg border">
              {template.opening_paragraph}
            </div>
          </div>
        )}

        {/* Sections */}
        {template.sections && template.sections.length > 0 && (
          <div className="space-y-2">
            <Label className="text-base font-semibold">
              Sections ({template.sections.length})
            </Label>
            <div className="space-y-2">
              {template.sections.map((section, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 p-3 border rounded-lg bg-muted/50"
                >
                  <span className="text-sm font-medium text-muted-foreground w-8">
                    {index + 1}.
                  </span>
                  <span className="text-sm flex-1">{section}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Closing Paragraph */}
        {template.closing_paragraph && (
          <div className="space-y-2">
            <Label className="text-base font-semibold">Closing Paragraph</Label>
            <div className="whitespace-pre-wrap text-sm bg-muted/50 p-4 rounded-lg border">
              {template.closing_paragraph}
            </div>
          </div>
        )}

        {/* Set as Default */}
        <div className="flex items-center space-x-2 pt-4 border-t">
          <CheckCircle2 className={`h-5 w-5 ${template.is_default ? 'text-primary' : 'text-muted-foreground'}`} />
          <Label className="text-sm font-normal">
            {template.is_default ? 'This is the default template for your firm' : 'This is not the default template'}
          </Label>
        </div>
      </div>

      {/* Edit Button */}
      <div className="flex justify-end max-w-4xl">
        <Button onClick={() => navigate(`/templates/${templateId}/edit`)}>
          <Edit className="h-4 w-4 mr-2" />
          Edit Template
        </Button>
      </div>
    </div>
  );
}

