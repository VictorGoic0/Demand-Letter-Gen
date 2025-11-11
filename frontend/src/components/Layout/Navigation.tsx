import { Link, useLocation } from 'react-router-dom';
import { FileText, LayoutTemplate, FileEdit, Mail, Upload } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/documents',
    icon: FileText,
  },
  {
    name: 'My Campaigns',
    href: '/letters',
    icon: Mail,
  },
  {
    name: 'Templates',
    href: '/templates',
    icon: LayoutTemplate,
  },
  {
    name: 'Upload Assets',
    href: '/documents',
    icon: Upload,
  },
];

export function Navigation() {
  const location = useLocation();

  return (
    <nav className="flex items-center gap-6">
      {navigationItems.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.href || 
                        (item.href === '/documents' && location.pathname.startsWith('/documents'));
        
        return (
          <Link
            key={item.name}
            to={item.href}
            className={cn(
              'px-4 py-2 rounded-md text-sm font-medium transition-colors',
              isActive
                ? 'bg-foreground text-background'
                : 'text-foreground/70 hover:text-foreground hover:bg-muted'
            )}
          >
            {item.name}
          </Link>
        );
      })}
    </nav>
  );
}

