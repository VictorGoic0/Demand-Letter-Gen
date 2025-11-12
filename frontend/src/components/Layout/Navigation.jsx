import { Link, useLocation } from 'react-router-dom';
import { FileText, LayoutTemplate, Mail, Upload } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: FileText,
  },
  {
    name: 'My Letters',
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
    href: '/upload-assets',
    icon: Upload,
  },
];

export function Navigation() {
  const location = useLocation();

  return (
    <nav className="flex items-center gap-6">
      {navigationItems.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.href;
        
        return (
          <Link
            key={item.name}
            to={item.href}
            className={cn(
              'px-4 py-2 text-sm font-medium transition-colors relative',
              isActive
                ? 'text-foreground'
                : 'text-foreground/70 hover:text-foreground'
            )}
          >
            {item.name}
            {isActive && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-foreground" />
            )}
          </Link>
        );
      })}
    </nav>
  );
}
