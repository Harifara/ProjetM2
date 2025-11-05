import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { 
  Users, 
  DollarSign, 
  FileText, 
  Calendar, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface DashboardStats {
  totalEmployees: number;
  totalExpenses: number;
  pendingLeaves: number;
  totalDocuments: number;
  recentActivities: Activity[];
  alerts: Alert[];
}

interface Activity {
  id: string;
  type: string;
  description: string;
  user: string;
  timestamp: string;
}

interface Alert {
  id: string;
  type: 'warning' | 'error' | 'info';
  title: string;
  message: string;
}

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Mock data for demo - replace with actual API calls
      const mockData: DashboardStats = {
        totalEmployees: 45,
        totalExpenses: 125000,
        pendingLeaves: 8,
        totalDocuments: 234,
        recentActivities: [
          {
            id: '1',
            type: 'leave_request',
            description: 'Demande de congé soumise',
            user: 'Marie Dupont',
            timestamp: new Date().toISOString(),
          },
          {
            id: '2',
            type: 'expense_approved',
            description: 'Note de frais approuvée',
            user: 'Jean Martin',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
          },
          {
            id: '3',
            type: 'contract_signed',
            description: 'Nouveau contrat signé',
            user: 'Sarah Johnson',
            timestamp: new Date(Date.now() - 7200000).toISOString(),
          },
        ],
        alerts: [
          {
            id: '1',
            type: 'warning',
            title: 'Budget dépassé',
            message: 'Le budget mensuel des dépenses est dépassé de 5%',
          },
          {
            id: '2',
            type: 'info',
            title: 'Mise à jour système',
            message: 'Une mise à jour système est programmée ce week-end',
          },
        ],
      };

      setTimeout(() => {
        setStats(mockData);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'leave_request':
        return <Calendar className="w-4 h-4 text-info" />;
      case 'expense_approved':
        return <CheckCircle className="w-4 h-4 text-success" />;
      case 'contract_signed':
        return <FileText className="w-4 h-4 text-primary" />;
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-destructive" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-info" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-foreground">
          Tableau de bord
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-20 bg-muted rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-foreground">
          Tableau de bord
        </h1>
        <Badge variant="secondary" className="text-sm">
          {user?.role === 'admin' ? 'Administrateur' : 'Employé'}
        </Badge>
      </div>

      {/* Stats Cards */}
      {user?.role === 'admin' && stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Employés</p>
                  <p className="text-2xl font-bold text-foreground">{stats.totalEmployees}</p>
                </div>
                <Users className="w-8 h-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Dépenses totales</p>
                  <p className="text-2xl font-bold text-foreground">
                    {stats.totalExpenses.toLocaleString('fr-FR')} €
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-success" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Congés en attente</p>
                  <p className="text-2xl font-bold text-foreground">{stats.pendingLeaves}</p>
                </div>
                <Calendar className="w-8 h-8 text-warning" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Documents</p>
                  <p className="text-2xl font-bold text-foreground">{stats.totalDocuments}</p>
                </div>
                <FileText className="w-8 h-8 text-info" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <Card>
          <CardHeader>
            <CardTitle>Activités récentes</CardTitle>
            <CardDescription>Les dernières actions dans le système</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-3">
                  {getActivityIcon(activity.type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground">
                      {activity.description}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {activity.user} • {new Date(activity.timestamp).toLocaleString('fr-FR')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Alerts */}
        <Card>
          <CardHeader>
            <CardTitle>Alertes</CardTitle>
            <CardDescription>Notifications importantes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.alerts.map((alert) => (
                <div key={alert.id} className="flex items-start space-x-3 p-3 rounded-lg bg-muted/50">
                  {getAlertIcon(alert.type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground">
                      {alert.title}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {alert.message}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;