import { Download, Trash2, File } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useDocumentDelete, useDocumentDownload } from '@/hooks/useDocuments';
import { useState } from 'react';

export function DocumentCard({ document, onDelete }) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const { deleteDocument, deleting } = useDocumentDelete();
  const { downloadDocument, downloading } = useDocumentDownload();

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteDocument(document.id);
      setDeleteDialogOpen(false);
      if (onDelete) {
        onDelete(document.id);
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  const handleDownload = async () => {
    try {
      await downloadDocument(document.id);
    } catch (error) {
      console.error('Failed to download document:', error);
    }
  };

  return (
    <>
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <div className="flex items-start gap-4">
            <div className="rounded-lg bg-primary/10 p-3 shrink-0">
              <File className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1 min-w-0 space-y-2">
              <h3 className="font-semibold truncate" title={document.filename}>
                {document.filename}
              </h3>
              <div className="flex flex-col gap-1 text-sm text-muted-foreground">
                <span>{formatFileSize(document.file_size)}</span>
                <span>{formatDate(document.uploaded_at)}</span>
              </div>
            </div>
            <div className="flex flex-col gap-2 shrink-0">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleDownload}
                disabled={downloading}
                title="Download"
              >
                <Download className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleDeleteClick}
                disabled={deleting}
                title="Delete"
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{document.filename}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
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
    </>
  );
}

