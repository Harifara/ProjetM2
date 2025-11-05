import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import {
  Users,
  ScrollText,
  Briefcase,
  LayoutDashboard,
  LogOut,
  FileText
} from 'lucide-react';
import { Button } from "@/components/ui/button";

// Navigation principale avec rôle et lien
const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, roles: ['admin','responsable_rh','responsable_stock','responsable_finance','magasinier','coordinateur'] },
  { name: 'Utilisateurs', href: '/users', icon: Users, roles: ['admin'] },
  { name: "Logs d'audit", href: '/audit-logs', icon: ScrollText, roles: ['admin'] },

  // Pages RH
  { name: 'Districts', href: '/rh/districts', icon: Briefcase, roles: ['admin','responsable_rh'] },
  { name: 'Communes', href: '/rh/communes', icon: Briefcase, roles: ['admin','responsable_rh'] },
  { name: 'Fokontanies', href: '/rh/fokontanys', icon: Briefcase, roles: ['admin','responsable_rh'] },
];

export const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  // Filtrage de la navigation selon le rôle de l'utilisateur
  const filteredNavigation = navigation.filter(item => user?.role && item.roles.includes(user.role));

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-sidebar border-r border-sidebar-border">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center justify-center h-16 px-4 border-b border-sidebar-border">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-primary flex items-center justify-center">
              <span className="text-white font-bold text-xl">E</span>
            </div>
            <span className="text-xl font-bold text-sidebar-foreground">E.C.A.R.T</span>
          </div>
        </div>

        {/* Menu de navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {filteredNavigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
                )}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Profil utilisateur + Déconnexion */}
        <div className="p-4 border-t border-sidebar-border space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-sidebar-accent rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-sidebar-accent-foreground">
                {user?.full_name?.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase() || user?.username?.[0]?.toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-sidebar-foreground truncate">{user?.full_name || user?.username}</p>
              <p className="text-xs text-sidebar-foreground/60 capitalize">{user?.role?.replace('_',' ')}</p>
            </div>
          </div>
          <Button variant="outline" size="sm" className="w-full" onClick={logout}>
            <LogOut className="w-4 h-4 mr-2" /> Déconnexion
          </Button>
        </div>
      </div>
    </div>
  );
};
