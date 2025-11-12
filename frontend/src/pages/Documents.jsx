import { useState } from 'react';
import { File } from 'lucide-react';
import { DocumentUpload } from '@/components/Documents/DocumentUpload';
import { DocumentList } from '@/components/Documents/DocumentList';
import { useDocuments } from '@/hooks/useDocuments';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { EmptyState } from '@/components/ui/EmptyState';

export function Documents() {
  const [sortBy, setSortBy] = useState('uploaded_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const { documents, loading, error, refetch } = useDocuments(sortBy, sortOrder);

  const handleSort = (field, order) => {
    setSortBy(field);
    setSortOrder(order);
  };

  const handleUploadSuccess = () => {
    refetch();
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Document Library</h1>
        <p className="text-muted-foreground">
          Upload and manage your documents for demand letter generation
        </p>
      </div>

      {/* Upload Section - Always Visible */}
      <div className="bg-card border rounded-xl p-8 shadow-sm">
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-1">Upload Documents</h2>
          <p className="text-sm text-muted-foreground">
            Drag and drop PDF files or click to browse. Maximum file size is 50MB.
          </p>
        </div>
        <DocumentUpload onUploadSuccess={handleUploadSuccess} />
      </div>

      {/* Error State */}
      <ErrorMessage error={error} onRetry={refetch} />

      {/* Document List */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Your Documents</h2>
        <DocumentList
          documents={documents}
          loading={loading}
          onRefresh={refetch}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSort={handleSort}
        />
      </div>
    </div>
  );
}
