import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Edit, Save, FileDown, Loader2, AlertCircle, ArrowLeft, CheckCircle2, RefreshCw } from 'lucide-react';
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
import { LetterViewer } from '@/components/Letters/LetterViewer';
import { LetterEditor } from '@/components/Letters/LetterEditor';
import { useLetter, useUpdateLetter } from '@/hooks/useLetterFinalize';
import { useExportLetter } from '@/hooks/useLetters';

export function EditLetter() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { letter, loading, error, refetch } = useLetter(id);
  const { updateLetter, updating, error: updateError, setError: setUpdateError } = useUpdateLetter();
  const { exportLetter, exporting, error: exportError } = useExportLetter();

  const [isEditMode, setIsEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [showReExportDialog, setShowReExportDialog] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [pendingNavigation, setPendingNavigation] = useState(null);
  const navigateRef = useRef(navigate);

  // Track if there are unsaved changes
  const hasUnsavedChanges = isEditMode && editedContent !== originalContent;

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
      setDownloadUrl(letter.docx_url || null);
    }
  }, [letter]);

  const handleEdit = () => {
    setIsEditMode(true);
    setEditedContent(letter?.content || '');
    setOriginalContent(letter?.content || '');
    setUpdateError(null);
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    setEditedContent(originalContent);
    setUpdateError(null);
  };

  const handleSave = async () => {
    if (!letter) return;

    setUpdateError(null);

    try {
      await updateLetter(letter.id, null, editedContent);
      setOriginalContent(editedContent);
      setIsEditMode(false);
      await refetch();
    } catch (err) {
      console.error('Failed to save letter:', err);
    }
  };

  const handleReExportClick = () => {
    setShowReExportDialog(true);
  };

  const handleReExportConfirm = async () => {
    if (!letter) return;

    setShowReExportDialog(false);

    try {
      const url = await exportLetter(letter.id);
      setDownloadUrl(url);
      setShowSuccessDialog(true);
      await refetch(); // Refresh to get updated docx_url
    } catch (err) {
      console.error('Failed to re-export letter:', err);
      // Error is already set in the hook, will be displayed in the error banner
    }
  };

  const handleDownload = () => {
    if (letter?.docx_url) {
      const link = document.createElement('a');
      link.href = letter.docx_url;
      link.download = '';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleFinalize = () => {
    if (hasUnsavedChanges) {
      setPendingNavigation(() => () => navigate(`/letters/${letter.id}/finalize`));
      setShowUnsavedDialog(true);
    } else {
      navigate(`/letters/${letter.id}/finalize`);
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
        <Card className="bg-destructive/10 border-destructive/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          </CardContent>
        </Card>
        <Button onClick={() => refetch()}>Retry</Button>
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

  const isFinalized = letter.status === 'created';
  const hasDocx = !!letter.docx_url;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleBack}
            title="Back to Letters"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold mb-2">{letter.title}</h1>
            <p className="text-muted-foreground">
              {isFinalized ? 'Edit finalized letter' : 'Edit draft letter'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {!isEditMode ? (
            <>
              {hasDocx && (
                <Button
                  variant="outline"
                  onClick={handleDownload}
                  disabled={updating || exporting}
                >
                  <FileDown className="h-4 w-4 mr-2" />
                  Download
                </Button>
              )}
              {isFinalized && (
                <Button
                  variant="outline"
                  onClick={handleReExportClick}
                  disabled={updating || exporting}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Re-export
                </Button>
              )}
              {!isFinalized && (
                <Button
                  variant="outline"
                  onClick={handleFinalize}
                  disabled={updating || exporting}
                >
                  <FileDown className="h-4 w-4 mr-2" />
                  Finalize
                </Button>
              )}
              <Button
                variant="outline"
                onClick={handleEdit}
                disabled={updating || exporting}
              >
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                onClick={handleCancelEdit}
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
            </>
          )}
        </div>
      </div>

      {/* Error Banner */}
      {(updateError || exportError) && (
        <Card className="bg-destructive/10 border-destructive/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <p className="text-sm font-medium">{updateError || exportError}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Letter Content */}
      <Card>
        <CardContent className="p-6">
          {isEditMode ? (
            <LetterEditor
              content={editedContent}
              onChange={setEditedContent}
            />
          ) : (
            <div className="max-h-[calc(100vh-400px)] overflow-y-auto">
              <LetterViewer content={letter.content} />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Re-export Confirmation Dialog */}
      <Dialog open={showReExportDialog} onOpenChange={setShowReExportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Re-export Letter</DialogTitle>
            <DialogDescription>
              This will regenerate the .docx file with the current letter content. The existing file will be replaced.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowReExportDialog(false)}
              disabled={exporting}
            >
              Cancel
            </Button>
            <Button onClick={handleReExportConfirm} disabled={exporting}>
              {exporting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Exporting...
                </>
              ) : (
                'Re-export'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Success Dialog */}
      <Dialog open={showSuccessDialog} onOpenChange={setShowSuccessDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              Letter Re-exported Successfully
            </DialogTitle>
            <DialogDescription>
              Your letter has been re-exported and the .docx file has been updated.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {downloadUrl && (
              <div>
                <Button
                  asChild
                  className="w-full"
                  variant="outline"
                >
                  <a
                    href={downloadUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    download
                  >
                    <FileDown className="h-4 w-4 mr-2" />
                    Download .docx File
                  </a>
                </Button>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button onClick={() => setShowSuccessDialog(false)} className="w-full">
              OK
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
