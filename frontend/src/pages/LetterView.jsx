import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, FileDown, Loader2, RefreshCw, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { PageLoader } from '@/components/ui/PageLoader';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { LetterViewer } from '@/components/Letters/LetterViewer';
import { useLetter } from '@/hooks/useLetterFinalize';
import { useExportLetter } from '@/hooks/useLetters';

export function LetterView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { letter, loading, error, refetch } = useLetter(id);
  const { exportLetter, exporting, error: exportError } = useExportLetter();

  const [showReExportDialog, setShowReExportDialog] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);

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
    }
  };

  const handleFinalize = () => {
    navigate(`/letters/${letter.id}/finalize`);
  };

  if (loading) {
    return <PageLoader message="Loading letter..." />;
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
        <ErrorMessage error={error} onRetry={refetch} />
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
      <div>
        <Button
          variant="ghost"
          onClick={() => navigate('/letters')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Letters
        </Button>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{letter.title}</h1>
              {letter.status === 'draft' && (
                <Badge variant="secondary">
                  Draft
                </Badge>
              )}
            </div>
            <p className="text-muted-foreground">
              {isFinalized ? 'View finalized letter' : 'View draft letter'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {hasDocx && (
              <Button
                variant="outline"
                onClick={handleDownload}
                disabled={exporting}
              >
                <FileDown className="h-4 w-4 mr-2" />
                Download
              </Button>
            )}
            {isFinalized && (
              <Button
                variant="outline"
                onClick={handleReExportClick}
                disabled={exporting}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Re-export
              </Button>
            )}
            {!isFinalized && (
              <Button
                variant="outline"
                onClick={handleFinalize}
                disabled={exporting}
              >
                <FileDown className="h-4 w-4 mr-2" />
                Finalize
              </Button>
            )}
            <Button
              onClick={() => navigate(`/letters/${letter.id}/edit`)}
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      <ErrorMessage error={exportError} />

      {/* Letter Content */}
      <Card>
        <CardContent className="p-6">
          <div className="max-h-[calc(100vh-400px)] overflow-y-auto">
            <LetterViewer content={letter.content} />
          </div>
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
    </div>
  );
}

