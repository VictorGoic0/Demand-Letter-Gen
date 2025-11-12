import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Edit, Save, FileDown, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
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
import { useLetter, useUpdateLetter, useFinalizeLetter } from '@/hooks/useLetterFinalize';

export function FinalizeLetter() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { letter, loading, error, refetch } = useLetter(id);
  const { updateLetter, updating, error: updateError, setError: setUpdateError } = useUpdateLetter();
  const { finalizeLetter, finalizing, error: finalizeError, setError: setFinalizeError } = useFinalizeLetter();

  const [isEditMode, setIsEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const [showFinalizeDialog, setShowFinalizeDialog] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);

  // Letter is fetched automatically by useLetter hook

  useEffect(() => {
    if (letter) {
      setEditedContent(letter.content || '');
      
      // If letter is already finalized, show message
      if (letter.status === 'created') {
        // Stay on page with message (handled in render)
      }
    }
  }, [letter]);

  const handleEdit = () => {
    setIsEditMode(true);
    setEditedContent(letter?.content || '');
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    setEditedContent(letter?.content || '');
    setUpdateError(null);
  };

  const handleSave = async () => {
    if (!letter) return;

    setUpdateError(null);

    try {
      const updatedLetter = await updateLetter(letter.id, null, editedContent);
      setIsEditMode(false);
      // Refetch to get latest data
      await refetch();
    } catch (err) {
      // Error is already set in hook
      console.error('Failed to save letter:', err);
    }
  };

  const handleFinalizeClick = () => {
    setShowFinalizeDialog(true);
  };

  const handleFinalizeConfirm = async () => {
    if (!letter) return;

    setShowFinalizeDialog(false);
    setFinalizeError(null);

    try {
      const result = await finalizeLetter(letter.id);
      setDownloadUrl(result.download_url);
      setShowSuccessDialog(true);
    } catch (err) {
      // Error is already set in hook
      console.error('Failed to finalize letter:', err);
    }
  };

  const handleSuccessConfirm = () => {
    setShowSuccessDialog(false);
    navigate('/letters');
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
        <p className="text-muted-foreground">Letter not found</p>
        <Button onClick={() => navigate('/letters')} className="mt-4">
          Back to Letters
        </Button>
      </div>
    );
  }

  const isFinalized = letter.status === 'created';

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">{letter.title}</h1>
          <p className="text-muted-foreground">
            {isFinalized ? 'This letter has been finalized' : 'Review and finalize your letter'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {!isEditMode ? (
            <>
              <Button
                variant="outline"
                onClick={handleEdit}
                disabled={updating || finalizing}
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
                disabled={updating || finalizing}
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

      {/* Already Finalized Message */}
      {isFinalized && !isEditMode && (
        <Card className="bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-blue-900 dark:text-blue-100">
              <CheckCircle2 className="h-5 w-5 shrink-0" />
              <p className="text-sm font-medium">
                This letter has already been finalized. You can still edit and re-export it.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Banner */}
      {(updateError || finalizeError) && (
        <Card className="bg-destructive/10 border-destructive/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <p className="text-sm font-medium">{updateError || finalizeError}</p>
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

      {/* Finalize Button */}
      {!isEditMode && (
        <div className="flex justify-end">
          <Button
            onClick={handleFinalizeClick}
            disabled={updating || finalizing}
            size="lg"
          >
            {finalizing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Finalizing...
              </>
            ) : (
              <>
                <FileDown className="h-4 w-4 mr-2" />
                Finalize
              </>
            )}
          </Button>
        </div>
      )}

      {/* Finalize Confirmation Dialog */}
      <Dialog open={showFinalizeDialog} onOpenChange={setShowFinalizeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Finalize Letter</DialogTitle>
            <DialogDescription>
              This will generate a .docx file and mark the letter as finalized. You can still edit it later.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowFinalizeDialog(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleFinalizeConfirm}>
              Finalize
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
              Letter Finalized Successfully
            </DialogTitle>
            <DialogDescription>
              Your letter has been finalized and the .docx file has been generated.
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
            <Button onClick={handleSuccessConfirm} className="w-full">
              OK
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
