import { FileText } from 'lucide-react';
import { TemplateCard } from './TemplateCard';
import { TemplateCardSkeleton } from '@/components/ui/LoadingSkeleton';
import { EmptyState } from '@/components/ui/EmptyState';

export function TemplateList({ templates, loading, onView, onEdit, onDelete }) {
  if (loading) {
    return <TemplateCardSkeleton />;
  }

  if (templates.length === 0) {
    return (
      <EmptyState
        icon={FileText}
        title="No templates yet"
        description="Create your first template to get started with generating demand letters."
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {templates.map((template) => (
        <TemplateCard
          key={template.id}
          template={template}
          onView={onView}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

