import React from 'react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { NotificationDropdown } from '@/components/notifications/NotificationDropdown';
import { LogOut, User } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export const Header = () => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-background border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-semibold text-foreground">
          Tableau de bord
        </h1>
      </div>

      <div className="flex items-center space-x-4">
        <NotificationDropdown />
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                <User className="w-4 h-4" />
              </div>
              <span className="hidden md:block">{user?.full_name || user?.username}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={logout} className="text-destructive">
              <LogOut className="w-4 h-4 mr-2" />
              Déconnexion
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};