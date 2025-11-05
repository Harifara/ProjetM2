import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useAuth } from '@/contexts/AuthContext';

const DashboardLayout = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className="pl-64">
        <Header />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;