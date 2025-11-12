import { useState } from 'react';
import { Search, ArrowUpDown, ArrowUp, ArrowDown, FileText } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { LetterCardSkeleton } from '@/components/ui/LoadingSkeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { LetterCard } from './LetterCard';
import { cn } from '@/lib/utils';

export function LetterList({ 
  letters, 
  loading, 
  onView,
  onEdit, 
  onDownload, 
  onDelete,
  sortBy,
  sortOrder,
  onSort,
  statusFilter,
  onStatusFilterChange,
  searchQuery,
  onSearchChange
}) {
  const SortIcon = ({ field }) => {
    if (sortBy !== field) {
      return <ArrowUpDown className="h-4 w-4 ml-1 opacity-50" />;
    }
    return sortOrder === 'asc' ? (
      <ArrowUp className="h-4 w-4 ml-1" />
    ) : (
      <ArrowDown className="h-4 w-4 ml-1" />
    );
  };

  const handleSort = (field) => {
    if (onSort) {
      const newOrder = sortBy === field && sortOrder === 'asc' ? 'desc' : 'asc';
      onSort(field, newOrder);
    }
  };

  if (loading) {
    return <LetterCardSkeleton />;
  }

  if (letters.length === 0) {
    return (
      <EmptyState
        icon={FileText}
        title="No letters yet"
        description={
          searchQuery || statusFilter !== 'all' 
            ? 'No letters match your filters. Try adjusting your search or filters.'
            : 'Create your first demand letter to get started.'
        }
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search letters by title or template..."
            value={searchQuery || ''}
            onChange={(e) => onSearchChange?.(e.target.value)}
            className="pl-10"
          />
        </div>
        
        {/* Status Filter */}
        <Select value={statusFilter || 'all'} onValueChange={onStatusFilterChange}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="created">Created</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Sort Controls */}
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="text-muted-foreground">Sort by:</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleSort('created_at')}
          className="h-8"
        >
          Date Created
          <SortIcon field="created_at" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleSort('updated_at')}
          className="h-8"
        >
          Date Modified
          <SortIcon field="updated_at" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleSort('title')}
          className="h-8"
        >
          Title
          <SortIcon field="title" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleSort('status')}
          className="h-8"
        >
          Status
          <SortIcon field="status" />
        </Button>
      </div>

      {/* Letter Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {letters.map((letter) => (
          <LetterCard
            key={letter.id}
            letter={letter}
            onView={onView}
            onEdit={onEdit}
            onDownload={onDownload}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
}

