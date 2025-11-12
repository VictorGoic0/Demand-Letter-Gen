import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Save, Loader2, AlertCircle, ArrowLeft } from 'lucide-react';
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
import { LetterEditor } from '@/components/Letters/LetterEditor';
import { useLetter, useUpdateLetter } from '@/hooks/useLetterFinalize';

export function EditLetter() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { letter, loading, error } = useLetter(id);
  const { updateLetter, updating, error: updateError, setError: setUpdateError } = useUpdateLetter();

  const [editedContent, setEditedContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);
  const [pendingNavigation, setPendingNavigation] = useState(null);
  const navigateRef = useRef(navigate);

  // Track if there are unsaved changes
  const hasUnsavedChanges = editedContent !== originalContent;

  // Update navigate ref
  useEffect(() => {
    navigateRef.current = navigate;
  }, [navigate]);

  // Handle browser navigation (closing tab/window)
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  // Initialize content when letter loads
  useEffect(() => {
    if (letter) {
      setEditedContent(letter.content || '');
      setOriginalContent(letter.content || '');
    }
  }, [letter]);

  const handleCancel = () => {
    if (hasUnsavedChanges) {
      setPendingNavigation(() => () => navigate(`/letters/${letter.id}/view`));
      setShowUnsavedDialog(true);
    } else {
      navigate(`/letters/${letter.id}/view`);
    }
  };

  const handleSave = async () => {
    if (!letter) return;

    setUpdateError(null);

    try {
      await updateLetter(letter.id, null, editedContent);
      setOriginalContent(editedContent);
      // Navigate to view page on success
      navigate(`/letters/${letter.id}/view`);
    } catch (err) {
      // Stay on edit page if save fails
      console.error('Failed to save letter:', err);
    }
  };




  const handleBack = () => {
    if (hasUnsavedChanges) {
      setPendingNavigation(() => () => navigate('/letters'));
      setShowUnsavedDialog(true);
    } else {
      navigate('/letters');
    }
  };

  const handleUnsavedConfirm = () => {
    setShowUnsavedDialog(false);
    if (pendingNavigation) {
      pendingNavigation();
      setPendingNavigation(null);
    }
  };

  const handleUnsavedCancel = () => {
    setShowUnsavedDialog(false);
    setPendingNavigation(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading letter...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Button
          variant="ghost"
          onClick={() => navigate('/letters')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Letters
        </Button>
        <Card className="bg-destructive/10 border-destructive/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!letter) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-4">Letter not found</p>
        <Button onClick={() => navigate('/letters')}>
          Back to Letters
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <Button
          variant="ghost"
          onClick={handleBack}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Letters
        </Button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{letter.title}</h1>
            <p className="text-muted-foreground">Edit letter</p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handleCancel}
              disabled={updating}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={updating}
            >
              {updating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {updateError && (
        <Card className="bg-destructive/10 border-destructive/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <p className="text-sm font-medium">{updateError}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Letter Content */}
      <Card>
        <CardContent className="p-6">
          <LetterEditor
            content={editedContent}
            onChange={setEditedContent}
          />
        </CardContent>
      </Card>

      {/* Unsaved Changes Warning Dialog */}
      <Dialog open={showUnsavedDialog} onOpenChange={setShowUnsavedDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Unsaved Changes</DialogTitle>
            <DialogDescription>
              You have unsaved changes. Are you sure you want to leave? Your changes will be lost.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleUnsavedCancel}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleUnsavedConfirm}
            >
              Leave Without Saving
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
