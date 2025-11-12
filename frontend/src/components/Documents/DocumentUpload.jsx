import { useState, useRef, useCallback, useEffect } from 'react';
import { Upload, File, X, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useDocumentUpload } from '@/hooks/useDocuments';
import { MAX_FILE_SIZE } from '@/lib/constants';
import { cn } from '@/lib/utils';

export function DocumentUpload({ onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadQueue, setUploadQueue] = useState([]);
  const fileInputRef = useRef(null);
  const startedUploadsRef = useRef(new Set());
  const { uploadDocument } = useDocumentUpload();

  // Track upload state for each file
  const [uploadStates, setUploadStates] = useState({});

  const validateFile = (file) => {
    // Check file type
    if (file.type !== 'application/pdf') {
      return { valid: false, error: 'Only PDF files are allowed' };
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      const maxSizeMB = MAX_FILE_SIZE / (1024 * 1024);
      return { valid: false, error: `File size cannot exceed ${maxSizeMB}MB` };
    }

    return { valid: true };
  };

  const handleFiles = useCallback((files) => {
    const fileArray = Array.from(files);
    const validFiles = [];
    const errors = [];

    fileArray.forEach((file) => {
      const validation = validateFile(file);
      if (validation.valid) {
        validFiles.push(file);
      } else {
        errors.push({ filename: file.name, error: validation.error });
      }
    });

    // Add valid files to upload queue
    if (validFiles.length > 0) {
      const newUploads = validFiles.map((file) => ({
        id: `${Date.now()}-${Math.random()}`,
        file,
        status: 'pending', // pending, uploading, success, error
        progress: 0,
        error: null,
      }));

      setUploadQueue((prev) => [...prev, ...newUploads]);
    }

    // Show errors if any
    if (errors.length > 0) {
      errors.forEach(({ filename, error }) => {
        console.error(`${filename}: ${error}`);
      });
    }
  }, []);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleChange = useCallback((e) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
      // Reset input to allow selecting same file again
      e.target.value = '';
    }
  }, [handleFiles]);

  // Upload a single file
  const uploadSingleFile = useCallback(async (uploadItem) => {
    const { id, file } = uploadItem;

    // Update status to uploading
    setUploadStates((prev) => ({
      ...prev,
      [id]: { status: 'uploading', progress: 0, error: null },
    }));

    try {
      const result = await uploadDocument(
        file,
        (progress) => {
          // Update progress for this specific file
          setUploadStates((prev) => ({
            ...prev,
            [id]: { ...prev[id], progress },
          }));
        }
      );

      // Update status to success
      setUploadStates((prev) => ({
        ...prev,
        [id]: { status: 'success', progress: 100, error: null },
      }));

      // Remove from queue after a delay
      setTimeout(() => {
        setUploadQueue((prev) => prev.filter((item) => item.id !== id));
        setUploadStates((prev) => {
          const newState = { ...prev };
          delete newState[id];
          return newState;
        });
        startedUploadsRef.current.delete(id);
        if (onUploadSuccess) {
          onUploadSuccess(result);
        }
      }, 2000);

      return result;
    } catch (err) {
      // Update status to error
      setUploadStates((prev) => ({
        ...prev,
        [id]: {
          status: 'error',
          progress: 0,
          error: err.message || 'Failed to upload document',
        },
      }));
      throw err;
    }
  }, [uploadDocument, onUploadSuccess]);

  // Process upload queue - upload all files in parallel
  useEffect(() => {
    uploadQueue.forEach((item) => {
      // Only start upload if we haven't started it yet
      if (!startedUploadsRef.current.has(item.id)) {
        startedUploadsRef.current.add(item.id);
        
        // Initialize state
        setUploadStates((prev) => ({
          ...prev,
          [item.id]: { status: 'pending', progress: 0, error: null },
        }));

        // Start upload
        uploadSingleFile(item);
      }
    });
  }, [uploadQueue, uploadSingleFile]);

  const handleRemove = (id) => {
    setUploadQueue((prev) => prev.filter((item) => item.id !== id));
    setUploadStates((prev) => {
      const newState = { ...prev };
      delete newState[id];
      return newState;
    });
    startedUploadsRef.current.delete(id);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const hasActiveUploads = uploadQueue.length > 0;
  const isUploading = uploadQueue.some(
    (item) => uploadStates[item.id]?.status === 'uploading'
  );

  return (
    <div className="w-full space-y-6">
      {/* Drag and Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-16 transition-all duration-200 cursor-pointer',
          dragActive
            ? 'border-primary bg-primary/10 scale-[1.01] shadow-lg'
            : 'border-muted-foreground/30 hover:border-primary/50 hover:bg-primary/5',
          isUploading && 'pointer-events-none opacity-50'
        )}
        onClick={() => !isUploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          id="file-upload"
          className="hidden"
          accept=".pdf,application/pdf"
          onChange={handleChange}
          multiple
          disabled={isUploading}
        />

        {!hasActiveUploads ? (
          <div className="flex flex-col items-center justify-center text-center space-y-6">
            <div className="rounded-full bg-primary/10 p-6">
              <Upload className="h-12 w-12 text-primary" />
            </div>
            <div className="space-y-3">
              <h3 className="text-2xl font-semibold">
                Drag and drop your PDF files here
              </h3>
              <p className="text-base text-muted-foreground">
                or click anywhere in this area to browse
              </p>
            </div>
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              disabled={isUploading}
              className="mt-2"
            >
              Select Files
            </Button>
            <p className="text-sm text-muted-foreground mt-2">
              PDF files only, max {MAX_FILE_SIZE / (1024 * 1024)}MB each
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center space-y-4">
            <div className="rounded-full bg-primary/10 p-6">
              <Loader2 className="h-12 w-12 text-primary animate-spin" />
            </div>
            <div className="space-y-2">
              <h3 className="text-2xl font-semibold">Uploading...</h3>
              <p className="text-base text-muted-foreground">
                {uploadQueue.filter((item) => uploadStates[item.id]?.status === 'uploading').length} file(s) uploading
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Upload Progress Cards */}
      {hasActiveUploads && (
        <div className="space-y-3">
          {uploadQueue.map((item) => {
            const state = uploadStates[item.id] || { status: 'pending', progress: 0, error: null };
            const { status, progress, error } = state;

            return (
              <div
                key={item.id}
                className="flex items-center gap-4 w-full p-6 bg-muted/50 rounded-xl border"
              >
                <div className="rounded-full bg-primary/10 p-3 shrink-0">
                  {status === 'success' ? (
                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                  ) : status === 'error' ? (
                    <AlertCircle className="h-6 w-6 text-destructive" />
                  ) : status === 'uploading' ? (
                    <Loader2 className="h-6 w-6 text-primary animate-spin" />
                  ) : (
                    <File className="h-6 w-6 text-primary" />
                  )}
                </div>
                <div className="flex-1 min-w-0 space-y-2">
                  <p className="text-base font-semibold truncate">{item.file.name}</p>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">
                      {formatFileSize(item.file.size)}
                    </p>
                    {status === 'uploading' && (
                      <div className="w-full">
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all duration-300 ease-out"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {progress}%
                        </p>
                      </div>
                    )}
                    {status === 'success' && (
                      <p className="text-sm text-green-600">Upload successful!</p>
                    )}
                    {status === 'error' && (
                      <p className="text-sm text-destructive">{error}</p>
                    )}
                  </div>
                </div>
                {(status === 'error' || status === 'success') && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => handleRemove(item.id)}
                    className="shrink-0"
                  >
                    <X className="h-5 w-5" />
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
