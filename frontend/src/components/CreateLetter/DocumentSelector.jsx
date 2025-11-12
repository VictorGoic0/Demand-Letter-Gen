import { useState } from 'react';
import { Search, File, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useDocuments } from '@/hooks/useDocuments';
import { cn } from '@/lib/utils';

export function DocumentSelector({ selectedDocuments, onSelectionChange }) {
  const [searchQuery, setSearchQuery] = useState('');
  const { documents, loading } = useDocuments();

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

  const filteredDocuments = documents.filter((doc) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return doc.filename.toLowerCase().includes(query);
  });

  const handleToggleDocument = (documentId) => {
    if (selectedDocuments.includes(documentId)) {
      onSelectionChange(selectedDocuments.filter(id => id !== documentId));
    } else {
      if (selectedDocuments.length < 5) {
        onSelectionChange([...selectedDocuments, documentId]);
      }
    }
  };

  const handleClearSelection = () => {
    onSelectionChange([]);
  };

  const isMaxSelected = selectedDocuments.length >= 5;
  const selectedCount = selectedDocuments.length;

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-10 bg-muted animate-pulse rounded" />
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center border border-dashed rounded-lg">
        <div className="rounded-full bg-muted p-4 mb-4">
          <File className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold mb-2">No documents available</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Upload documents first to generate a demand letter.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Selection Info */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-muted-foreground">
            {selectedCount} of 5 selected
            {isMaxSelected && (
              <span className="ml-2 text-destructive font-medium">(Maximum reached)</span>
            )}
          </div>
          {selectedCount > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearSelection}
            >
              <X className="h-4 w-4 mr-2" />
              Clear Selection
            </Button>
          )}
        </div>
      </div>

      {/* Documents Table */}
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">
                <Checkbox
                  checked={filteredDocuments.length > 0 && filteredDocuments.every(doc => selectedDocuments.includes(doc.id))}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      const newSelection = [...selectedDocuments];
                      filteredDocuments.forEach(doc => {
                        if (!newSelection.includes(doc.id) && newSelection.length < 5) {
                          newSelection.push(doc.id);
                        }
                      });
                      onSelectionChange(newSelection);
                    } else {
                      onSelectionChange(selectedDocuments.filter(id => 
                        !filteredDocuments.some(doc => doc.id === id)
                      ));
                    }
                  }}
                  disabled={isMaxSelected && filteredDocuments.some(doc => !selectedDocuments.includes(doc.id))}
                />
              </TableHead>
              <TableHead>Filename</TableHead>
              <TableHead>Upload Date</TableHead>
              <TableHead>File Size</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredDocuments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                  No documents found matching "{searchQuery}"
                </TableCell>
              </TableRow>
            ) : (
              filteredDocuments.map((document) => {
                const isSelected = selectedDocuments.includes(document.id);
                const isDisabled = !isSelected && isMaxSelected;
                
                return (
                  <TableRow
                    key={document.id}
                    className={cn(
                      'cursor-pointer hover:bg-muted/50',
                      isSelected && 'bg-muted/30'
                    )}
                    onClick={() => !isDisabled && handleToggleDocument(document.id)}
                  >
                    <TableCell>
                      <Checkbox
                        checked={isSelected}
                        onCheckedChange={() => !isDisabled && handleToggleDocument(document.id)}
                        disabled={isDisabled}
                      />
                    </TableCell>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <File className="h-4 w-4 text-muted-foreground" />
                        <span className="truncate max-w-xs">{document.filename}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDate(document.uploaded_at)}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatFileSize(document.file_size)}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Max Selection Message */}
      {isMaxSelected && (
        <p className="text-sm text-muted-foreground">
          Maximum 5 documents selected. Deselect a document to select another.
        </p>
      )}
    </div>
  );
}

