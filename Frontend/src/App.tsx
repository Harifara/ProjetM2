import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

// Pages principales
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import AuditLogs from "./pages/AuditLogs";
import NotFound from "./pages/NotFound";
import DashboardLayout from "./components/layout/DashboardLayout";

// Pages RH
import Districts from "./pages/rh/Districts";
import Communes from "./pages/rh/Communes";
import Fokontanys from "./pages/rh/Fokontanys";

const queryClient = new QueryClient();

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return user ? <>{children}</> : <Navigate to="/login" replace />;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* Auth */}
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* Routes protégées */}
            <Route
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              {/* Dashboard */}
              <Route path="/dashboard" element={<Dashboard />} />

              {/* Utilisateurs & Logs */}
              <Route path="/users" element={<Users />} />
              <Route path="/audit-logs" element={<AuditLogs />} />

              {/* Pages RH */}
              <Route path="/rh/districts" element={<Districts />} />
              <Route path="/rh/communes" element={<Communes />} />
              <Route path="/rh/fokontanys" element={<Fokontanys />} />
            </Route>

            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
