import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function ErrorMessage({ 
  error, 
  onRetry, 
  className,
  title = 'Error',
  showIcon = true 
}) {
  if (!error) return null;

  return (
    <div 
      className={cn(
        'flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive',
        className
      )}
    >
      {showIcon && <AlertCircle className="h-5 w-5 shrink-0" />}
      <div className="flex-1">
        {title && <p className="text-sm font-semibold mb-1">{title}</p>}
        <p className="text-sm">{error}</p>
      </div>
      {onRetry && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onRetry}
          className="ml-auto shrink-0"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      )}
    </div>
  );
}

