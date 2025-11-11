import { ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Navigation } from './Navigation';
import { Mail, User } from 'lucide-react';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const { user } = useAuth();
  const displayName = user 
    ? `${user.first_name} ${user.last_name}` 
    : 'User';

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 bg-foreground rounded">
                <Mail className="w-5 h-5 text-background" />
              </div>
              <span className="text-xl font-semibold">Demand Letter Generator</span>
            </div>

            {/* Navigation */}
            <Navigation />

            {/* User Profile */}
            <div className="flex items-center gap-2">
              <User className="w-5 h-5 text-foreground/70" />
              <span className="text-sm font-medium">{displayName}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  );
}

