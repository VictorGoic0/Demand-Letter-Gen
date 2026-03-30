import { cn } from '@/lib/utils';

export function LoadingSkeleton({ className, variant = 'default' }) {
  const variants = {
    default: 'h-4 w-full',
    card: 'h-48 w-full',
    tableRow: 'h-16 w-full',
    text: 'h-4 w-3/4',
    circle: 'h-12 w-12 rounded-full',
    button: 'h-10 w-24',
  };

  return (
    <div
      className={cn(
        'bg-muted animate-pulse rounded',
        variants[variant] || variants.default,
        className
      )}
    />
  );
}

export function DocumentListSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <LoadingSkeleton key={i} variant="tableRow" />
      ))}
    </div>
  );
}

export function LetterCardSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div key={i} className="h-64 bg-muted animate-pulse rounded-lg" />
      ))}
    </div>
  );
}

export function TemplateCardSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-48 bg-muted animate-pulse rounded-lg" />
      ))}
    </div>
  );
}

