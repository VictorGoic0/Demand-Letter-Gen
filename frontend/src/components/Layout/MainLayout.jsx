import { useAuth } from '@/contexts/AuthContext';
import { Navigation } from './Navigation';
import { User } from 'lucide-react';

export function MainLayout({ children }) {
  const { user } = useAuth();
  const displayName = user 
    ? `${user.first_name} ${user.last_name}` 
    : 'User';

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <img 
                src="/logo.svg" 
                alt="Demand Letter Generator" 
                className="w-8 h-8"
              />
              <span className="text-xl font-semibold text-foreground">Demand Letter Generator</span>
            </div>

            {/* Navigation */}
            <Navigation />

            {/* User Profile */}
            <div className="flex items-center gap-2">
              <User className="w-5 h-5 text-foreground/70" />
              <span className="text-sm font-medium text-foreground">{displayName}</span>
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

