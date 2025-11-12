import { useState } from 'react';
import { Plus, RefreshCw, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { LetterList } from '@/components/Letters/LetterList';
import { useLetters, useDeleteLetter, useExportLetter } from '@/hooks/useLetters';

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
  const { exportLetter } = useExportLetter();

  const handleCreateClick = () => {
    navigate('/letters/new');
  };

  const handleViewClick = (letter) => {
    navigate(`/letters/${letter.id}/view`);
  };

  const handleEditClick = (letter) => {
    navigate(`/letters/${letter.id}/edit`);
  };

  const handleDownloadClick = async (letter) => {
    try {
      // If letter has docx_url, use it directly
      if (letter.docx_url) {
        const link = document.createElement('a');
        link.href = letter.docx_url;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // Otherwise, call export endpoint with auto-download
        await exportLetter(letter.id, true);
      }
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
      {error && (
        <div className="flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <p className="text-sm">{error}</p>
          <Button
            variant="ghost"
            size="sm"
            onClick={refetch}
            className="ml-auto"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      )}

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

