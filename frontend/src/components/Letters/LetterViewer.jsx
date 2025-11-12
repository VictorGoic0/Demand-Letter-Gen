import { useMemo } from 'react';
import DOMPurify from 'dompurify';

export function LetterViewer({ content }) {
  const sanitizedContent = useMemo(() => {
    if (!content) return '';
    
    // Remove markdown code fences if present (```html ... ```)
    let cleanedContent = content;
    cleanedContent = cleanedContent.replace(/```html\s*/g, '');
    cleanedContent = cleanedContent.replace(/```\s*/g, '');
    
    return DOMPurify.sanitize(cleanedContent, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'div', 'span'],
      ALLOWED_ATTR: ['class', 'style'],
    });
  }, [content]);

  if (!content) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No content available</p>
      </div>
    );
  }

  return (
    <>
      <style>{`
        .letter-content {
          line-height: 1.6;
          font-size: 14px;
        }
        .letter-content h1 {
          font-size: 2em;
          font-weight: bold;
          margin-top: 0.67em;
          margin-bottom: 0.67em;
        }
        .letter-content h2 {
          font-size: 1.5em;
          font-weight: bold;
          margin-top: 0.83em;
          margin-bottom: 0.83em;
        }
        .letter-content h3 {
          font-size: 1.17em;
          font-weight: bold;
          margin-top: 1em;
          margin-bottom: 1em;
        }
        .letter-content h4 {
          font-size: 1em;
          font-weight: bold;
          margin-top: 1.33em;
          margin-bottom: 1.33em;
        }
        .letter-content h5 {
          font-size: 0.83em;
          font-weight: bold;
          margin-top: 1.67em;
          margin-bottom: 1.67em;
        }
        .letter-content h6 {
          font-size: 0.67em;
          font-weight: bold;
          margin-top: 2.33em;
          margin-bottom: 2.33em;
        }
        .letter-content p {
          margin-top: 1em;
          margin-bottom: 1em;
        }
        .letter-content ul,
        .letter-content ol {
          margin-top: 1em;
          margin-bottom: 1em;
          padding-left: 2em;
        }
        .letter-content li {
          margin-top: 0.5em;
          margin-bottom: 0.5em;
        }
        .letter-content strong {
          font-weight: bold;
        }
        .letter-content em {
          font-style: italic;
        }
        .letter-content u {
          text-decoration: underline;
        }
        @media print {
          .letter-content {
            font-size: 12pt;
            line-height: 1.5;
            color: black;
          }
          .letter-content h1,
          .letter-content h2,
          .letter-content h3 {
            page-break-after: avoid;
          }
          .letter-content p {
            margin-bottom: 1em;
          }
        }
      `}</style>
      <div className="prose prose-sm max-w-none">
        <div
          className="letter-content"
          dangerouslySetInnerHTML={{ __html: sanitizedContent }}
        />
      </div>
    </>
  );
}

