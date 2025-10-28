import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

// Pages
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import RHEmployees from "./pages/rh/RHEmployees";
import RHContracts from "./pages/rh/RHContracts";
import RHLeaveRequests from "./pages/rh/RHLeaveRequests";
import RHAssignments from "./pages/rh/RHAssignments";
import RHPayments from "./pages/rh/RHPayments";
import RHPurchases from "./pages/rh/RHPurchases";
import Stock from "./pages/Stock";
import Users from "./pages/Users";
import AuditLogs from "./pages/AuditLogs";
import Finance from "./pages/Finance";
import Projects from "./pages/Projects";
import DashboardLayout from "./components/layout/DashboardLayout";
import NotFound from "./pages/NotFound";

// Nouvelles pages RH pour géographie
import RHDistricts from "./pages/rh/RHDistricts";
import RHCommunes from "./pages/rh/RHCommunes";
import RHFokontany from "./pages/rh/RHFokontany";

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
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
              {/* Dashboard */}
              <Route path="/dashboard" element={<Dashboard />} />

              {/* Utilisateurs & Logs */}
              <Route path="/users" element={<Users />} />
              <Route path="/audit-logs" element={<AuditLogs />} />

              {/* RH */}
              <Route path="/rh/employees" element={<RHEmployees />} />
              <Route path="/rh/contracts" element={<RHContracts />} />
              <Route path="/rh/leave-requests" element={<RHLeaveRequests />} />
              <Route path="/rh/assignments" element={<RHAssignments />} />
              <Route path="/rh/payments" element={<RHPayments />} />
              <Route path="/rh/purchases" element={<RHPurchases />} />

              {/* Géographie */}
              <Route path="/rh/districts" element={<RHDistricts />} />
              <Route path="/rh/communes" element={<RHCommunes />} />
              <Route path="/rh/fokontany" element={<RHFokontany />} />

              {/* Autres modules */}
              <Route path="/stock" element={<Stock />} />
              <Route path="/finance" element={<Finance />} />
              <Route path="/projects" element={<Projects />} />
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
