import { Loader2 } from 'lucide-react';

export function GenerationProgress() {
  return (
    <div className="flex flex-col items-center justify-center py-12 space-y-4">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <p className="text-sm font-medium">Generating your demand letter...</p>
      <p className="text-xs text-muted-foreground">
        This may take up to 30 seconds
      </p>
    </div>
  );
}

