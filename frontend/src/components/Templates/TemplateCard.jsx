import { Eye, Edit, Trash2, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export function TemplateCard({ template, onView, onEdit, onDelete }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const sectionCount = template.sections?.length || 0;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold pr-2">{template.name}</CardTitle>
          {template.is_default && (
            <Badge variant="default" className="shrink-0">
              <Star className="h-3 w-3 mr-1" />
              Default
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="font-medium">Sections:</span>
            <span>{sectionCount}</span>
          </div>
        </div>
        <div className="text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="font-medium">Created:</span>
            <span>{formatDate(template.created_at)}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-end gap-2 pt-4 border-t">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onView(template)}
        >
          <Eye className="h-4 w-4 mr-2" />
          View
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onEdit(template)}
        >
          <Edit className="h-4 w-4 mr-2" />
          Edit
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onDelete(template)}
          className="text-destructive hover:text-destructive"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete
        </Button>
      </CardFooter>
    </Card>
  );
}

