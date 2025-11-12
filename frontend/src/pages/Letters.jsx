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
import { LetterList } from '@/components/Letters/LetterList';
import { useLetters, useDeleteLetter } from '@/hooks/useLetters';

export function Letters() {
  const navigate = useNavigate();
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [letterToDelete, setLetterToDelete] = useState(null);

  const { letters, loading, error, refetch } = useLetters(sortBy, sortOrder, statusFilter, searchQuery);
  const { deleteLetter, deleting } = useDeleteLetter();

  const handleCreateClick = () => {
    navigate('/letters/new');
  };

  const handleViewClick = (letter) => {
    navigate(`/letters/${letter.id}/view`);
  };

  const handleEditClick = (letter) => {
    navigate(`/letters/${letter.id}/edit`);
  };

  const handleDownloadClick = (letter) => {
    // Only download if docx_url exists (letter must be finalized)
    if (!letter.docx_url) {
      console.warn('No download URL available for letter:', letter.id);
      return;
    }
    
    try {
      const link = document.createElement('a');
      link.href = letter.docx_url;
      link.download = '';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Failed to download letter:', error);
    }
  };

  const handleDeleteClick = (letter) => {
    setLetterToDelete(letter);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!letterToDelete) return;

    try {
      await deleteLetter(letterToDelete.id);
      setDeleteDialogOpen(false);
      setLetterToDelete(null);
      refetch();
    } catch (error) {
      console.error('Failed to delete letter:', error);
    }
  };

  const handleSort = (field, order) => {
    setSortBy(field);
    setSortOrder(order);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Generated Letters</h1>
          <p className="text-muted-foreground">
            View and manage your generated demand letters
          </p>
        </div>
        <Button onClick={handleCreateClick}>
          <Plus className="h-4 w-4 mr-2" />
          Create New Letter
        </Button>
      </div>

      {/* Error State */}
      <ErrorMessage error={error} onRetry={refetch} />

      {/* Letter List */}
      <div>
        <LetterList
          letters={letters}
          loading={loading}
          onView={handleViewClick}
          onEdit={handleEditClick}
          onDownload={handleDownloadClick}
          onDelete={handleDeleteClick}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSort={handleSort}
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Letter</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{letterToDelete?.title}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDeleteDialogOpen(false);
                setLetterToDelete(null);
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

