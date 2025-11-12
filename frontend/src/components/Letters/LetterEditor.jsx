import { useState, useEffect } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

export function LetterEditor({ content, onChange }) {
  const [localContent, setLocalContent] = useState(content || '');

  useEffect(() => {
    setLocalContent(content || '');
  }, [content]);

  const handleChange = (e) => {
    const newContent = e.target.value;
    setLocalContent(newContent);
    if (onChange) {
      onChange(newContent);
    }
  };

  // Count words and characters
  const wordCount = localContent.trim() ? localContent.trim().split(/\s+/).length : 0;
  const charCount = localContent.length;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label htmlFor="letter-editor">Letter Content</Label>
        <div className="text-sm text-muted-foreground">
          {wordCount} {wordCount === 1 ? 'word' : 'words'} • {charCount.toLocaleString()} {charCount === 1 ? 'character' : 'characters'}
        </div>
      </div>
      <Textarea
        id="letter-editor"
        value={localContent}
        onChange={handleChange}
        className="min-h-[600px] font-mono text-sm"
        placeholder="Enter letter content here..."
      />
      <p className="text-xs text-muted-foreground">
        HTML formatting will be preserved. Edit the raw HTML content directly.
      </p>
    </div>
  );
}

