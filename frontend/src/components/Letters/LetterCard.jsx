import { Edit, Download, Trash2, FileText, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export function LetterCard({ letter, onView, onEdit, onDownload, onDelete }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const isFinalized = letter.status === 'created';
  const hasDocx = !!letter.docx_url;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold pr-2">{letter.title}</CardTitle>
          {letter.status === 'draft' && (
            <Badge variant="secondary" className="shrink-0">
              Draft
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {letter.template_name && (
          <div className="text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="font-medium">Template:</span>
              <span>{letter.template_name}</span>
            </div>
          </div>
        )}
        <div className="text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="font-medium">Created:</span>
            <span>{formatDate(letter.created_at)}</span>
          </div>
        </div>
        <div className="text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="font-medium">Modified:</span>
            <span>{formatDate(letter.updated_at)}</span>
          </div>
        </div>
        {letter.source_documents && letter.source_documents.length > 0 && (
          <div className="text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="font-medium">Documents:</span>
              <span>{letter.source_documents.length}</span>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex items-center justify-end gap-2 pt-4 border-t">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onView(letter)}
        >
          <Eye className="h-4 w-4 mr-2" />
          View
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onEdit(letter)}
        >
          <Edit className="h-4 w-4 mr-2" />
          Edit
        </Button>
        {hasDocx && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onDownload(letter)}
          >
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
        )}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onDelete(letter)}
          className="text-destructive hover:text-destructive"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete
        </Button>
      </CardFooter>
    </Card>
  );
}

