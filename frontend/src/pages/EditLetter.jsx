import { useParams } from 'react-router-dom';

export function EditLetter() {
  const { id } = useParams();
  
  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Edit Letter</h1>
      <p className="text-muted-foreground mb-8">Edit your letter content</p>
      <p>Edit letter content for ID: {id} coming soon...</p>
    </div>
  );
}

