import { useParams } from 'react-router-dom';

export function FinalizeLetter() {
  const { id } = useParams<{ id: string }>();
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Finalize Letter</h1>
      <p className="text-muted-foreground mb-8">Review and finalize your letter</p>
      <p>Finalize letter content for ID: {id} coming soon...</p>
    </div>
  );
}

