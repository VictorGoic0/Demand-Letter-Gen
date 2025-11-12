import { useState } from 'react';
import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { TemplateList } from '@/components/Templates/TemplateList';
import { useTemplates, useDeleteTemplate } from '@/hooks/useTemplates';

export function Templates() {
  const navigate = useNavigate();
  const [sortBy] = useState(null);
  const [sortOrder] = useState('asc');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState(null);

  const { templates, loading, error, refetch } = useTemplates(sortBy, sortOrder);
  const { deleteTemplate, deleting } = useDeleteTemplate();

  const handleCreateClick = () => {
    navigate('/templates/new');
  };

  const handleViewClick = (template) => {
    navigate(`/templates/${template.id}/view`);
  };

  const handleEditClick = (template) => {
    navigate(`/templates/${template.id}/edit`);
  };

  const handleDeleteClick = (template) => {
    setTemplateToDelete(template);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!templateToDelete) return;

    try {
      await deleteTemplate(templateToDelete.id);
      setDeleteDialogOpen(false);
      setTemplateToDelete(null);
      refetch();
    } catch (error) {
      console.error('Failed to delete template:', error);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Template Management</h1>
          <p className="text-muted-foreground">
            Create and manage letter templates for your firm
          </p>
        </div>
        <Button onClick={handleCreateClick}>
          <Plus className="h-4 w-4 mr-2" />
          Create Template
        </Button>
      </div>

      {/* Error State */}
      <ErrorMessage error={error} onRetry={refetch} />

      {/* Template List */}
      <div>
        <TemplateList
          templates={templates}
          loading={loading}
          onView={handleViewClick}
          onEdit={handleEditClick}
          onDelete={handleDeleteClick}
        />
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Template</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{templateToDelete?.name}"? 
              {templateToDelete?.is_default && (
                <span className="block mt-2 text-destructive font-medium">
                  This is the default template. Deleting it will remove the default setting.
                </span>
              )}
              {templateToDelete && ' This action cannot be undone.'}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDeleteDialogOpen(false);
                setTemplateToDelete(null);
              }}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={deleting}
            >
              {deleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
