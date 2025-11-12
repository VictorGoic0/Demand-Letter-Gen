import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { GripVertical, Plus, X, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export function TemplateForm({ template, onSubmit, onCancel, isSubmitting = false }) {
  const [name, setName] = useState('');
  const [letterheadText, setLetterheadText] = useState('');
  const [openingParagraph, setOpeningParagraph] = useState('');
  const [closingParagraph, setClosingParagraph] = useState('');
  const [sections, setSections] = useState([]);
  const [isDefault, setIsDefault] = useState(false);
  const [errors, setErrors] = useState({});
  const [draggedIndex, setDraggedIndex] = useState(null);

  const isEditMode = !!template;

  useEffect(() => {
    if (template) {
      setName(template.name || '');
      setLetterheadText(template.letterhead_text || '');
      setOpeningParagraph(template.opening_paragraph || '');
      setClosingParagraph(template.closing_paragraph || '');
      setSections(template.sections || []);
      setIsDefault(template.is_default || false);
    }
  }, [template]);

  const validate = () => {
    const newErrors = {};

    if (!name.trim()) {
      newErrors.name = 'Template name is required';
    } else if (name.trim().length > 255) {
      newErrors.name = 'Template name cannot exceed 255 characters';
    }

    // Validate sections
    sections.forEach((section, index) => {
      if (!section.trim()) {
        newErrors[`section-${index}`] = 'Section name cannot be empty';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    const formData = {
      name: name.trim(),
      letterhead_text: letterheadText.trim() || undefined,
      opening_paragraph: openingParagraph.trim() || undefined,
      closing_paragraph: closingParagraph.trim() || undefined,
      sections: sections.filter(s => s.trim()).length > 0 ? sections.filter(s => s.trim()) : undefined,
      is_default: isDefault,
    };

    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Failed to submit template:', error);
    }
  };

  const handleAddSection = () => {
    setSections([...sections, '']);
  };

  const handleRemoveSection = (index) => {
    const newSections = sections.filter((_, i) => i !== index);
    setSections(newSections);
    // Clear error for removed section
    const newErrors = { ...errors };
    delete newErrors[`section-${index}`];
    setErrors(newErrors);
  };

  const handleSectionChange = (index, value) => {
    const newSections = [...sections];
    newSections[index] = value;
    setSections(newSections);
    // Clear error when user starts typing
    if (errors[`section-${index}`]) {
      const newErrors = { ...errors };
      delete newErrors[`section-${index}`];
      setErrors(newErrors);
    }
  };

  // Drag and drop handlers
  const handleDragStart = (index) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, dropIndex) => {
    e.preventDefault();
    e.stopPropagation(); // Prevent parent handlers from firing
    
    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDraggedIndex(null);
      return;
    }

    const newSections = [...sections];
    const draggedSection = newSections[draggedIndex];
    newSections.splice(draggedIndex, 1);
    newSections.splice(dropIndex, 0, draggedSection);
    
    setSections(newSections);
    setDraggedIndex(null);
  };

  const handleDropAtStart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (draggedIndex === null || draggedIndex === 0) {
      setDraggedIndex(null);
      return;
    }

    const newSections = [...sections];
    const draggedSection = newSections[draggedIndex];
    newSections.splice(draggedIndex, 1);
    newSections.splice(0, 0, draggedSection);
    
    setSections(newSections);
    setDraggedIndex(null);
  };

  const handleDropAtEnd = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (draggedIndex === null || draggedIndex === sections.length - 1) {
      setDraggedIndex(null);
      return;
    }

    const newSections = [...sections];
    const draggedSection = newSections[draggedIndex];
    newSections.splice(draggedIndex, 1);
    newSections.push(draggedSection);
    
    setSections(newSections);
    setDraggedIndex(null);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Template Name */}
      <div className="space-y-2">
        <Label htmlFor="name">
          Template Name <span className="text-destructive">*</span>
        </Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            if (errors.name) {
              const newErrors = { ...errors };
              delete newErrors.name;
              setErrors(newErrors);
            }
          }}
          placeholder="e.g., Standard Demand Letter"
          className={cn(errors.name && 'border-destructive')}
        />
        {errors.name && (
          <p className="text-sm text-destructive flex items-center gap-1">
            <AlertCircle className="h-4 w-4" />
            {errors.name}
          </p>
        )}
      </div>

      {/* Letterhead Text */}
      <div className="space-y-2">
        <Label htmlFor="letterhead">Letterhead Text</Label>
        <Textarea
          id="letterhead"
          value={letterheadText}
          onChange={(e) => setLetterheadText(e.target.value)}
          placeholder="Law Firm Name&#10;Address&#10;Phone Number"
          rows={4}
        />
        <p className="text-sm text-muted-foreground">
          This text will appear at the top of generated letters.
        </p>
      </div>

      {/* Opening Paragraph */}
      <div 
        className="space-y-2"
        onDragOver={handleDragOver}
        onDrop={handleDropAtStart}
      >
        <Label htmlFor="opening">Opening Paragraph</Label>
        <Textarea
          id="opening"
          value={openingParagraph}
          onChange={(e) => setOpeningParagraph(e.target.value)}
          placeholder="Dear Sir/Madam,"
          rows={3}
        />
        <p className="text-sm text-muted-foreground">
          This text will appear at the beginning of the letter body.
        </p>
      </div>

      {/* Sections */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Label>Sections</Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleAddSection}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Section
          </Button>
        </div>
        
        {sections.length === 0 ? (
          <div className="text-sm text-muted-foreground p-4 border border-dashed rounded-lg text-center">
            No sections added. Click "Add Section" to create one.
          </div>
        ) : (
          <div className="space-y-2">
            {sections.map((section, index) => (
              <div
                key={index}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, index)}
                onDragEnd={handleDragEnd}
                className={cn(
                  'flex items-center gap-2 p-3 border rounded-lg bg-card',
                  draggedIndex === index && 'opacity-50',
                  draggedIndex !== null && draggedIndex !== index && 'border-primary'
                )}
              >
                <GripVertical className="h-5 w-5 text-muted-foreground cursor-move" />
                <Input
                  value={section}
                  onChange={(e) => handleSectionChange(index, e.target.value)}
                  placeholder={`Section ${index + 1} name`}
                  className={cn(
                    'flex-1',
                    errors[`section-${index}`] && 'border-destructive'
                  )}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => handleRemoveSection(index)}
                  className="shrink-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
            {Object.keys(errors).some(key => key.startsWith('section-')) && (
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                Please fill in all section names
              </p>
            )}
          </div>
        )}
        <p className="text-sm text-muted-foreground">
          Drag sections to reorder them. These will be used as headings in generated letters.
        </p>
      </div>

      {/* Closing Paragraph */}
      <div 
        className="space-y-2"
        onDragOver={handleDragOver}
        onDrop={handleDropAtEnd}
      >
        <Label htmlFor="closing">Closing Paragraph</Label>
        <Textarea
          id="closing"
          value={closingParagraph}
          onChange={(e) => setClosingParagraph(e.target.value)}
          placeholder="Sincerely,&#10;Attorney Name"
          rows={3}
        />
        <p className="text-sm text-muted-foreground">
          This text will appear at the end of the letter body.
        </p>
      </div>

      {/* Set as Default */}
      <div className="flex items-center space-x-2">
        <Checkbox
          id="is_default"
          checked={isDefault}
          onCheckedChange={(checked) => setIsDefault(checked === true)}
        />
        <Label
          htmlFor="is_default"
          className="text-sm font-normal cursor-pointer"
        >
          Set as default template for this firm
        </Label>
      </div>

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-4 pt-4 border-t">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : isEditMode ? 'Update Template' : 'Create Template'}
        </Button>
      </div>
    </form>
  );
}

