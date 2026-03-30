import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Navigation } from './Navigation';
import { UserMenu } from './UserMenu';

export function MainLayout({ children }) {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Firm Name */}
            <div className="flex items-center gap-3">
              <Link to="/letters" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                <img 
                  src="/logo.svg" 
                  alt="Demand Letter Generator" 
                  className="w-8 h-8"
                />
                <span className="text-xl font-semibold text-foreground">Demand Letter Generator</span>
              </Link>
              {user?.firmName && (
                <span className="text-sm text-muted-foreground font-medium">
                  {user.firmName}
                </span>
              )}
            </div>

            {/* Navigation */}
            <Navigation />

            {/* User Menu */}
            <UserMenu />
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

