import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function PageLoader({ message = 'Loading...', className }) {
  return (
    <div className={cn('min-h-screen flex items-center justify-center', className)}>
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}

